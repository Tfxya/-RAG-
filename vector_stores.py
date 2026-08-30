"""
向量数据库服务

职责：
1. 创建 / 连接 Chroma 向量数据库
2. 添加文档
3. 执行相似度检索
4. 获取知识库数量
5. 清空知识库

这里不负责：
- 文件上传
- MD5 去重
- Streamlit 页面
- API Key 管理
"""

from typing import List

from langchain_core.documents import Document
from langchain_chroma import Chroma

import config_data as config


class VectorStoreService:
    """Chroma 向量数据库服务"""

    def __init__(self, embedding):
        """
        初始化向量数据库。

        Args:
            embedding:
                LangChain Embedding 对象，
                例如 GLMEmbeddings()
        """

        self.embedding = embedding

        self.vector_store = Chroma(
            collection_name=config.collection_name,
            embedding_function=self.embedding,
            persist_directory=config.persist_directory,
        )

    def add_documents(self, documents: List[Document]):
        """
        将 Documents 添加到向量数据库。

        Args:
            documents: LangChain Document 列表
        """

        if not documents:
            return

        self.vector_store.add_documents(documents)

    def add_texts(self, texts: List[str], metadatas=None):
        """
        将文本直接添加到向量数据库。

        Args:
            texts: 文本列表
            metadatas: 每段文本对应的 metadata
        """

        if not texts:
            return

        self.vector_store.add_texts(
            texts=texts,
            metadatas=metadatas,
        )

    def get_retriever(self):
        """
        获取 LangChain Retriever。

        用于 RAG 检索。
        """

        return self.vector_store.as_retriever(
            search_kwargs={
                "k": config.similarity_threshold
            }
        )

    def similarity_search(self, query: str):
        """
        根据问题进行相似度检索。
        """

        return self.vector_store.similarity_search(
            query,
            k=config.similarity_threshold,
        )

    def count(self) -> int:
        """
        获取当前知识库中的向量数量。
        """

        return self.vector_store._collection.count()

    def get_all(self):
        """
        获取知识库中的全部数据。

        主要用于调试和管理页面。
        """

        return self.vector_store.get()

    def clear(self):
        """
        清空当前 Chroma collection。

        注意：
        这是危险操作。
        会删除整个知识库 collection 中的数据。
        """

        self.vector_store.delete_collection()

        # 重新创建 collection
        self.vector_store = Chroma(
            collection_name=config.collection_name,
            embedding_function=self.embedding,
            persist_directory=config.persist_directory,
        )