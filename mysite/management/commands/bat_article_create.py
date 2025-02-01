from django.core.management.base import BaseCommand

import os
import random
import pprint
from django.utils.text import slugify
from django.conf import settings
import shutil

from blog.models import *
from mysite.models import User

class Command(BaseCommand):
    help = "ランダムな記事を作成し、ユーザーごとにタグをランダムに付与する"

    def add_arguments(self, parser):
        # コマンドライン引数を追加
        parser.add_argument("count", type=int, help="1ユーザーにつき作成する記事の数")

    def handle(self, *args, **options):
        base_path = "/Users/miedashuya/Desktop/practice/REALLYSITE/media/article/images"

        all_files_name = []
        all_existing_files = []

        ## 「/media/article/images/UserID/ArticleID」内のすべての画像ファイルを取得
        for user_folder in os.listdir(base_path):
            user_path = os.path.join(base_path, user_folder)

            ## UserIDのフォルダでない場合は処理しない
            if not os.path.isdir(user_path):
                continue

            for article_folder in os.listdir(user_path):
                article_path = os.path.join(user_path, article_folder)

                if os.path.isdir(article_path):  # ArticleIDのフォルダか確認
                    for file in os.listdir(article_path):
                        file_path = os.path.join(user_folder, article_folder, file)
                        all_existing_files.append(file_path)
                        all_files_name.append(file)

        pprint.pprint(all_files_name)  # ファイル一覧を出力

        ## コマンドライン引数を取得
        article_create_count = options["count"]

        print("Articleを作成します。開始")
        user_all = User.objects.all().order_by("-id")
        user_count = user_all.count()
        print(f"現在のユーザー数は{user_count}人ですので、{user_count}人分の記事を作成します。")
        print("-"*30)

        for _ in range(article_create_count):
            for user in user_all:

                ### 記事の作成 ###

                ## タイトルを設定
                article_title = random.choice(Command.ARTICLE_TITLE)
                ## テキストを設定
                article_text = random.choice(Command.ARTICLE_TEXT)
                ## 記事を販売と価格を設定
                sell_flg = bool(random.randint(0, 1))
                price = random.randint(300, 2000) if sell_flg else None

                article = Article.objects.create(
                    title = article_title,
                    text = article_text,
                    author = user,
                    is_public = True,
                    sell_flag = sell_flg,
                    price = price,
                )

                ### 画像の作成 ###
                for _ in range(random.randint(1, 2)):
                    ## /media/article/images/をmedia_pathに代入する
                    media_path = os.path.join(settings.MEDIA_ROOT, "article", "images")

                    ## 現在/media/article/imagesにある画像全ての中から1つのみ自動で取得する
                    get_file_path = random.choice(all_existing_files)
                    existing_file_path = os.path.join(base_path, get_file_path)
                    existing_file_name = os.path.basename(get_file_path)

                    user_id = 'UserID:' + str(user.id)
                    article_id = 'ArticleID:' + str(article.id)

                    new_directory = os.path.join(media_path, user_id, article_id)
                    # ディレクトリが存在しない場合は作成する
                    os.makedirs(new_directory, exist_ok=True)
                    new_file_name = os.path.join(new_directory, existing_file_name)

                    # ファイルが存在しない場合は処理終了
                    if not os.path.exists(existing_file_path):
                        print(f"コピー元のファイルが見つかりません: {existing_file_path}")
                        return

                    shutil.copyfile(existing_file_path, new_file_name)

                    image = os.path.join('article', 'images', user_id, article_id, existing_file_name)
                    Image.objects.create(article=article, image=image)

                ### タグの作成 ###

                ## 50%の確率でタグの設定しないと判断したらタグは設定しない
                tag_create_flg = bool(random.randint(0, 1))
                if not tag_create_flg:
                    print(f"ユーザーID：{user.id}の記事作成完了:記事のID：{article.id}")
                    continue

                tag_list = []
                for _ in range(random.randint(1, 5)):
                    tag_name = random.choice(Command.TAG_WORD)
                    slug = slugify(tag_name)
                    ## slug="python"とslug="Python"を別のタグとして認識してしまう可能性があるため、大文字小文字を区別せず検索
                    ## (get_or_createdでも良いが拡張性は現在のコードの方が良い)
                    tag = ArticleTag.objects.filter(slug__iexact=slug).first()
                    if not tag:
                        tag = ArticleTag.objects.create(slug=slug, name=tag_name)

                    tag_list.append(tag)

                article.tags.set(tag_list)

                print(f"ユーザーID：{user.id}の記事作成完了:記事のID：{article.id}")

        print("-"*30)
        print("Articleを作成します。終了")

    ## 記事のタイトルを20個設定しておき、記事の作成時にランダムで選んで作成する
    ARTICLE_TITLE = [
        # 🌟 トレンド・ライフスタイル
        "2025年最新！ライフハックで毎日を効率化する方法",
        "これだけでOK！朝のルーティンで1日を最高にする秘訣",
        "スマホ1つでできる！最新の副業アイデア10選",
        "シンプルライフのすすめ｜ミニマリストが教える暮らしのコツ",
        "SNSでバズる！魅力的な写真を撮るための5つのテクニック",

        # 📚 ビジネス・自己啓発
        "成功者が実践する朝の習慣5選",
        "仕事の生産性が劇的に上がる！最新タスク管理術",
        "失敗しない！初めてのフリーランス生活完全ガイド",
        "あなたの価値を最大化する！自己ブランディング戦略",
        "年収アップのカギ！交渉力を磨くための心理学テクニック",

        # 🏠 ライフスタイル・趣味
        "初心者でも簡単！観葉植物でおしゃれな部屋を作るコツ",
        "週末の楽しみ方10選｜一人でも満喫できるおすすめアクティビティ",
        "読書好き必見！2025年おすすめのベストセラー本ランキング",
        "コーヒー好きのための、至極の1杯を淹れる方法",
        "旅行好きが選ぶ！日本国内の絶景スポットTOP10",

        # 💻 テクノロジー・ガジェット
        "AIが変える未来｜最新テクノロジーがもたらす影響とは？",
        "スマートホームの最前線！便利すぎるIoTデバイス5選",
        "プログラミング初心者向け！独学で学べる無料リソースまとめ",
        "メタバースって何？未来のインターネット体験を徹底解説！",
        "知らないと損！Google検索を極める便利ワザ10選"
    ]

    ## 記事のテキストを20個設定しておき、記事の作成時にランダムで選んで作成する
    ARTICLE_TEXT = [
        "朝のルーティンを変えるだけで、1日の生産性が大きく向上します。例えば、朝の時間を有効活用し、軽いストレッチや読書を取り入れることで、頭が冴えた状態で仕事や勉強をスタートできます。",
        "成功者が共通して持つ習慣とは何でしょうか？多くの成功者は、毎日決まった時間に起き、日記をつけたり、目標を明確にしたりしています。小さな積み重ねが大きな結果を生むのです。",
        "スマホだけでできる副業が急増中！プログラミング、ライティング、デザイン、オンライン販売など、手軽に始められる仕事が増えています。まずは自分の得意なことを活かしてみましょう。",
        "シンプルライフを実践することで、ストレスを減らし、心に余裕が生まれます。不要なものを減らし、本当に大切なものに集中することで、より充実した毎日を送ることができるでしょう。",
        "SNSのアルゴリズムを理解すれば、フォロワーを増やすのも簡単です。投稿のタイミングやハッシュタグの活用、ユーザーとのコミュニケーションを意識することで、より多くの人に届きやすくなります。",
        "読書は知識を増やすだけでなく、視野を広げる最良の方法の一つです。特に自己啓発書やビジネス書、小説など、幅広いジャンルを読むことで、新しい考え方やアイデアを得ることができます。",
        "旅行は新しい発見とインスピレーションを与えてくれる最高の経験です。異なる文化に触れ、新しい景色を見ることで、日常では得られない気づきが生まれ、心が豊かになります。",
        "最新のAI技術を活用すれば、日常の仕事がもっと効率的になります。例えば、AIを使ったスケジュール管理やデータ分析を取り入れることで、作業時間を短縮し、よりクリエイティブな仕事に集中できます。",
        "デスク環境を整えるだけで、集中力と生産性が大幅にアップします。モニターの高さ、椅子の座り心地、照明の明るさを調整し、快適な作業スペースを作ることで、長時間の仕事でも疲れにくくなります。",
        "目標を明確に持つことで、行動が変わり、結果がついてきます。まずは小さな目標を設定し、それをクリアしていくことで、大きな目標も達成しやすくなります。習慣化が成功への鍵となるでしょう。",
        "時間管理のコツは、やるべきことを優先順位ごとに整理することです。TODOリストを作成し、最も重要なタスクから取り組むことで、効率的に作業を進めることができます。",
        "コーヒーの種類を知ることで、より豊かなコーヒーライフを楽しめます。エスプレッソ、カプチーノ、ラテなど、豆の選び方や抽出方法を工夫することで、味わいが大きく変わるのが魅力です。",
        "週末に自然と触れ合うことで、心がリフレッシュされます。都市の喧騒を離れ、公園や山、海でリラックスすることで、ストレスを軽減し、翌週の仕事や勉強に向けてリフレッシュできます。",
        "プログラミングは最初は難しいですが、習慣化すれば楽しくなります。簡単なプロジェクトから始め、毎日少しずつコードを書くことで、スキルが向上し、応用力もついてきます。",
        "メタバースが今後のインターネットの形を大きく変えていきます。バーチャル空間での交流や仕事、学習がより一般的になり、リアルとデジタルが融合した新しい体験が可能になるでしょう。",
        "ストレスを減らすためには、適度な運動とリラックスする時間が必要です。運動によってエンドルフィンが分泌され、気分が向上し、リラックスすることで心身のバランスが整います。",
        "本を読む習慣がある人は、人生の選択肢が増えると言われています。知識が増えることで、新しい視点を持つことができ、問題解決能力や創造力が向上します。",
        "副業を始める前に、まずは自分の得意なことをリストアップしましょう。趣味や経験を活かせる仕事を選ぶことで、楽しく続けられ、本業との両立もしやすくなります。",
        "睡眠の質を改善することで、翌日のパフォーマンスが向上します。就寝前のスマホ使用を控え、リラックスできる環境を整えることで、深い眠りにつきやすくなります。",
        "小さな挑戦を積み重ねることで、大きな目標も達成できるようになります。一歩ずつ前進することで、モチベーションを維持しながら、確実に成長することができます。"
    ]

    ## タグの候補である50個を設定しておき、タグの作成時にランダムで選んで作成する
    TAG_WORD = [
        "りんご", "ねこ", "太陽", "風", "未来", "冒険", "希望", "笑顔", "空", "花",
        "夢", "旅", "音楽", "映画", "友情", "光", "自然", "自由", "青春", "星",
        "海", "山", "心", "愛", "情熱", "桜", "雨", "風景", "宇宙", "絆",
        "努力", "幸せ", "創造", "芸術", "スポーツ", "美", "楽園", "知識", "学び", "読書",
        "挑戦", "感動", "冒険", "伝説", "成長", "夢中", "時間", "平和", "信念", "笑い"
    ]