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

    def save(self, user, user_image_url=None, commit=True):
        profile = super().save(commit=False)
        default_image = f"profile_images/{user.id}/default.png"

        # 新しい画像がアップロードされていない場合、既存の画像を保持
        if self.cleaned_data.get('image') == "images/default.png" and user_image_url != default_image:
            print('アイコンは変わっていません')
            profile.image = user_image_url.replace(f'media/profile_images/{user.id}', '')
        else:
            print('アイコンは変わっています')

            # アイコンが変更されたため、メディアのプロフィール画像を削除
            profile_image = Profile.objects.get(user=user)
            print('profile_image.image', str(profile_image.image))
            if not "images/default.png" in str(profile_image.image):
                print(str(profile_image.image), 'を削除しました。')
                profile_image.image.delete(save=False)
            else:
                print(str(profile_image.image), 'のため削除しません。')
        if commit:
            profile.save()
        return profile