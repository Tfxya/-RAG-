import os

from dotenv import load_dotenv
from openai import OpenAI

from langchain_core.runnables import RunnableLambda


load_dotenv()

ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")

if not ZHIPUAI_API_KEY:
    raise ValueError(
        "没有找到 ZHIPUAI_API_KEY，请检查项目根目录下的 .env 文件"
    )


client = OpenAI(
    api_key=ZHIPUAI_API_KEY,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)


class GLMEmbeddings:
    """
    智谱 embedding-3 的 LangChain Embedding 适配器
    """

    def __init__(self, model="embedding-3"):
        self.model = model

    def embed_documents(self, texts):
        response = client.embeddings.create(
            model=self.model,
            input=texts
        )

        return [item.embedding for item in response.data]

    def embed_query(self, text):
        response = client.embeddings.create(
            model=self.model,
            input=text
        )

        return response.data[0].embedding


def glm_chat(prompt):
    """
    调用 GLM-4.5
    """

    if hasattr(prompt, "to_messages"):
        messages = []

        for message in prompt.to_messages():

            role = message.type

            # LangChain 的 system/human/ai
            # 转换成 OpenAI 格式
            if role == "human":
                role = "user"
            elif role == "ai":
                role = "assistant"

            messages.append({
                "role": role,
                "content": message.content
            })

    else:
        messages = [
            {
                "role": "user",
                "content": str(prompt)
            }
        ]

    response = client.chat.completions.create(
        model="glm-4.5",
        messages=messages
    )

    return response.choices[0].message.content


# 把普通 Python 函数包装成 LangChain Runnable
GLMChat = RunnableLambda(glm_chat)