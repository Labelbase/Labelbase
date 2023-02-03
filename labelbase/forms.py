
from django import forms
from .models import Label, Labelbase

class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['labelbase', 'type', 'ref', 'label']
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(LabelForm, self).__init__(*args, **kwargs)
        self.fields['labelbase'] = forms.ModelChoiceField(
            queryset=Labelbase.objects.filter(user_id=request.user.id),
            required=True,
            widget=forms.Select(attrs={'class': 'chzn-select'}),
        )
