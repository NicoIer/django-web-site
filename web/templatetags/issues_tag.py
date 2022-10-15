from django.template import Library

register = Library()


@register.simple_tag
def id_padding(num):
    return '#{}'.format(str(num).zfill(4))
