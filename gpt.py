from openai import OpenAI, _types as OpenAI_types
import os

API_KEY = os.getenv("GPT_API_KEY")

class GPT:
    def __init__(self,  seed: int = None):
        self.api_key = API_KEY
        self.client = OpenAI(api_key=self.api_key)
        self.seed = seed

    def request_chat(self, user_input):

        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_input,
                }
            ],
            model="gpt-3.5-turbo",
            seed=self.seed
        )
        return chat_completion.choices[0].message.content