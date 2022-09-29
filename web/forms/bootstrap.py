class BootstrapForm:
    # TODO 修改这种方法 使其更加清晰
    def __init__(self, except_set=None, *args, **kwargs):
        # name是变量名 , field.label是传参的label
        # 这个字段不是这个类有的...是子类的另一个父类有的属性
        if except_set is None:
            except_set = set()

        for name, field in self.fields.items():
            if name in except_set:
                continue
            # if name == 'email':
            field.widget.attrs['data-toggle'] = 'popover'
            field.widget.attrs['data-placement'] = 'bottom'
            field.widget.attrs['data-trigger'] = 'manual'
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = f'Place Enter {name}'
            field.required = True
