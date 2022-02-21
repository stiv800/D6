from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from .models import *
 
 
@receiver(m2m_changed, sender=Post.postCategorys.through)
def notify_new_post(sender, instance, action, **kwargs):
    if action == "post_add":
        post_categories = [pc.category for pc in instance.postCategorys.all()]
        mailing_addresses = set()
        for cat in post_categories:
            mailing_addresses.update([sub.subscribersUser.email for sub in Subscriber.objects.filter(postCategory=Category.objects.get(category=cat))])

        print(mailing_addresses)


        for mail in list(mailing_addresses):

            html_content = render_to_string( 
                'mail_body.html',
                {
                    'instance': instance,
                }
            )

            if mail.find('mail.ru'):
                msg = EmailMultiAlternatives(
                            subject=f'{instance.title}',
                            body=instance.text[:50],
                            from_email='stpab18@yandex.ru',
                            to=[mail],
                        )
                msg.attach_alternative(html_content, "text/html") # добавляем html

                #msg.send() # отсылаем


@receiver(post_save, sender=User)
def notify_new_user(sender, instance, created, **kwargs):
    if instance.email:
        html_content = render_to_string( 
            'mail_new_user.html',
            {
                'instance': instance,
            }
        )

        msg = EmailMultiAlternatives(
                    subject=f'Рады Вас видеть!',
                    from_email='stpab18@yandex.ru',
                    to=[instance.email],
                )
        msg.attach_alternative(html_content, "text/html")
        print(msg.body)
        #msg.send() #боремся со спамом так...
