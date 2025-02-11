import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        print(f"WebSocket connected to room: {self.room_group_name}")
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )
        print(f"WebSocket disconnected from room: {self.room_group_name}")

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            # Check if the 'message' key exists in the received data
            if "message" in text_data_json:
                message = text_data_json["message"]
                print(f"Received message: {message}")

                # Send message to room group
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {"type": "chat.message", "message": message},
                )
                # Send a response back to the WebSocket
                self.chat_message({"message": "from backend"})
            else:
                print("Error: Message field is missing in the received data.")
                self.send(
                    text_data=json.dumps(
                        {"error": "Message field is required"}
                    )
                )

        except json.JSONDecodeError as e:
            print(f"Error decoding message: {e}")
            self.send(text_data=json.dumps({"error": "Invalid JSON format"}))
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.send(
                text_data=json.dumps({"error": "An unexpected error occurred"})
            )

    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))
