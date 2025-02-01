import os
import json
import payjp
import random

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.views import View
from django.db.models import Count, Sum
from django.db.models import Q
from django.forms.models import model_to_dict
from django.template.loader import render_to_string

# 非同期処理
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

from .models import *
from mysite.models.profile_models import Profile
from .forms import *
from common.myiste_def import *




################
##  記事の一覧
################
class ArticleIndexView(CustomLoginRequiredMixin, View):
    template_name = 'mysite/blog/blogs.html'

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page')

        articles = Article.objects.filter(is_public=True).annotate(
            # ! distinct=Trueで重複を避ける
            like_count=Count('article_like', distinct=True),
            comment_count=Count('comments', distinct=True),
            view_total_count=Count('view_count', distinct=True),
        ).order_by('-created_at')
        # 1ページの記事の表示を変更
        paginator = Paginator(articles, 20).get_page(page_number)

        # 決済未完了のorderを取得
        orders = Order.objects.filter(user=request.user, order_status=0)

        # タプルの内容をflat=Trueでリスト形式に変更
        purchased_article_ids = orders.values_list('article_id', flat=True)

        # UserItemが存在していたら購入扱いにする
        user_items = user_item_index(request, request.user, 1)
        user_item_ids = user_items.values_list('article_id', flat=True)

        return render(request, self.template_name, {
            'page_title': 'ブログ一覧画面',
            'paginator_articles': paginator,
            'page_number': page_number,
            'purchased_article_ids': purchased_article_ids,
            'user_item_ids': user_item_ids,
        })


################
##  記事の無限スクロール
################
class ArticleListApiView(CustomLoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        print("リクエストが届きました。")

        ## Ajaxで送られてくるデータの取得
        print(f"request.GET => {request.GET}")
        try:
            request_data = request.GET
            offset = int(request_data.get('offset'))
        except json.JSONDecodeError:
            return JsonResponse({"message": "error", "details": "Invalid JSON"}, status=400)

        ## 無限スクロールでは10ページごとを更新していく
        articles = Article.objects.filter(is_public=True).annotate(
            # ! distinct=Trueで重複を避ける
            like_count=Count('article_like', distinct=True),
            comment_count=Count('comments', distinct=True),
            view_total_count=Count('view_count', distinct=True),
        ).order_by('-created_at')[offset:offset+10]

        ## 無限スクロールで全て表示している場合
        if not articles:
            return JsonResponse({
            "message": "success",
            "limit": True,
        }, status=200)

        # 決済未完了のorderを取得
        orders = Order.objects.filter(user=request.user, order_status=0)

        # タプルの内容をflat=Trueでリスト形式に変更
        purchased_article_ids = orders.values_list('article_id', flat=True)

        # UserItemが存在していたら購入扱いにする
        user_items = user_item_index(request, request.user, 1)
        user_item_ids = user_items.values_list('article_id', flat=True)

        ## HTMLをサーバー側でレンダリング
        include_articles_html = render_to_string("snippets/articles_index.html",
            {
                "paginator_articles": articles,
                "purchased_article_ids": purchased_article_ids,
                "user_item_ids": user_item_ids,
            }
        )

        return JsonResponse({
            "message": "success",
            "include_articles_html": include_articles_html,
        }, status=200)



################
##  記事の作成
################
class ArticleNewView(CustomLoginRequiredMixin, View):
    template_name = 'mysite/blog/blog_new.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'title': '新規ブログ作成',
        })

    def post(self, request, *args, **kwargs):
        article_new_form = ArticleNewForm(request.POST)
        print('request.POST.get', request.POST.get)
        images = request.FILES.getlist('images', None)
        context = {
            'article_new_form': article_new_form,
        }

        if article_new_form.is_valid() and images:
            # forms.pyの中でタグの設定などの処理を行う
            form = article_new_form.save(request.user, commit=False)
            form.save()
            # 複数画像の保存
            for image in images:
                Image.objects.create(article=form, image=image)

            messages.success(request, '記事を作成しました。')
            return redirect('blog:detail', form.id)
        else:
            messages.error(request, '記事の作成に失敗しました。')
            if not images:
                image_error = '画像を1枚以上選択してください'
                context['image_error'] = image_error

        return render(request, self.template_name, context)


