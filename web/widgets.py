from django.forms import RadioSelect


class ColorSelect(RadioSelect):
    # 基于RadioSelect修改
    template_name = '../templates/web/color.html'
    option_template_name = '../templates/web/color_option.html'
