from django import forms
from .models import Label, Labelbase


class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ["labelbase", "type", "ref", "label"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.labelbase_id = kwargs.pop("labelbase_id")
        super(LabelForm, self).__init__(*args, **kwargs)
        user_labelbases = Labelbase.objects.filter(
            user_id=self.request.user.id, id=self.labelbase_id
        )
        self.fields["labelbase"] = forms.ModelChoiceField(
            queryset=user_labelbases,
            required=True,
            widget=forms.HiddenInput(),
        )
        if user_labelbases.count() == 1:
            self.fields["labelbase"].initial = user_labelbases[0]


class LabelbaseForm(forms.ModelForm):
    class Meta:
        model = Labelbase
        fields = ["name", "fingerprint", "about"]
