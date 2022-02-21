from django import template
 
register = template.Library()


@register.filter(name='cenzor')
def cenzor(value):
    bad_words = ('ххх', 'ууу')
    for word in bad_words:
        value = value.replace(word, '@@@@@')
    return value