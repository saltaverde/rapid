from django import forms
from rapid.models import UserProfile
from django.contrib.auth.models import User


class UploadFileForm(forms.Form):
    des = forms.CharField(max_length=50, label='Description ')
    public = forms.BooleanField(initial=False, required=False)
    #token = forms.CharField(max_length=100, widget=forms.HiddenInput(attrs={'style' : 'display: none'}))
    file = forms.FileField(label='File ')


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ()