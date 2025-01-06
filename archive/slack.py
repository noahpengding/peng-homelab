from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from app.config import config
from app.openai_api import OpenAIHandler
from app.minio_storage import MinioStorage
from app.read_file import FileReader
from app.log import output_log
from app.message_format import format_message
import time
import json

class Slack:
    def __init__(self):
        self.token = config.slack_token
        self.app_token = config.slack_socket_token
        self.client = WebClient(token=self.token)
        self.socket_client = SocketModeClient(app_token=self.app_token, web_client=self.client)
        self.socket_client.socket_mode_request_listeners.append(self.handle_socket_mode_request)
        self.openai = OpenAIHandler("USLACKBOT")
        self.minio_storage = MinioStorage()

    def send_message(self, text):
        try:
            text = str(format_message(text))
            response = self.client.chat_postMessage(
                channel=config.channel_id,
                text=text
            )
            output_log(response, "debug")
        except SlackApiError as e:
            output_log(e.response["error"], "error")

    def send_message_with_channel(self, channel, text):
        try:
            text = str(format_message(text))
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                mrkdwn=True
            )
            output_log(response, "debug")
        except SlackApiError as e:
            output_log(e.response["error"], "error")
    
    def send_local_image(self, channel, image_path, message):
        try:
            response = self.client.files_upload(
                channels=channel,
                file=image_path,
                initial_comment=message
            )
            output_log(response, "debug")
        except SlackApiError as e:
            output_log(e.response["error"], "error")
    
    def send_image_with_channel(self, channel, image, message):
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message,
                blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                },
                {
                    "type": "image",
                    "image_url": image,
                    "alt_text": message
                }
                ]
            )
            assert response["message"]["text"] == message
        except SlackApiError as e:
            assert e.response["error"]

    def end_conversation(self, chat_name, bucket_name=config.minio_default_bucket):
        conversation = self.openai.get_coversions()
        date = time.strftime("%Y%m%d-%H%M", time.localtime())
        if len(conversation) < 2:
            return
        if chat_name == "":
            topic = conversation[1].get("content")
            topic = topic.replace(" ", "_")
            topic = topic[:20] if len(topic) > 20 else topic
        else:
            topic = chat_name
        file_name = f"{date}_{topic}.json"
        response = "Conversation ended. File not saved."
        if chat_name.lower() != "not save" and chat_name.lower() != "no save" and chat_name.lower() != "don't save":
            with open(file_name, "w") as f:
                json.dump(conversation, f)
            self.minio_storage.file_upload(bucket_name, file_name, f"Chat/{file_name}", "application/json")
            response = f"Conversation ended. File uploaded to {bucket_name}/{file_name}."
        self.openai.end_conversation()
        return response

    def list_conversations(self, bucket_name=config.minio_default_bucket, folder_name="Chat"):
        output_log(f"Listing conversations in {bucket_name}/{folder_name}", "debug")
        conversation = self.minio_storage.file_list_name(bucket_name, folder_name)
        output_log(f"Conversations: {conversation}", "debug")
        return conversation

    def share_file(self, file_path):
        m = MinioStorage()
        bucket = file_path.split("://")[0]
        file_key = file_path.split("://")[1]
        output_log(f"{file_path}:{bucket};{file_key}", "debug")
        if not m.file_exists(bucket, file_key):
            self.send_message("File not found")
            return
        download_path = file_path.split("/")[-1]
        output_log(f"Downloading file to {download_path}", "debug")
        download = m.file_download(bucket, file_key, download_path)
        if not download:
            self.send_message(f"Failed to download file {file_path}")
            return
        r = FileReader()
        if not r.check_exists(download_path):
            self.send_message(f"Failed to read file {download_path}")
            return
        text = r.reader(download_path)
        output_log(f"File content: {text}", "debug")
        prompt = f"Here is a file content of {text}. Can you summarize it?"
        completion = self.openai.create_chat_completion(prompt)
        return completion

    def handle_message(self, event_data):
        user_name = event_data.get("user_name")
        text = event_data.get("text")
        channel = event_data.get("channel_id")
        if not user_name or user_name == "USLACKBOT" or not text:
            return
        self.openai = OpenAIHandler(user_name)
        self.send_message_with_channel(channel, f"{user_name}: {text}")
        response = ""
        command = text.lower().split()[0]
        text = ' '.join(text.split()[1:])
        output_log(f"Received message: {command}: {text}", "debug")
        if command == "share":
            response = self.share_file(text)
        elif command == "get":
            response = str(self.openai.get_coversions())
        elif command == "chat": 
            response = self.openai.create_chat_completion(text.strip())
        elif command == "end":
            response = self.end_conversation(text.strip())
        elif command == "list" or command == "ls":
            response = self.handle_chat_list_command(text.strip())
        elif command == "set":
            response = self.handle_chat_set_command(text.strip())
        elif command == "image":
            response = self.handle_image_command(text, channel)
        else:
            response = "No Valid Command"
        if response != "":
            self.send_message_with_channel(channel, response)
        else:
            self.send_message_with_channel(channel, "Next")

    def handle_chat_command(self, command, text):
        output_log(f"Handling chat command: {command}: {text}", "debug")
        if command == "end":
            return self.end_conversation(text)
        elif command == "list" or command == "ls":
            return self.handle_chat_list_command(text.strip())
        elif command == "set":
            return self.handle_chat_set_command(text.strip())
        return ""

    def handle_chat_list_command(self, text):
        output_log(f"Handling chat list command: {text}", "debug")
        if text in ["parameters", "parameter", "params", "param"]:
            return str(self.openai.list_parameters())
        elif text in ["models", "model"]:
            return str(self.openai.list_models())
        elif text in ["conversations", "conversation", "chat", "chats"]:
            return str(self.list_conversations())
        return "Invalid command. Available commands: parameters, models, or chats"

    def handle_chat_set_command(self, text):
        params = text.split("=")
        if len(params) < 2:
            return "Invalid command. Usage: chat set <parameter>=<value>"
        if params[0] in ["chat", "conversation"]:
            location = params[1]
            bucket_name = location.split("://")[0] if len(location.split("://")) > 1 else config.minio_default_bucket
            file_name = location.split("://")[1] if len(location.split("://")) > 1 else location
            file_name = f"Chat/{file_name}" if not len(file_name.split("/")) > 1 else file_name
            self.minio_storage.file_download(bucket_name, file_name, "temp.json")
            with open("temp.json", "rb") as f:
                params[1] = json.load(f)
            params[0] = "conversation"
        self.openai.set_parameters(params[0], params[1])
        params[1] = params[1][:20] if len(params[1]) > 30 else params[1]
        return f"Parameters set. {params[0]}={params[1]}"

    def handle_image_command(self, input_text, channel):
        text = input_text[6:].strip()
        image = self.openai.image_generation(text)
        self.send_image_with_channel(channel, image, text)
        return ""

    def handle_socket_mode_request(self, client: SocketModeClient, req: SocketModeRequest):
        output_log(f"Received request: {req.type}", "info")
        if req.type == "events_api" or req.type == "slash_commands":
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)
            event_data = req.payload
            output_log(f"Received event: {event_data}", "debug")
            self.handle_message(event_data)

    def start(self):
        output_log("Starting Slack client", "info")
        self.socket_client.connect()
