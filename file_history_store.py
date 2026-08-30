"""
对话历史记录存储

使用内存字典保存每个 session 的历史消息。
"""

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage


# 保存所有用户的历史记录
# {
#     "user_001": [
#         HumanMessage(...),
#         AIMessage(...),
#         ...
#     ]
# }
store = {}


class InMemoryHistory(BaseChatMessageHistory):
    """基于内存的对话历史记录"""

    def __init__(self):
        self.messages = []

    def add_message(self, message):
        self.messages.append(message)

    def clear(self):
        self.messages = []


def get_history(session_id: str) -> BaseChatMessageHistory:
    """根据 session_id 获取历史记录"""

    if session_id not in store:
        store[session_id] = InMemoryHistory()

    return store[session_id]


def clear_history(session_id: str):
    """清空指定 session 的历史记录"""

    if session_id in store:
        store[session_id].clear()


def get_history_messages(session_id: str):
    """获取指定 session 的全部历史消息"""

    if session_id not in store:
        return []

    return store[session_id].messages