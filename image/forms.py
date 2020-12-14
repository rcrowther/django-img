from django import forms



class ReformsForm(forms.Form):
    '''
    A form empty of filters, until choices pressed on by __init___
    '''
    error_css_class = 'error'
    required_css_class = 'required'
    available_filters = forms.MultipleChoiceField(
        choices= [],
        help_text="Choose a filter or filters to generate the reforms"
    )
    def __init__(self, filter_choices, *args, **kwargs):
        self.declared_fields['available_filters'].choices = filter_choices
        super().__init__(*args, **kwargs)