################
##  記事の詳細
################
class ArticleDetailView(CustomLoginRequiredMixin, View):
    template_name = 'mysite/blog/article.html'

    def get(self, request, pk, *args, **kwargs):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            messages.error(request, '指定された記事は存在しません。')
            return redirect('blog:index')

        comments = Comment.objects.filter(article=article)
        comments_with_time = [(comment, days_ago_comment(comment.created_at)) for comment in comments]
        like_count = ArticleLike.objects.filter(article=article).count()

        # 投稿者以外のユーザーが表示させたら閲覧数のカウントをする
        view_count = ViewCount.create_view_count(request.user, article)

        return render(request, self.template_name, {
            'article': article,
            'comments_with_time': comments_with_time,
            'like_count': like_count,
            'view_count': view_count,
        })

    def post(self, request, pk, *args, **kwargs):
        # textareaのnameがrequest.POST.get('comment')に送られてくる
        request_comment = request.POST.get('comment')

        try:
            article = Article.objects.get(pk=pk)
        except Comment.DoesNotExist:
            messages.error(request, 'コメントの投稿に失敗しました。')
            return redirect('blog:index')

        comment_form = CommentForm(request.POST)

        # 非同期処理を使わない、いいね機能
        # if request.POST.get('like_count', None):
        #     if request.POST.get('like_delete', None):
        #         ArticleLike.objects.filter(user=request.user, article=article).delete()
        #     elif article_like_exists(article, request.user):
        #         ArticleLike.objects.create(user=request.user, article=article)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.article = article
            comment.save()
            # 通知を飛ばす
            notification_create(
                request.user,
                receive_user=article.comments.all(),
                action_type="comment",
                object=comment,
                article=article
            )
        else:
            messages.error(request, '処理に失敗しました。')
            return redirect('blog:detail', pk)

        comments = Comment.objects.filter(article=article)
        comments_with_time = [(comment, days_ago_comment(comment.created_at)) for comment in comments]
        like_count = ArticleLike.objects.filter(article=article).count()

        return render(request, self.template_name, {
            'article': article,
            'comment_form': comment_form,
            'comments_with_time': comments_with_time,
            'like_count': like_count,
        })


################
##  記事の編集
################
class ArticleEditView(CustomLoginRequiredMixin, View):
    template_name = 'mysite/blog/blog_new.html'

    def get(self, request, pk, *args, **kwargs):
        article = Article.objects.get(pk=pk)
        tag_list = article.tags.all()
        tag_string = '、'.join([tag.name for tag in tag_list])

        return render(request, self.template_name, {
            'title': 'ブログ編集',
            'article': article,
            'article_title': article.title,
            'article_text': article.text,
            'tags': tag_string,
            'article_is_public': article.is_public,
            'article_sell_flag': article.sell_flag,
            'article_price': article.price,
        })

    def post(self, request, pk, *args, **kwargs):
        article = Article.objects.get(pk=pk)
        article_new_form = ArticleNewForm(request.POST, instance=article)
        images = request.FILES.getlist('images', None)

        if article_new_form.is_valid():
            # forms.pyの中でタグの設定などの処理を行う
            form = article_new_form.save(request.user, commit=False)
            form.save()
            if images:
                # 既存の画像のファイルを削除
                existing_images = Image.objects.filter(article=article)
                for image in existing_images:
                    # メディアフォルダのファイルを削除
                    image.image.delete(save=False)
                existing_images.delete()
                for image in images:
                    Image.objects.create(article=form, image=image)

            messages.success(request, '記事を編集しました。')
            return redirect('blog:detail', form.id)
        else:
            article_new_form = ArticleNewForm(instance=article)
            tags = request.POST.get('tags')
            messages.error(request, '記事の編集に失敗しました。')

        return render(request, self.template_name, {
            'article_new_form': article_new_form,
            'article_title': article_new_form['title'].initial,
            'article_text': article_new_form['text'].initial,
            'tags': tags,
            'article_is_public': article_new_form['is_public'].initial,
            'article_sell_flag': article_new_form['sell_flag'].initial,
            'article_price': article_new_form['price'].initial,
        })



