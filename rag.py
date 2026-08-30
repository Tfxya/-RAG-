from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from file_history_store import get_history
from vector_stores import VectorStoreService
from glm_models import GLMEmbeddings, GLMChat

import config_data as config


def print_prompt(prompt):
    """
    打印最终发送给大模型的 Prompt。
    方便调试 RAG 检索结果和历史对话是否正确注入。
    """

    print("=" * 20)
    print(prompt.to_string())
    print("=" * 20)

    return prompt


class RagService:
    """
    企业知识库 RAG 服务。

    功能：

    1. 从 Chroma 向量数据库检索知识
    2. 将检索结果加入 Prompt
    3. 维护用户历史对话
    4. 支持历史对话查询
    5. 调用 GLM 大模型
    6. 支持 invoke / stream
    """

    def __init__(self):

        # ==================================================
        # 1. 初始化向量数据库
        # ==================================================

        self.vector_service = VectorStoreService(
            embedding=GLMEmbeddings()
        )

        # ==================================================
        # 2. 创建 Prompt
        # ==================================================

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
你是一个企业知识库智能服务。

请严格遵守以下规则：

【一、知识库问题】

1. 用户询问企业业务、企业宗旨、公司介绍、产业、产品等事实信息时，
   优先根据【知识库参考资料】回答。

2. 如果知识库中有明确答案，直接根据资料回答，
   不要说“无法得知”。

3. 不要编造知识库中不存在的信息。

4. 如果知识库中确实没有相关信息，请明确告诉用户：

“知识库中没有找到相关信息”。

【二、历史对话问题】

5. 如果用户询问以下内容：

   - 我之前问了什么
   - 我刚才问了什么
   - 输出历史记录
   - 输出所有历史对话
   - 输出所有历史问答
   - 我们之前聊了什么
   - 总结之前的对话
   - 输出所有历史对话信息

   这类问题属于【历史对话查询】。

   应该直接根据【历史对话记录】回答，
   不要根据知识库参考资料回答。

6. 如果用户要求：

“输出所有历史对话信息”

请按照时间顺序列出历史记录。

格式：

1. 用户：xxx
   助手：xxx

2. 用户：xxx
   助手：xxx

不要遗漏历史记录中的问答。

7. 历史对话中的内容只能作为历史信息使用。

   不要把历史对话中的用户陈述自动当成企业知识库事实。

【三、知识库与历史记录的优先级】

8. 企业事实问题：

   优先使用知识库。

9. 历史记录问题：

   优先使用历史对话记录。

10. 如果知识库和历史记录都无法回答，
    不要编造答案。

【四、回答风格】

11. 回答简洁、准确、专业。

12. 不需要重复说明“根据参考资料”。

【知识库参考资料】

{context}
""",
                ),
                MessagesPlaceholder(variable_name="history"),
                (
                    "user",
                    """
请回答当前用户的问题：

{input}
""",
                ),
            ]
        )

        # ==================================================
        # 3. 初始化 GLM
        # ==================================================

        # glm_models.py 中：
        #
        # GLMChat = RunnableLambda(glm_chat)
        #
        # 因此 GLMChat 本身就是 Runnable。
        #
        # 不能写：
        #
        # GLMChat(...)
        #
        # 必须直接使用 GLMChat。

        self.chat_model = GLMChat

        # ==================================================
        # 4. 创建 RAG Chain
        # ==================================================

        self.chain = self.__get_chain()

    def __get_chain(self):
        """
        创建 RAG 执行链。

        RunnableWithMessageHistory 会自动向 Chain 输入：

        {
            "input": 用户问题,
            "history": 历史消息
        }

        所以这里需要同时把：

        input
        history
        context

        传递给 Prompt。
        """

        # ==================================================
        # 1. 获取 Retriever
        # ==================================================

        retriever = self.vector_service.get_retriever()

        # ==================================================
        # 2. 格式化知识库文档
        # ==================================================

        def format_document(docs: list[Document]) -> str:
            """
            将 Retriever 返回的 Document 转换成字符串。
            """

            if not docs:
                return "无相关参考资料"

            formatted_str = ""

            for doc in docs:
                formatted_str += (
                    f"文档片段：{doc.page_content}\n"
                    f"文档元数据：{doc.metadata}\n\n"
                )

            return formatted_str

        # ==================================================
        # 3. 从 Chain 输入中获取用户问题
        # ==================================================

        def get_user_input(value: dict) -> str:
            """
            从：

            {
                "input": "...",
                "history": [...]
            }

            中提取用户当前问题。
            """

            return value["input"]

        # ==================================================
        # 4. 创建 RAG Chain
        # ==================================================

        chain = (
            {
                # 当前用户问题
                "input": RunnableLambda(
                    lambda value: value["input"]
                ),

                # 知识库检索结果
                "context": (
                    RunnableLambda(get_user_input)
                    | retriever
                    | format_document
                ),

                # 历史对话
                #
                # RunnableWithMessageHistory 会自动注入 history
                # 这里直接把它传递给 Prompt。
                "history": RunnableLambda(
                    lambda value: value["history"]
                ),
            }
            | self.prompt_template
            | print_prompt
            | self.chat_model
            | StrOutputParser()
        )

        # ==================================================
        # 5. 添加历史对话能力
        # ==================================================

        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        return conversation_chain


# ==========================================================
# 测试 RAG
# ==========================================================

if __name__ == "__main__":

    print("\n开始测试 RAG...\n")

    # ======================================================
    # Session
    # ======================================================

    session_config = {
        "configurable": {
            "session_id": "user_001",
        }
    }

    # ======================================================
    # 创建 RAG 服务
    # ======================================================

    service = RagService()

    # ======================================================
    # 测试问题
    # ======================================================

    question = "企业宗旨是什么？"

    print(f"用户：{question}\n")

    # ======================================================
    # 调用 RAG
    # ======================================================

    res = service.chain.invoke(
        {
            "input": question
        },
        session_config,
    )

    # ======================================================
    # 输出结果
    # ======================================================

    print("\n最终回答：")
    print(res)