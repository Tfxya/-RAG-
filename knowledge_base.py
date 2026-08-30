"""
知识库业务服务

职责：
1. 接收上传的文本
2. MD5 去重
3. 文本切分
4. 构造 Document
5. 写入向量数据库

不负责：
- Streamlit 页面
- Chroma 底层实现
- GLM API 调用
"""

import hashlib
import os
from datetime import datetime
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config_data as config
from vector_stores import VectorStoreService
from glm_models import GLMEmbeddings


class KnowledgeBaseService:
    """知识库业务服务"""

    def __init__(self):
        # 创建 Chroma 数据目录
        os.makedirs(
            config.persist_directory,
            exist_ok=True
        )

        # 初始化向量数据库
        self.vector_store = VectorStoreService(
            embedding=GLMEmbeddings()
        )

        # 初始化文本切分器
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            length_function=len,
        )

        # MD5 文件
        self.md5_path = config.md5_path

        # 确保 MD5 文件存在
        self._ensure_md5_file()

    # =========================================================
    # MD5
    # =========================================================

    def _ensure_md5_file(self):
        """
        确保 MD5 记录文件存在。
        """

        if not os.path.exists(self.md5_path):
            with open(
                self.md5_path,
                "w",
                encoding="utf-8"
            ):
                pass

    def get_md5(self, text: str) -> str:
        """
        计算文本 MD5。
        """

        return hashlib.md5(
            text.encode("utf-8")
        ).hexdigest()

    def exists(self, md5: str) -> bool:
        """
        判断 MD5 是否已经存在。
        """

        if not os.path.exists(self.md5_path):
            return False

        with open(
            self.md5_path,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:
                if line.strip() == md5:
                    return True

        return False

    def _save_md5(self, md5: str):
        """
        保存 MD5。
        """

        with open(
            self.md5_path,
            "a",
            encoding="utf-8"
        ) as f:

            f.write(md5 + "\n")

    # =========================================================
    # 文本处理
    # =========================================================

    def split_text(self, text: str) -> List[str]:
        """
        将文本切分成多个 chunk。
        """

        if not text.strip():
            return []

        if len(text) <= config.max_spliter_char_number:
            return [text]

        return self.splitter.split_text(text)

    def create_documents(
        self,
        text: str,
        filename: str,
    ) -> List[Document]:
        """
        将文本转换成 LangChain Document。
        """

        chunks = self.split_text(text)

        if not chunks:
            return []

        create_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        documents = []

        for index, chunk in enumerate(chunks):

            metadata = {
                "source": filename,
                "chunk_index": index,
                "create_time": create_time,
            }

            documents.append(
                Document(
                    page_content=chunk,
                    metadata=metadata,
                )
            )

        return documents

    # =========================================================
    # 上传知识库
    # =========================================================

    def upload_by_str(
        self,
        data: str,
        filename: str,
    ) -> str:
        """
        将文本加入知识库。

        Returns:
            操作结果字符串
        """

        # -----------------------------------------
        # 1. 检查内容
        # -----------------------------------------

        if not data or not data.strip():
            return "[Error] 文件内容为空"

        # -----------------------------------------
        # 2. 计算 MD5
        # -----------------------------------------

        md5 = self.get_md5(data)

        # -----------------------------------------
        # 3. 判断是否重复
        # -----------------------------------------

        if self.exists(md5):
            return "[Repeat] 内容已经存在知识库"

        # -----------------------------------------
        # 4. 创建 Documents
        # -----------------------------------------

        documents = self.create_documents(
            text=data,
            filename=filename,
        )

        if not documents:
            return "[Error] 文件没有有效内容"

        # -----------------------------------------
        # 5. 写入向量数据库
        # -----------------------------------------

        try:

            self.vector_store.add_documents(
                documents
            )

        except Exception as e:

            return (
                "[Error] 写入知识库失败："
                f"{type(e).__name__}: {e}"
            )

        # -----------------------------------------
        # 6. 保存 MD5
        # -----------------------------------------

        self._save_md5(md5)

        return (
            "[Success] 内容已经成功载入知识库\n"
            f"文件：{filename}\n"
            f"切分数量：{len(documents)}"
        )

    # =========================================================
    # 知识库管理
    # =========================================================

    def count(self) -> int:
        """
        获取知识库当前 chunk 数量。
        """

        return self.vector_store.count()

    def get_all(self):
        """
        获取知识库全部内容。
        """

        return self.vector_store.get_all()

    def clear(self):
        """
        清空知识库。
        """

        self.vector_store.clear()

        # 同时清空 MD5
        with open(
            self.md5_path,
            "w",
            encoding="utf-8"
        ):
            pass

    # =========================================================
    # 测试
    # =========================================================


if __name__ == "__main__":

    service = KnowledgeBaseService()

    text = """
    星辰科技主要从事人工智能软件开发。

    公司的核心业务是大语言模型应用、
    RAG知识库和智能服务系统。

    企业宗旨是用人工智能技术帮助企业提高工作效率。
    """

    result = service.upload_by_str(
        text,
        "test.txt"
    )

    print(result)

    print(
        "当前知识库数量：",
        service.count()
    )