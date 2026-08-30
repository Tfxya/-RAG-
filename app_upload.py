"""
知识库管理页面
功能：
1. TXT 文件上传
2. 文件信息展示
3. 文件内容预览
4. 写入知识库
5. 知识库统计
6. 清空知识库
"""

import streamlit as st

from knowledge_base import KnowledgeBaseService


# =========================================================
# 页面配置
# =========================================================

st.set_page_config(
    page_title="知识库管理",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# CSS：现代简洁风格（极简浅色 · 靛蓝 Indigo）
# =========================================================

st.markdown(
    """
    <style>

    /* ================================
       全局
    ================================= */

    .stApp {
        background: #f5f6f8;
        color: #16181d;
        -webkit-font-smoothing: antialiased;
    }

    .stApp,
    .stApp div, .stApp p, .stApp span, .stApp li,
    .stApp h1, .stApp h2, .stApp h3,
    .stApp label, .stApp button, .stApp input, .stApp textarea {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                     "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                     "Helvetica Neue", Arial, sans-serif;
    }

    .stApp code, .stApp pre {
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1100px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }


    /* ================================
       滚动条 / 选中文字
    ================================= */

    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #d8dbe2; border-radius: 8px; }
    ::-webkit-scrollbar-thumb:hover { background: #c3c7d0; }

    ::selection { background: #c7d2fe; }


    /* ================================
       页头
    ================================= */

    .page-header {
        margin-bottom: 2rem;
    }

    .header-row {
        display: flex;
        align-items: flex-start;
        gap: 16px;
    }

    .header-badge {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        background: #eef2ff;
        border: 1px solid #e0e7ff;
    }

    .page-title {
        font-size: 1.9rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #16181d;
        line-height: 1.25;
    }

    .page-description {
        font-size: 0.95rem;
        color: #6b7280;
        margin-top: 4px;
    }


    /* ================================
       统计卡片
    ================================= */

    .card {
        background: #ffffff;
        border: 1px solid #e6e8ee;
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        height: 100%;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    }

    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(16, 24, 40, 0.07);
        border-color: #dfe3ec;
    }

    .card-top {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
    }

    .card-icon {
        width: 34px;
        height: 34px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        background: #eef2ff;
        border: 1px solid #e0e7ff;
    }

    .card-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #6b7280;
        letter-spacing: 0.3px;
    }

    .card-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #16181d;
        letter-spacing: -0.5px;
        font-variant-numeric: tabular-nums;
    }

    .card-description {
        font-size: 0.78rem;
        color: #9aa1ac;
        margin-top: 5px;
    }


    /* ================================
       Section 标题
    ================================= */

    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #16181d;
        margin-top: 2.25rem;
        margin-bottom: 0.35rem;
        display: flex;
        align-items: center;
        gap: 9px;
    }

    .section-title::before {
        content: "";
        width: 4px;
        height: 16px;
        border-radius: 2px;
        background: linear-gradient(180deg, #6366f1, #4f46e5);
    }

    .section-description {
        color: #6b7280;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }


    /* ================================
       上传区域
    ================================= */

    [data-testid="stFileUploader"] {
        background: #ffffff;
        border: 1.5px dashed #d4d7de;
        border-radius: 16px;
        padding: 10px;
        transition: all 0.2s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #a5b4fc;
        background: #fdfdff;
    }

    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] section > div {
        background: transparent;
    }


    /* ================================
       文件信息卡
    ================================= */

    .file-info {
        display: flex;
        align-items: center;
        gap: 14px;
        background: #ffffff;
        border: 1px solid #e6e8ee;
        border-radius: 14px;
        padding: 16px 18px;
        margin-top: 1rem;
        margin-bottom: 6px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }

    .file-icon {
        width: 42px;
        height: 42px;
        border-radius: 11px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        background: #eef2ff;
        border: 1px solid #e0e7ff;
    }

    .file-name {
        font-size: 0.98rem;
        font-weight: 600;
        color: #16181d;
    }

    .file-meta {
        font-size: 0.82rem;
        color: #8a90a0;
        margin-top: 3px;
    }


    /* ================================
       按钮
    ================================= */

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        min-height: 42px;
        transition: all 0.18s ease;
    }

    .stButton > button[kind="primary"] {
        background: #4f46e5;
        border-color: #4f46e5;
        color: #ffffff;
        box-shadow: 0 1px 2px rgba(79, 70, 229, 0.35);
    }

    .stButton > button[kind="primary"]:hover {
        background: #4338ca;
        border-color: #4338ca;
        color: #ffffff;
    }

    .stButton > button[kind="primary"]:focus {
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.18);
    }

    .stButton > button[kind="secondary"]:hover {
        border-color: #c7d2fe;
        color: #4f46e5;
    }


    /* ================================
       折叠面板
    ================================= */

    details[data-testid="stExpander"],
    [data-testid="stExpander"] details {
        border: 1px solid #e6e8ee !important;
        border-radius: 12px !important;
        background: #ffffff;
        overflow: hidden;
    }

    details[data-testid="stExpander"] summary:hover,
    [data-testid="stExpander"] details summary:hover {
        background: #f7f8fa;
    }


    /* ================================
       提示条
    ================================= */

    [data-testid="stAlert"] {
        border-radius: 12px;
    }


    /* ================================
       页脚
    ================================= */

    [data-testid="stCaptionContainer"], .stCaption {
        color: #9aa1ac;
    }


    /* ================================
       隐藏 Streamlit 菜单
    ================================= */

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 初始化服务
# =========================================================

if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()

service = st.session_state["service"]


# =========================================================
# Header
# =========================================================

st.markdown(
    """
    <div class="page-header">
        <div class="header-row">
            <div class="header-badge">📚</div>
            <div>
                <div class="page-title">知识库管理</div>
                <div class="page-description">
                    上传企业文档，将内容转换为向量并加入知识库，为智能服务提供可靠的知识来源。
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Statistics
# =========================================================

count = service.count()

col1, col2, col3 = st.columns(3)


with col1:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-top">
                <div class="card-icon">🧩</div>
                <div class="card-title">知识片段</div>
            </div>
            <div class="card-value">{count}</div>
            <div class="card-description">当前知识库中的文本 Chunk</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col2:
    st.markdown(
        """
        <div class="card">
            <div class="card-top">
                <div class="card-icon">🗄️</div>
                <div class="card-title">向量数据库</div>
            </div>
            <div class="card-value">Chroma</div>
            <div class="card-description">本地持久化向量存储</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col3:
    st.markdown(
        """
        <div class="card">
            <div class="card-top">
                <div class="card-icon">⚡</div>
                <div class="card-title">Embedding</div>
            </div>
            <div class="card-value">GLM</div>
            <div class="card-description">智谱 Embedding 模型</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# Upload Section
# =========================================================

st.markdown(
    """
    <div class="section-title">上传文档</div>
    <div class="section-description">
        支持 TXT 文本文件，上传后系统会自动进行文本切分、向量化和知识库存储。
    </div>
    """,
    unsafe_allow_html=True,
)


uploaded_file = st.file_uploader(
    "选择 TXT 文件",
    type=["txt"],
    accept_multiple_files=False,
    label_visibility="collapsed",
)


# =========================================================
# File Processing
# =========================================================

if uploaded_file is not None:

    file_name = uploaded_file.name
    file_type = uploaded_file.type or "text/plain"
    file_size = uploaded_file.size / 1024

    # -----------------------------------------------------
    # 读取文件
    # -----------------------------------------------------

    file_bytes = uploaded_file.getvalue()

    try:

        text = file_bytes.decode("utf-8")

    except UnicodeDecodeError:

        try:

            text = file_bytes.decode("gbk")

        except UnicodeDecodeError:

            st.error(
                "无法识别文件编码，请将 TXT 文件保存为 UTF-8 编码后重新上传。"
            )

            st.stop()

    # -----------------------------------------------------
    # 文件信息
    # -----------------------------------------------------

    st.markdown(
        f"""
        <div class="file-info">
            <div class="file-icon">📄</div>
            <div>
                <div class="file-name">{file_name}</div>
                <div class="file-meta">
                    {file_type} · {file_size:.2f} KB · {len(text)} 个字符
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # 文件预览
    # -----------------------------------------------------

    with st.expander("查看文件内容"):

        st.text(text[:5000])

        if len(text) > 5000:

            st.caption(
                "仅显示前 5000 个字符。"
            )

    # -----------------------------------------------------
    # Upload Button
    # -----------------------------------------------------

    st.write("")

    if st.button(
        "加入知识库",
        type="primary",
        use_container_width=True,
    ):

        with st.spinner(
            "正在处理文档..."
        ):

            result = service.upload_by_str(
                data=text,
                filename=file_name,
            )

        if result.startswith("[Success]"):

            st.success(
                result
            )

            st.rerun()

        elif result.startswith("[Repeat]"):

            st.warning(
                result
            )

        else:

            st.error(
                result
            )


# =========================================================
# Knowledge Base Management
# =========================================================

st.markdown(
    """
    <div class="section-title">知识库管理</div>
    <div class="section-description">
        管理当前本地知识库。
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Clear Database
# ---------------------------------------------------------

with st.expander(
    "危险操作"
):

    st.warning(
        "清空知识库会删除当前 Chroma Collection 中的全部数据，"
        "同时清除 MD5 去重记录。此操作无法恢复。"
    )

    if "confirm_clear" not in st.session_state:
        st.session_state["confirm_clear"] = False

    if not st.session_state["confirm_clear"]:

        if st.button(
            "清空整个知识库",
            type="secondary",
        ):

            st.session_state["confirm_clear"] = True
            st.rerun()

    else:

        st.error(
            "确定要删除全部知识库数据吗？"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "确认删除",
                type="primary",
                use_container_width=True,
            ):

                try:

                    service.clear()

                    st.session_state[
                        "confirm_clear"
                    ] = False

                    st.success(
                        "知识库已清空。"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"清空失败：{e}"
                    )

        with col2:

            if st.button(
                "取消",
                use_container_width=True,
            ):

                st.session_state[
                    "confirm_clear"
                ] = False

                st.rerun()


# =========================================================
# Footer
# =========================================================

st.write("")

st.caption(
    "Knowledge Base · Chroma · GLM"
)
