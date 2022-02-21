from django.forms import ModelChoiceField, ModelForm, ModelMultipleChoiceField, TypedChoiceField
from django import forms
#from matplotlib.pyplot import title
from .models import *


class PostsForm(ModelForm):
    aa = Post.objects.select_related('author__authorUser').all()
    bb = aa.values()
    author = forms.ModelChoiceField(label='Автор', queryset=Post.author.get_queryset())
    title = forms.CharField(label='Заголовок')
    text = forms.CharField(label='Текст')
    postCategorys = forms.ModelMultipleChoiceField(label='Категория', queryset=Category.objects.all(), to_field_name='category')
    categoryType = forms.ChoiceField(label='Тип', choices=Post.CATEGORY_CHOICES)


    class Meta:
        model = Post
        fields = ['author', 'title', 'text', 'postCategorys', 'categoryType']
        