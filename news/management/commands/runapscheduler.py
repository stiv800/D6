import logging
import datetime
 
from django.conf import settings
 
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from news.models import *
 
 
logger = logging.getLogger(__name__)
 
 
def my_job():
    #  Your job processing logic here... 
    all_categories = set()

    past_date = datetime.datetime.today() - datetime.timedelta(days=7)
    
    posts_for_week = Post.objects.filter(dateCreation__date__gt=past_date)

    post_categories = {}
    user_sub_categories = {}

    for post in posts_for_week:
        post_categories[post.id] = set([c.category for c in post.postCategorys.all()])

    users = User.objects.all()

    for user in users:
        user_sub_categories[user.username] = set([s.postCategory.category for s in Subscriber.objects.filter(subscribersUser = user.id)])

    
    user_send_posts = {}
    
    for user in user_sub_categories.keys():
        user_new_posts = set()

        for post in post_categories.keys():
            a = user_sub_categories[user].intersection(post_categories[post])
            if a:
                user_new_posts.add(post)
        
        
        if user_new_posts:
            user_send_posts[user] = user_new_posts.copy()


    for user in user_send_posts.keys():
        send_posts = Post.objects.filter(id__in=list(user_send_posts[user]))
        print(f'user = {user}')

        html_content = render_to_string( 
        'mail_week.html',
        {
            'posts': send_posts,
        }
        )

        msg = EmailMultiAlternatives(
                    subject=f'Новости за последнюю неделю.',
                    from_email='stpab18@yandex.ru',
                    to=['stpab@mail.ru'],
                )
        msg.attach_alternative(html_content, "text/html") # добавляем html

        msg.send() # отсылаем

 
 
# функция которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
 
 
class Command(BaseCommand):
    help = "Runs apscheduler."
 
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),  # Тоже самое что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")
 
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )
 
        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")