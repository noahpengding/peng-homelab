from openai import OpenAI, Model
import openai
from app.config import config
from app.log import output_log
import weakref

class OpenAIHandler:
    _instances = weakref.WeakValueDictionary()
    
    def __new__(cls, user_id):
        if user_id in cls._instances:
            return cls._instances[user_id]
        instance = super(OpenAIHandler, cls).__new__(cls)
        cls._instances[user_id] = instance
        return instance
    
    def __init__(self, user_id):
        if not hasattr(self, "initialized"):
            self.user_id = user_id
            self.client = OpenAI(
                api_key=config.openai_api_key,
                organization=config.openai_organization_id, 
                project=config.openai_project_id)
            self.start_prompt = config.openai_start_prompt
            self.conversation = [{"role": "system", "content": self.start_prompt}]
            self.file_ids = []
            self.model_id = "gpt-4o-mini"
            self.image_model_id = "dall-e-3"
            self.max_completion_tokens = 3000
            self.temperature = 0.5
            self.frequency_penalty = 0.2
            self.presence_penalty = 0.0
            self.initialized = True

    def list_models(self):
        response = self.client.models.list()
        models = [model.id for model in response.data]
        return models
    
    def list_parameters(self):
        return {
            "model_id": self.model_id,
            "max_completion_tokens": self.max_completion_tokens,
            "temperature": self.temperature,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty
        }
    
    def set_parameters(self, name, value):
        if name == "model_id" or name == "model":
            self.model_id = str(value)
        elif name == "image_model_id" or name == "image_model":
            self.image_model_id = str(value)
        elif name == "max_completion_tokens":
            self.max_completion_tokens = int(value)
        elif name == "temperature":
            self.temperature = float(value)
        elif name == "frequency_penalty":
            self.frequency_penalty = float(value)
        elif name == "presence_penalty":
            self.presence_penalty = float(value)
        elif name == "prompt":
            self.start_prompt = str(value)
            self.conversation = [{"role": "system", "content": self.start_prompt}]
        elif name == "conversation":
            self.conversation = list(value)
        else:
            output_log(f"Invalid parameter: {name}", "error")

    def create_chat_completion(self, messages):
        self.conversation.append({"role": "user", "content": messages})
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=self.conversation,
            max_completion_tokens=self.max_completion_tokens,
            temperature=self.temperature,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty
        )
        generate_message = response.choices[0].message.content
        self.conversation.append({"role": "assistant", "content": generate_message})
        return response.choices[0].message.content

    def __file_delete(self):
        for file_id in self.file_ids:
            self.client.files.delete(file_id)
    
    def image_generation(self, messages, size="1024x1024"):
        response = self.client.images.generate(
            model=self.image_model_id,
            prompt=messages,
            size=size,
            n=1
        )
        return response.data[0].url
    
    def image_variance(self, picture, size="1024x1024"):
        response = self.client.images.create_variation(
            model=self.image_model_id,
            image=picture,
            size=size,
            n=1
        )
        return response.data[0].url
    
    def image_edit(self, picture, prompt, mask=None, size="1024x1024"):
        response = self.client.images.edit(
            model=self.image_model_id,
            image=picture,
            mask=mask,
            prompt=prompt,
            size=size,
            n=1
        )
        return response.data[0].url
    
    def get_coversions(self):
        output_log("Getting conversions", "debug")
        return self.conversation

    def end_conversation(self):
        self.conversation = [{"role": "system", "content": self.start_prompt}]
        self.__file_delete()
        self.file_ids = []

    def get_usage(self):
        r = openai.api_requestor.APIRequestor()
        resp = r.request("get", "/dashboard/billing/usage?end_date=2024-09-28&start_date=2024-09-21", self.client.api_key)
        resp_object = resp[0]
        return resp_object.data
