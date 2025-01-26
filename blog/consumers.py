import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Message, Conversation
from django.core.exceptions import ValidationError
from django.db.models import Q
from mysite.models.account_models import User


class ChatConsumer(AsyncWebsocketConsumer):
    # WebSocket接続が確立された
    async def connect(self):
        # チャットルームの名前を取得
        print("Websocket：", self.scope)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        print("self.room_name : ", self.room_name)
        print("self.scope['user'] : ", self.scope['user'])

        # グループに参加
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    # WebSocket接続が切断された
    async def disconnect(self, close_code):
        # グループから退出
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # WebSocketからのメッセージを受け取る
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', None)
        image = text_data_json.get('image', None)
        partner_id = text_data_json.get('partner_id')

        # メッセージか画像がなかったらエラーを吐かせる
        if not message and not image:
            await self.send_error("メッセージの送信に失敗しました。")
            return

        conversation = await self.get_conversation(self.room_name)
        request_user_id, partner_data = await self.get_request_user_and_partner(self.scope['user'], partner_id)

        if partner_data is None:
            await self.send_error("パートナーが存在しません。")
            return

        # メッセージをデータベースに保存
        try:
            await self.save_message_to_db(conversation, message, image)
        except ValidationError as e:
            await self.send_error(str(e))
            return

        send_content = {
            "message": message,
            "request_user_id": request_user_id,
            "is_partner": partner_data.is_partner,
            "partner_data": {
                "id": partner_data.id,
                "username": partner_data.username,
                "profile_img": partner_data.profile_img,
            },
        }

        # グループにメッセージを送信
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'send_content': send_content,
            }
        )

    # エラーメッセージをWebSocketに送信
    async def send_error(self, error_message):
        await self.send(text_data=json.dumps({
            'error': error_message
        }))

    # グループからのメッセージをWebSocketに送信
    async def chat_message(self, event):
        message = event['send_content']['message']
        request_user_id = event['send_content']['request_user_id']
        is_partner = event['send_content']['is_partner']
        partner_data = event['send_content']['partner_data']

        send_content = {
            "message": message,
            "request_user_id": request_user_id,
            "is_partner": is_partner,
            "partner_data": {
                "id": partner_data['id'],
                "username": partner_data['username'],
                "profile_img": partner_data['profile_img'],
            },
        }

        # WebSocketにメッセージを送信
        await self.send(text_data=json.dumps(send_content))

    # メッセージをデータベースに保存する処理
    @database_sync_to_async
    def save_message_to_db(self, conversation, message, image):
        # Messageモデルに新しいメッセージを保存
        message = Message(
            conversation=conversation,
            sender=self.scope['user'],  # ユーザー情報を含める
            text=message,
            created_at=timezone.now()
        )

        # ! 画像があれば保存する
        if image:
            # TODO: 画像があった際の処理（MessageAttachmentに保存する）
            pass

        # バリデーションの実行
        message.full_clean()

        message.save()

    # 会話を取得する処理（DBにアクセスする場合は「@database_sync_to_async」を使用する）
    @database_sync_to_async
    def get_conversation(self, conversation_id):
        # room_nameからConversationを取得するロジックを実装
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            print(f"DMのRoomが見つかりませんでした。RoomId：{conversation_id}")
            return conversation_id

        return conversation

    ## 送信ユーザーがパートナーかを確認する
    @database_sync_to_async
    def get_request_user_and_partner(self, request_user_email, partner_id):
        try:
            request_user = User.objects.get(email=request_user_email)
            partner = User.objects.get(id=partner_id)
            is_partner = request_user.id == partner_id
            print(f"メッセージ送信ユーザー：{request_user.id}, パートナー：{partner_id}")
            partner.is_partner = is_partner
            partner.username = partner.profile.username
            partner.profile_img = partner.profile.image.url
            return request_user.id, partner
        except User.DoesNotExist:
            print(f"WebSocektでリクエストしたユーザーが見つかりませんでした。リクエストEmail：{request_user_email}")
        return None