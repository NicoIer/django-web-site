class BootstrapForm:
    def __init__(self, *args: object, **kwargs: object) -> object:
        super().__init__(*args, **kwargs)
        # name是变量名 , field.label是传参的label
        for name, field in self.fields.items():
            # if name == 'email':
            field.widget.attrs['data-toggle'] = 'popover'
            field.widget.attrs['data-placement'] = 'bottom'
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = f'{name}'
            field.required = True