################
##  記事の削除
################
class ArticleDeleteView(CustomLoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        try:
            article = Article.objects.get(pk=pk)
            # メディアの画像も一緒に削除
            for image in article.image.all():
                image.image.delete(save=False)
            article.delete()

            messages.success(request, '記事を削除しました。')

        except Article.DoesNotExist:
            messages.error(request, '記事の削除に失敗しました。')
        return redirect('blog:index')


################
##  タグ
################
class ArticleTagView(CustomLoginRequiredMixin, View):
    template_name = 'mysite/blog/blogs.html'

    def get(self, request, name, *args, **kwargs):
        page_number = request.GET.get('page')
        tag = ArticleTag.objects.get(name=name)
        articles = tag.articles.all()
        tag_obj = articles.filter(is_public=True)

        paginator = Paginator(tag_obj, 3).get_page(page_number)

        orders = Order.objects.filter(user=request.user, order_status=0)

        # タプルの内容をflat=Trueでリスト形式に変更
        purchased_article_ids = orders.values_list('article_id', flat=True)

        # UserItemが存在していたら購入扱いにする
        user_items = user_item_index(request, request.user, 1)
        uset_item_ids = user_items.values_list('article_id', flat=True)

        return render(request, self.template_name, {
            'page_title': '記事一覧 #{}'.format(name),
            'paginator_articles': paginator,
            'page_number': page_number,
            'purchased_article_ids': purchased_article_ids,
            'uset_item_ids': uset_item_ids,
        })


################
##  非同期いいね
################
class ArticleLikeView(CustomLoginRequiredMixin, View):

    def get(self, request, pk, *args, **kwargs):
        context = {
            "message": "error",
        }
        return JsonResponse(context)

    def post(self, request, pk, *args, **kwargs):
        # javascriptから送られてきたbodyの中身を取得
        data = json.loads(request.body)
        # bodyの中のarticle_pkを取得
        article_pk = data.get('article_pk')

        context = {
            "message": "error",
        }
        try:
            article = Article.objects.get(pk=article_pk)
            # article = Article.objects.get(pk=pk)でも可能
        except Article.DoesNotExist:
            messages.error(request, '存在しない記事です。')
            return redirect('blog:index')

        try:
            like_exists = article_like_exists(article, request.user)

            if like_exists:
                article_like = ArticleLike.objects.create(user=request.user, article=article)
                context["method"] = "create"

                # いいねされた記事の投稿主に通知を飛ばす
                if article.author != request.user:
                    notification_create(request.user, receive_user=article.author, action_type="like", object=article_like)
            else:
                ArticleLike.objects.filter(user=request.user, article=article).delete()
                context["method"] = "delete"
            context['message'] = 'success'
            # いいねのカウント数を集計
            context["like_count"] = article.article_like.count()
        except:
            pass

        return JsonResponse(context)



################
##  非同期コメント
################

class CommentNewView(CustomLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        context = {"message": "error"}

        try:
            data = json.loads(request.body)
            article_id = data.get("article_id")
            comment = data.get("comment")
            article = Article.objects.get(pk=article_id)
        except json.JSONDecodeError as e:
            return JsonResponse({"message": "error", "details": "Invalid JSON"}, status=400)
        except Article.DoesNotExist:
            return JsonResponse({"message": "error", "details": "Article not found"}, status=404)

        comment_form = CommentForm(data)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.article = article
            comment.save()
            # 通知を飛ばす
            notification_create(
                request.user,
                receive_user=article.comments.all(),
                action_type="comment",
                object=comment,
                article=article
            )
            context = {
                "message": "success",
                "comment": model_to_dict(comment), ## 自動的に辞書形式に変換
                "username": comment.user.profile.username,
                "comment_create_time": days_ago_comment(comment.created_at),
                "comment_count": article.comments.count(),
            }
            return JsonResponse(context)

        ## コメント作成時にエラーの場合
        context["details"] = "Invalid form data"
        context["errors"] = comment_form.errors
        return JsonResponse(context, status=400)



class CommentEditView(CustomLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            print(data)
            comment_id = data.get("comment_id")
            comment = Comment.objects.get(id=comment_id)
        except json.JSONDecodeError as e:
            return JsonResponse({"message": "error", "details": "Invalid JSON"}, status=400)
        except Comment.DoesNotExist:
            return JsonResponse({"message": "error", "details": "Comment not found"}, status=404)

        form = CommentForm(data, instance=comment)
        if form.is_valid():
            comment = form.save()
            print(comment.comment)
            return JsonResponse({"message": "success", "comment_id": comment.id, "comment_text": comment.comment}, status=200)

        return JsonResponse({"message": "error", "details": "Invalid form data", "errors": form.errors}, status=400)



class CommentDeleteView(CustomLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            comment_id = data.get("comment_id")
            comment = Comment.objects.get(id=comment_id)
            comment_count = comment.article.comments.count()
            comment.delete()
        except json.JSONDecodeError as e:
            return JsonResponse({"message": "error", "details": "Invalid JSON"}, status=400)
        except Comment.DoesNotExist:
            return JsonResponse({"message": "error", "details": "Comment not found"}, status=404)
        except Exception as e:
            return JsonResponse({"message": "error", "details": "予期しないエラーが発生しました", "error_message": e}, status=500)

        return JsonResponse({"message": "success", "comment_count": comment_count - 1}, status=200)


################
##  検索機能
################

class SearchView(View):
    template_name = 'mysite/search.html'
    def get(self, request, *args, **kwargs):
        # ?:作ってみただけ
        form = SearchForm()
        context = {}

        search = request.GET.get('search', None)
        articles = request.GET.get('articles', None)
        users = request.GET.get('users', None)

        if search and (articles or users):
            context['search'] = search
            context['filter'] = True

        if search and articles:
            context['articles'] = Article.objects.filter(Q(title__icontains=search) | Q(text__icontains=search))
        elif search and users:
            context['users'] = Profile.objects.filter(username__icontains=search)


        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        search = request.POST.get('search')
        articles = Article.objects.filter(Q(title__icontains=search) | Q(text__icontains=search))
        users = Profile.objects.filter(username__icontains=search)
        random_number = random.randint(1, 5)

        context = {
            'search': search,
            'articles': articles,
            'users': users,
            'random_number': random_number,
        }

        return render(request, self.template_name, context)


################
##  通知機能
################

class NotificationView(View):
    template_name = 'mysite/notification/notification.html'
    def get(self, request, *args, **kwargs):
        action_type = request.GET.get('action_type')

        new_notifications = Notification.objects.select_related('profile').filter(user=request.user, is_read=False)
        # TODO: 一度だけカウント数をtemplate側で表示させたい

        # 通知の既読をつける
        new_notifications.update(is_read=True)

        context = {
            'title' : '通知一覧',
            "action_type": ACTION_TYPE,
        }
        context = filter_notifications(request.user, action_type, context)

        return render(request, self.template_name, context)



################
##  カート
################
class ArticleInCartView(CustomLoginRequiredMixin, View):
    # カートに入れるを選択するとorderが作成され、カートから外すを選択でorderを削除する処理

    def get(self, request, *args, **kwargs):
        # TODO:非同期処理にする
        article_id = request.GET.get('article_id')
        delete = request.GET.get('delete', None)

        if delete:
            try:
                orders = Order.objects.filter(user=request.user, article=article_id, charge_type=0)
                orders.delete()
                messages.info(request, 'マイカートから商品を削除しました。')
            except Order.DoesNotExist as e:
                messages.error(request, f'商品をカートから外す処理に失敗しました。{e}')
            return redirect('blog:index')
        else:
            try:
                article = Article.objects.get(pk=article_id)
            except Article.DoesNotExist:
                messages.error(request, '記事の取得に失敗しました。')
                return redirect('blog:index')

            order_exists = Order.objects.filter(
                user=request.user,
                article=article,
                price=article.price,
                charge_type=0,
                order_status=0,
            ).exists()
            if not order_exists:
                Order.objects.create(
                    user=request.user,
                    article=article,
                    price=article.price,
                    charge_type=0,
                    order_status=0,
                )
                messages.success(request, 'マイカートに追加しました。')
                return redirect('blog:index')
            else:
                messages.error(request, 'すでにカートに追加済みです。')
                return redirect('blog:index')



################
##  決済
################
class ArticlePurchaseView(CustomLoginRequiredMixin, View):
    # Orderの決済未登録を取得して表示させる
    # 購入できたらUserItemにデータを作成する

    template_name = 'mysite/article_purchase.html'
    payjp.api_key = os.environ['PAYJP_SECRET_KEY']
    public_key = os.environ['PAYJP_PUBLIC_KEY']

    def get(self, request, *args, **kwargs):
        print(request.user.email)
        orders = Order.objects.select_related('article').filter(user=request.user, charge_type=0, order_status=0)
        # ! ordersのクエリセットに対してaggregateメソッドは、辞書型の結果を返す。
        total_price = orders.aggregate(total_price=Sum('price'))['total_price']

        return render(request, self.template_name, {
            'public_key': self.public_key,
            'orders': orders,
            'total_price': total_price,
        })

    # 購入した直後の処理
    def post(self, request, *args, **kwargs):
        orders = Order.objects.filter(user=request.user, charge_type=0, order_status=0)
        total_price = int(request.POST.get('total_price'))
        articles = [order.article for order in orders]
        payjp_token = request.POST.get('payjp-token')

        print('リクエスト内容', request.POST.get)

        if total_price < 50 or total_price > 9999999:
            messages.error(request, 'PAY.JPでは50円未満または9,999,999円超は決済範囲外の扱いです。')
            return redirect('blog:purchase')

        # UserItemが存在していたらMultipleObjectsReturnedエラーを返す
        print('UserItemが存在するかの確認')
        for article in articles:
            user_items = UserItem.objects.filter(user=request.user, article=article)
            if user_items.count() > 1:
                messages.error(request, 'ユーザーのアイテムが複数存在しています。')
                return redirect('blog:purchase')
            elif user_items.exists():
                messages.error(request, 'すでに購入しています。')
                return redirect('blog:purchase')
        print('UserItemは存在しないことが発覚')

        try:
            # 作成されたトークンをもとに作成されたのは誰かを判定して作成する
            print('作成されたトークンをもとに誰かを判定開始')
            customer = payjp.Customer.create(
                email = 'example@pay.jp',
                card = payjp_token,
            )
            print('ユーザー情報の作成が完了')

            # 登録したカードが決済に有効かどうか？
            if customer['cards']['data'][0]['cvc_check'] != 'passed':
                print('カード情報の処理に失敗しました。')
                messages.error(request, 'カード情報のCVCチェックに失敗しました。')
                return redirect('blog:purchase')

            print(f'ordersの支払い開始 order : {orders}')
            # それぞれのorderの支払いを行う
            charge = payjp.Charge.create(
                amount = total_price,
                currency = 'jpy', #通貨のこと
                customer = customer.id,
                description = '決済テスト',
            )
            print('支払いが完了')

        except:
            messages.error(request, '決済に失敗しました。')
            return redirect('blog:purchase')

        # tryの中の処理が成功したら
        else:
            # orderの課金タイプをクレカ、決済ステータスを決済完了に変更
            for order in orders:
                order.charge_type=1
                order.order_status=1
                order.save()

            for article in articles:
                UserItem.objects.create(user=request.user, article=article, charge_type=1)

                # 購入通知（アプリ内）を飛ばす
                notification_create(
                    request.user,
                    action_type="purchase",
                    article=article
                )
            print('UserItem、Notificationの作成完了')

            # 購入通知（メール）を飛ばす
            subject = "【購入メール】商品の購入をありがとうございます。"
            name = request.user.profile.username
            email = request.user.email
            articles = articles
            total_price = sum(article.price for article in articles)
            is_send_email = create_email(subject, name, email, articles=articles, price=total_price)
            if is_send_email == "送信完了":
                print('メール送信が完了しました。')
            else:
                print('メール送信に失敗しました。')

            messages.success(request, '購入が完了しました。')
            return render(request, self.template_name, {
                'amount': total_price,
                'public_key': self.public_key,
                'charge': charge,
                'card': payjp_token,
                'customer': customer,
            })

################
##  フォロー
################
class FollowView(CustomLoginRequiredMixin, View):

    # フォロー一覧画面
    def get(self, request, pk, *args, **kwargs):
        template_name = 'mysite/follow/follows.html'

        follower = request.GET.get('follower', None)

        user = get_user_model().objects.get(pk=pk)
        if follower:
            follower_list = user.profile.follows.all()
            print(follower_list)
            if request.user == user:
                title = 'あなたのフォロワー'
            title = f'{user.profile.username}さんのフォロワー'
            context = {
                'follower': follower_list,
                'title': title,
            }
        else:
            followed_by_list = user.followed_by.all()
            if request.user == user:
                title = 'あなたがフォローしたユーザー'
            title = f'{user.profile.username}さんのフォローしたユーザー'
            context = {
                'followed_by': followed_by_list,
                'title': title,
            }

        return render(request, template_name, context)

    # フォローした時の処理
    def post(self, request, pk, *args, **kwargs):
        follow_delete = request.POST.get('delete', None)

        # TODO:非同期処理にする

        try:
            user = get_user_model().objects.get(pk=pk)
        except get_user_model().DoesNotExist:
            messages.error(request, '存在しないユーザーにアクセスしました。')
            return redirect('/')

        profile = Profile.objects.get(user=request.user)
        if follow_delete:
            Follow.objects.get(follower=request.user, followed=user).delete()
            profile.follows.remove(user)
        else:
            following = Follow.objects.create(follower=request.user, followed=user)
            profile.follows.add(user)

            # フォロー通知を飛ばす
            notification_create(
                request.user,
                receive_user=user,
                action_type="follow",
                object=following,
            )

        profile.save()
        return redirect('author', pk=pk)




################
##  DM
################
class DMIndexView(CustomLoginRequiredMixin, View):
    template_name = 'mysite/dm/dm_index.html'

    def get(self, request, *args, **kwargs):

        conversations = Conversation.objects.select_related('user1', 'user2').filter(Q(user1=request.user) | Q(user2=request.user))
        conversation_with_time = []
        for conversation in conversations:
            if (last_message := conversation.messages.last()):
                partner = conversation.user2 if conversation.user1 == request.user else conversation.user1
                time_ago = days_ago_comment(last_message.created_at)
                conversation_with_time.append((conversation.id, partner, time_ago))


        return render(request, self.template_name, {
            "conversation_with_time": conversation_with_time,
        })


class DMCreateView(CustomLoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        try:
            partner = get_user_model().objects.get(pk=pk)
        except get_user_model().DoesNotExist:
            messages.error(request, '存在しないユーザーにアクセスしました。')
            return redirect('/')

        dm_room = Conversation.objects.filter(
                Q(user1=request.user, user2=partner) | Q(user1=partner, user2=request.user)
            ).first()

        if not dm_room:
            dm_room = Conversation.objects.create(user1=request.user, user2=partner)

        return redirect('blog:dm_detail', dm_room.id)


class DMDetailView(CustomLoginRequiredMixin, View):
    template_name = 'mysite/dm/dm_detail.html'
    User = get_user_model()

    def get(self, request, pk, *args, **kwargs):

        try:
            dm_room = Conversation.objects.get(pk=pk)
            if dm_room.user1 == request.user:
                partner = self.User.objects.get(pk=dm_room.user2.id)
            else:
                partner = self.User.objects.get(pk=dm_room.user1.id)
        except Conversation.DoesNotExist:
            messages.error(request, '存在しないルームにアクセスしました。')
            return redirect('/')
        except self.User.DoesNotExist:
            messages.error(request, '指定したユーザーが存在しません。')
            return redirect('/')

        # 既読をつける
        partner_send_messages = Message.objects.filter(conversation=dm_room, sender=partner, is_read=False)
        partner_send_messages.update(is_read=True)

        all_messages = Message.objects.filter(conversation=dm_room)

        # メッセージ投稿日時を取得（何日前か？など）
        messages_with_time = [(message, days_ago_comment(message.created_at)) for message in all_messages]

        return render(request, self.template_name, {
            'partner': partner,
            "messages_with_time": messages_with_time,
            'room_name': pk,
        })

    def post(self, request, pk, *args, **kwargs):
        text = request.POST.get('text', None)
        image = request.FILES.get('image', None)

        if not text and not image:
            messages.error(request, 'メッセージの送信に失敗しました。')
            return redirect('blog:dm_detail', pk=dm_room.id)

        try:
            dm_room = Conversation.objects.get(pk=pk)
        except Conversation.DoesNotExist:
            messages.error(request, '存在しないルームにアクセスしました。')
            return redirect('/')

        if dm_room.user1 == request.user:
                partner = self.User.objects.get(pk=dm_room.user2.id)
        else:
            partner = self.User.objects.get(pk=dm_room.user1.id)

        dm_room = Conversation.objects.filter(
            Q(user1=request.user, user2=partner) | Q(user1=partner, user2=request.user)
        ).first()
        form = DMForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = dm_room
            message.sender = request.user
            message.save()

        # DM時に通知を飛ばす
        notification_create(request.user, receive_user=partner, action_type="dm", object=message)

        return redirect('blog:dm_detail', pk=dm_room.id)


def chat_room(request, room_name):
    print(f'Room name: {room_name}')
    return render(request, 'demo/dm_chat.html', {
        'room_name': room_name
    })