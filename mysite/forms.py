from django import forms
from django.contrib.auth import get_user_model

from .models.profile_models import Profile

class UserCreateForm(forms.ModelForm):
    password = forms.CharField()

    class Meta:
        model = get_user_model()
        fields = ('email',)

    def clean_password(self):
        password = self.cleaned_data.get("password")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'username',
            'zipcode',
            'prefecture',
            'city',
            'address',
            'image',
            'is_public',
        )

    def save(self, user_image=None, commit=True):
        profile = super().save(commit=False)
        # 新しい画像がアップロードされていない場合、既存の画像を保持
        if self.cleaned_data.get('image') == "images/default.png" and user_image != "images/default.png":
            profile.image = user_image.replace('media/', '')
        if commit:
            profile.save()
        return profile