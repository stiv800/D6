#from re import template
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
#from matplotlib.style import context
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required

import datetime

from .models import *
from .filters import NewsFilter
from .forms import PostsForm


class NewsList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-dateCreation')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name = 'authors').exists()
        return context


class NewsPost(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    paginate_by = 10


    def user_not_subscribed(self):
        user = self.request.user
        id = self.kwargs.get('pk')
        user_subscriptions = [sub.postCategory.category for sub in Subscriber.objects.filter(subscribersUser=user)]
        post_categorys = [cat.category for cat in Post.objects.get(pk=id).postCategorys.all()]
        not_subscribed = list(set(post_categorys).difference(set(user_subscriptions)))
        return not_subscribed

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs.get('pk')
        if self.request.user.is_authenticated:
            context['not_subscribed'] = self.user_not_subscribed()

        return context
    

class NewsSearch(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-dateCreation')


    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


    def get_filter(self):
        return NewsFilter(self.request.GET, queryset=super().get_queryset())


    def get_queryset(self):
        return self.get_filter().qs


    def get_context_data(self, *args,**kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())
        return {
            **super().get_context_data(*args, **kwargs),
            "filter": self.get_filter(),
        }


class PostCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post')
    template_name = 'post_create.html'
    form_class = PostsForm


    def get_context_data(self, *args,**kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.datetime.today()
        posts_today = Post.objects.filter(dateCreation__date__exact=today)
        posts = []
        for post in posts_today:
            if post.author.authorUser.username == self.request.user.username:
                posts.append(post)

        context['limit'] = False if not len(posts) >= 3 else True

        return context


    def user_subscriptions(self):
        user = self.request.user
        id = self.kwargs.get('pk')
        categories = Post.objects.get(pk=id).postCategorys.all()
        user_subscriptions = [sub.postCategory.category for sub in Subscriber.objects.filter(subscribersUser=user)]
        post_categorys = [cat.category for cat in Post.objects.get(pk=id).postCategorys.all()]
        not_subscribed = list(set(post_categorys).difference(set(user_subscriptions)))
        return not_subscribed


class PostUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post')
    template_name = 'post_create.html'
    form_class = PostsForm


    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)
 
 
class PostDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post')
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'


@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/news')


@login_required
def subscribe_me(request):
    if request.method == "POST":
        user = request.user
        id_news = request.POST['id_news']
        post = Post.objects.get(pk=id_news)

        categories = set()
        for sub in post.postCategorys.all():
            if request.POST.get(sub.category):
                categories.add(request.POST.get(sub.category))

        if categories:
            user_subscriptions = {sub.postCategory.category for sub in Subscriber.objects.filter(subscribersUser=user)}
            categories_set = categories.difference(user_subscriptions)

            if categories_set:
                for cat in categories_set:
                    Subscriber.objects.create(subscribersUser=User.objects.get(username=user), postCategory=Category.objects.get(category=cat))

        return redirect(f'/news/{id_news}')
