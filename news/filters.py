from warnings import filters
#from attr import field
import django
#from django.forms import DateField
from django_filters import FilterSet # импортируем filterset, чем-то напоминающий знакомые дженерики
from .models import *

 
class NewsFilter(FilterSet):
    class Meta:
        model = Post
        fields = {
            'dateCreation':['date__gt'],
            'title': ['icontains'],
            'author__authorUser': ['in']
            }
