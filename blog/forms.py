from django import forms

from .models import Comment, Article, ArticleTag

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'comment',
        )

class ArticleNewForm(forms.ModelForm):
    # 新たにtagsを定義（理由：勝手にchoiceFieldにされるから）
    # ?リンク先 https://zenn.dev/cococig/articles/d3374aa8fd70b0

    tags = forms.CharField(label="タグ", max_length=250, required=False)
    class Meta:
        model = Article
        fields = {
            'title',
            'text',
        }

    def clean_tags(self):
        # is_valid()が呼び出された時に処理が走る
        tags = self.cleaned_data['tags']

        # カンマで区切られたタグをリストに変換
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

        # 処理が終わったらself.cleaned_data['tags']に自動的に入れてくれる
        return tag_list

    def save(self, author, commit=True):
        article = super().save(commit=False)

        # ユーザー情報をauthorカラムに入れる
        article.author = author
        article.save()
        for tag_name in self.cleaned_data['tags']:
            slug = tag_name.lower().replace(' ', '-')
            tag, created = ArticleTag.objects.get_or_create(slug=slug, defaults={'name': tag_name})
            print('タグのsaveが呼ばれました。', tag, created)
            article.tags.add(tag)
        return article