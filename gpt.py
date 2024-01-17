from openai import OpenAI, _types as OpenAI_types


class GPT:
    def __init__(self,  seed: int = None):
        self.api_key = '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'
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