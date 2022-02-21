from unicodedata import category
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    authorRating = models.SmallIntegerField(default = 0)

    def update_rating(self):
        postRat = self.post_set.all().aggregate(postRating=Sum('postRating'))
        pRat = 0
        pRat = postRat.get('postRating')

        comRat = self.authorUser.comment_set.all().aggregate(commentRating=Sum('commentRating'))
        cRat = 0
        cRat = comRat.get('commentRating')

        self.authorRating = pRat * 3 + cRat
        self.save()


class Category(models.Model):
    category = models.CharField(max_length = 255, unique = True)


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete = models.CASCADE)

    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = [(NEWS, 'Новость'), (ARTICLE, 'Статья')]

    categoryType = models.CharField(max_length = 8, choices = CATEGORY_CHOICES, default = 'news')
    dateCreation = models.DateTimeField(auto_now_add = True)
    postCategorys = models.ManyToManyField(Category, through = 'PostCategory')
    title = models.TextField()
    text = models.TextField()
    postRating = models.SmallIntegerField(default = 0)

    def like(self):
        self.postRating += 1
        self.save()

    def dislike(self):
        self.postRating -= 1
        self.save()

    def preview(self):
        return self.text[:124] + '...'

    def get_absolute_url(self):
        return f'/news/{self.id}'


class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete = models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete = models.CASCADE)


class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete = models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    dateCreation = models.DateTimeField(auto_now_add = True)
    commentRating = models.SmallIntegerField(default = 0)

    def like(self):
        self.commentRating += 1
        self.save()

    def dislike(self):
        self.commentRating -= 1
        self.save()


class Subscriber(models.Model):
    subscribersUser = models.ForeignKey(User, on_delete=models.CASCADE)
    postCategory = models.ForeignKey(Category, on_delete=models.CASCADE)
    