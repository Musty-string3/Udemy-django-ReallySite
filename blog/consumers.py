import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Message, Conversation  # Messageモデルをインポート

class ChatConsumer(AsyncWebsocketConsumer):
    # WebSocket接続が確立された
    async def connect(self):
        # チャットルームの名前を取得
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
        message = text_data_json['message']

        # DMルームを取得する
        # TODO: user1とuser2を取得する
        user1 = self.scope['user']
        user2 = self.room_name
        conversation = await self.get_conversation(user1, user2)

        # メッセージをデータベースに保存
        await self.save_message_to_db(conversation, message)

        # グループにメッセージを送信
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # グループからのメッセージをWebSocketに送信
    async def chat_message(self, event):
        message = event['message']

        # WebSocketにメッセージを送信
        await self.send(text_data=json.dumps({
            'message': message
        }))

    # メッセージをデータベースに保存する処理
    @database_sync_to_async
    def save_message_to_db(self, conversation, message):
        # Messageモデルに新しいメッセージを保存
        Message.objects.create(
            conversation=conversation,
            sender=self.scope['user'],  # ユーザー情報を含める
            text=message,
            created_at=timezone.now()
        )

    # 会話を取得する処理
    @database_sync_to_async
    def get_conversation(self, user1, user2):
        # room_nameからConversationを取得するロジックを実装
        return Conversation.objects.get(user1=user1, user2=user2)