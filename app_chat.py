import streamlit as st

from rag import RagService
import config_data as config
from file_history_store import clear_history


# ============================================================
# 页面配置
# ============================================================

st.set_page_config(
    page_title="企业智能服务",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS：现代简洁风格（极简浅色 · 靛蓝 Indigo）
# ============================================================

st.markdown(
    """
    <style>

    /* =========================
       全局
       ========================= */

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
        max-width: 820px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    /* 底部输入区与正文同宽居中 */
    [data-testid="stBottomBlockContainer"] {
        max-width: 820px;
        margin: 0 auto;
    }


    /* =========================
       滚动条 / 选中文字
       ========================= */

    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #d8dbe2; border-radius: 8px; }
    ::-webkit-scrollbar-thumb:hover { background: #c3c7d0; }

    ::selection { background: #c7d2fe; }


    /* =========================
       Sidebar
       ========================= */

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e8eaef;
    }

    section[data-testid="stSidebar"] > div {
        padding: 1.6rem 1.2rem;
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
    }

    .brand-badge {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        background: linear-gradient(135deg, #6366f1, #4f46e5 55%, #4338ca);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.28);
    }

    .brand-name {
        font-size: 16px;
        font-weight: 700;
        color: #16181d;
        letter-spacing: -0.2px;
        line-height: 1.3;
    }

    .brand-sub {
        font-size: 12px;
        color: #9aa1ac;
        margin-top: 2px;
    }

    .sidebar-divider {
        height: 1px;
        background: #edeff3;
        margin: 18px 0;
    }

    .sidebar-label {
        font-size: 11px;
        font-weight: 600;
        color: #9aa1ac;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }

    .sidebar-meta {
        background: #f7f8fb;
        border: 1px solid #eef0f4;
        border-radius: 12px;
        padding: 12px 14px;
        font-size: 12px;
        color: #6d7380;
    }

    .sidebar-meta .meta-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 3px 0;
    }

    .sidebar-meta .meta-key { color: #9aa1ac; }
    .sidebar-meta .meta-val { color: #3f4450; font-weight: 600; }


    /* =========================
       Sidebar 按钮
       ========================= */

    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #e6e8ee;
        background: #ffffff;
        color: #3f4450;
        font-size: 14px;
        font-weight: 500;
        padding: 0.55rem 1rem;
        transition: all 0.18s ease;
        margin-bottom: 8px;
    }

    section[data-testid="stSidebar"] .stButton button:hover {
        background: #eef2ff;
        border-color: #c7d2fe;
        color: #4f46e5;
    }


    /* =========================
       欢迎卡片
       ========================= */

    .welcome-card {
        position: relative;
        background: #ffffff;
        border: 1px solid #e6e8ee;
        border-radius: 16px;
        padding: 26px 28px;
        margin-bottom: 18px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        overflow: hidden;
    }

    .welcome-card::after {
        content: "";
        position: absolute;
        top: -70px;
        right: -70px;
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(79, 70, 229, 0.09), rgba(79, 70, 229, 0) 70%);
        pointer-events: none;
    }

    .welcome-title {
        font-size: 20px;
        font-weight: 700;
        color: #16181d;
        margin-bottom: 8px;
        letter-spacing: -0.3px;
    }

    .welcome-text {
        font-size: 14px;
        color: #5c6370;
        line-height: 1.75;
        margin-bottom: 16px;
    }

    .suggest-list {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
    }

    .suggest-item {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 13.5px;
        color: #3f4450;
        background: #f7f8fb;
        border: 1px solid #eef0f4;
        border-radius: 10px;
        padding: 9px 14px;
    }

    .suggest-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #4f46e5;
        opacity: 0.65;
        flex-shrink: 0;
    }


    /* =========================
       RAG 状态胶囊
       ========================= */

    .rag-status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 5px 12px;
        border-radius: 999px;
        background: #ecfdf5;
        border: 1px solid #d6f5e7;
        color: #0b7a53;
        font-size: 12.5px;
        font-weight: 500;
        margin-bottom: 14px;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #10b981;
        animation: pulse 2.2s ease-out infinite;
    }

    @keyframes pulse {
        0%   { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.40); }
        70%  { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }


    /* =========================
       聊天消息
       ========================= */

    [data-testid="stChatMessage"] {
        padding: 0.85rem 0;
    }

    /* 用户消息气泡 */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageContent"][aria-label="Chat message from user"]) {
        background: #eef2ff;
        border: 1px solid #e0e7ff;
        border-radius: 14px;
        padding: 0.85rem 1.1rem;
    }

    [data-testid="stChatMessageContent"] {
        font-size: 15px;
        line-height: 1.8;
        color: #2b2f36;
    }


    /* =========================
       Chat Input
       ========================= */

    [data-testid="stChatInput"] {
        padding-bottom: 1rem;
    }

    [data-testid="stChatInput"] textarea {
        border-radius: 16px;
        border: 1px solid #e3e5ea;
        background: #ffffff;
        font-size: 15px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
        transition: border-color 0.18s ease, box-shadow 0.18s ease;
    }

    [data-testid="stChatInput"] textarea:focus {
        border-color: #a5b4fc !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.13) !important;
    }

    [data-testid="stChatInputSubmitButton"] {
        color: #4f46e5;
    }


    /* =========================
       提示条
       ========================= */

    [data-testid="stAlert"] {
        border-radius: 12px;
    }


    /* =========================
       隐藏 Streamlit 默认元素
       ========================= */

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
    [data-testid="stDecoration"], [data-testid="stToolbar"] { display: none; }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Session State
# ============================================================

if "message" not in st.session_state:
    st.session_state["message"] = [
        {
            "role": "assistant",
            "content": "你好，有什么可以帮助你？",
        }
    ]


if "rag" not in st.session_state:
    st.session_state["rag"] = RagService()


# ============================================================
# Session ID
# ============================================================

session_id = config.session_config["configurable"]["session_id"]


# ============================================================
# 左侧 Sidebar
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand-row">
            <div class="brand-badge">🤖</div>
            <div>
                <div class="brand-name">企业智能服务</div>
                <div class="brand-sub">基于企业知识库 · RAG</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-label">当前会话</div>',
        unsafe_allow_html=True,
    )


    # ========================================================
    # 清空当前会话
    # ========================================================

    if st.button(
        "🗑️  清空当前会话",
        use_container_width=True,
    ):

        # 只删除页面显示的消息
        st.session_state["message"] = [
            {
                "role": "assistant",
                "content": "你好，有什么可以帮助你？",
            }
        ]

        # 注意：
        # 这里不调用 clear_history()
        # 所以后端历史记录仍然保留

        st.rerun()


    # ========================================================
    # 清空历史记录
    # ========================================================

    if st.button(
        "🧹  清空历史记录",
        use_container_width=True,
    ):

        # 删除后端历史记录
        clear_history(session_id)

        # 为了避免页面继续显示已经删除的历史，
        # 同时把页面消息恢复到初始状态
        st.session_state["message"] = [
            {
                "role": "assistant",
                "content": "你好，有什么可以帮助你？",
            }
        ]

        st.success("历史记录已清空")

        st.rerun()


    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-meta">
            <div class="meta-row"><span class="meta-key">系统</span><span class="meta-val">知识库智能服务</span></div>
            <div class="meta-row"><span class="meta-key">架构</span><span class="meta-val">RAG · GLM</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 欢迎卡片
# ============================================================

st.markdown(
    """
    <div class="welcome-card">
        <div class="welcome-title">👋 欢迎使用企业智能服务</div>
        <div class="welcome-text">你可以直接向我提问，例如：</div>
        <div class="suggest-list">
            <div class="suggest-item"><span class="suggest-dot"></span>企业宗旨是什么？</div>
            <div class="suggest-item"><span class="suggest-dot"></span>公司主要做什么业务？</div>
            <div class="suggest-item"><span class="suggest-dot"></span>公司有哪些产业？</div>
            <div class="suggest-item"><span class="suggest-dot"></span>公司在哪里设有生产基地？</div>
            <div class="suggest-item"><span class="suggest-dot"></span>我们公司的核心理念是什么？</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 系统状态
# ============================================================

st.markdown(
    """
    <div class="rag-status">
        <span class="status-dot"></span>
        知识库智能问答已就绪
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 显示当前页面消息
# ============================================================

for message in st.session_state["message"]:

    with st.chat_message(
        message["role"],
        avatar="🤖" if message["role"] == "assistant" else "🧑",
    ):
        st.markdown(message["content"])


# ============================================================
# 用户输入
# ============================================================

prompt = st.chat_input(
    "请输入您的问题……"
)


# ============================================================
# RAG 对话
# ============================================================

if prompt:

    # --------------------------------------------------------
    # 显示用户问题
    # --------------------------------------------------------

    st.chat_message("user", avatar="🧑").markdown(prompt)

    st.session_state["message"].append(
        {
            "role": "user",
            "content": prompt,
        }
    )


    # --------------------------------------------------------
    # AI 流式回答
    # --------------------------------------------------------

    ai_res_list = []

    with st.chat_message("assistant", avatar="🤖"):

        with st.spinner("AI 正在思考……"):

            res_stream = st.session_state["rag"].chain.stream(
                {"input": prompt},
                config.session_config,
            )

            def capture(generator, cache_list):

                for chunk in generator:

                    cache_list.append(chunk)

                    yield chunk


            st.write_stream(
                capture(
                    res_stream,
                    ai_res_list,
                )
            )


    # --------------------------------------------------------
    # 保存 AI 回答到页面 Session State
    # --------------------------------------------------------

    st.session_state["message"].append(
        {
            "role": "assistant",
            "content": "".join(ai_res_list),
        }
    )
