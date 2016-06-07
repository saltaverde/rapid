from django import forms
from rapid.models import UserProfile
from django.contrib.auth.models import User


class UploadFileForm(forms.Form):
    des = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter description'}))
    public = forms.BooleanField(label='Public Data', initial=False, required=False)
    #token = forms.CharField(max_length=100, widget=forms.HiddenInput(attrs={'style' : 'display: none'}))
    file = forms.FileField(label='File')

class UploadGeoviewForm(forms.Form):
    des = forms.CharField(max_length=50, label='Description ')
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