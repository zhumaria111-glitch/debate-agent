"""Debate Agent — AI-powered debate analysis.

Paste a B站/YouTube video link → transcript + structured mind map + personal knowledge base.
"""

import json
import os
import streamlit as st
from src.video_fetcher import fetch_transcript
from src.compressor import compress_transcript
from src.agent import run_agent_turn, generate_welcome_message, get_suggestions

# Resolve paths relative to this file so Streamlit works regardless of CWD
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Page config ─────────────────────────────────────────────────────────

st.set_page_config(
    page_title="辩析 · Debate Lens",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Styles ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Hide default sidebar */
    [data-testid="collapsedControl"] { display: none; }

    /* Video cards */
    .video-card {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        overflow: hidden;
        cursor: pointer;
        transition: all 0.25s;
        background: white;
        height: 100%;
    }
    .video-card:hover {
        border-color: #ff4b4b;
        box-shadow: 0 4px 16px rgba(255,75,75,0.12);
        transform: translateY(-2px);
    }
    .video-card .cover {
        width: 100%;
        aspect-ratio: 16/10;
        object-fit: cover;
        background: #f5f5f5;
    }
    .video-card .body {
        padding: 10px 12px 14px 12px;
    }
    .video-card .title {
        font-weight: 600;
        font-size: 14px;
        line-height: 1.4;
        margin-bottom: 6px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .video-card .meta {
        font-size: 12px;
        color: #999;
        display: flex;
        gap: 8px;
        align-items: center;
    }
    .video-card .tag {
        background: #fff0f0;
        color: #ff4b4b;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
    }

    /* Feature cards */
    .feature-card {
        border: 1px solid #e8e8e8;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        background: white;
        height: 100%;
    }
    .feature-card .icon {
        font-size: 36px;
        margin-bottom: 12px;
    }
    .feature-card h3 {
        font-size: 18px;
        margin-bottom: 8px;
    }
    .feature-card p {
        font-size: 13px;
        color: #888;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# ── API Key ─────────────────────────────────────────────────────────────

def _load_dotenv(path: str) -> None:
    """Load KEY=VALUE pairs from a .env file into os.environ (no dependencies)."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

_load_dotenv(os.path.join(ROOT_DIR, ".env"))

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", None)  # CC Switch proxy URL

# ── Session state ───────────────────────────────────────────────────────

defaults = {
    "debate_data": None,
    "processing_done": False,
    "messages": [],
    "transcript": "",
    "video_title": "",
    "video_error": "",
    "current_video_url": "",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Built-in debate videos ──────────────────────────────────────────────

BUILT_IN_VIDEOS = [
    {
        "title": "是否应该全面推行四天工作制",
        "url": "https://www.bilibili.com/video/BV1uT421k7Fb",
        "bvid": "BV1uT421k7Fb",
        "type": "政策辩",
        "transcript_file": os.path.join(ROOT_DIR, "data", "sample_debate.txt"),
    },
    {
        "title": "爱情是/不是人类的必需品",
        "url": "https://www.bilibili.com/video/BV1QdwCe3EoZ",
        "bvid": "BV1QdwCe3EoZ",
        "type": "价值辩",
        "transcript_file": os.path.join(ROOT_DIR, "data", "eval", "debate_01.txt"),
    },
    {
        "title": "拐卖妇女儿童应该/不应该买卖同罪",
        "url": "https://www.bilibili.com/video/BV1uY4y1m7hb",
        "bvid": "BV1uY4y1m7hb",
        "type": "政策辩",
        "transcript_file": os.path.join(ROOT_DIR, "data", "eval", "debate_02_cleaned.txt"),
    },
    {
        "title": "网络暴力的根源是恶意还是愚蠢",
        "url": "https://www.bilibili.com/video/BV1N6wLeUEnN",
        "bvid": "BV1N6wLeUEnN",
        "type": "事实辩",
        "transcript_file": os.path.join(ROOT_DIR, "data", "eval", "debate_03_cleaned.txt"),
    },
    {
        "title": "脱口秀还是辩论更能回应世界",
        "url": "https://www.bilibili.com/video/BV1uo4y1f7Ba",
        "bvid": "BV1uo4y1f7Ba",
        "type": "哲理辩",
        "transcript_file": os.path.join(ROOT_DIR, "data", "eval", "debate_04_cleaned.txt"),
    },
]


def get_video_cover(bvid: str) -> str:
    """Try to get B站 video cover, fall back to placeholder."""
    import requests
    try:
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.bilibili.com/",
        }
        resp = requests.get(url, headers=headers, timeout=8)
        data = resp.json()
        if data["code"] == 0:
            return data["data"]["pic"]
    except Exception:
        pass
    return ""


# ── Model selector (sidebar) ─────────────────────────────────────────────

with st.sidebar:
    model = st.selectbox(
        "模型",
        ["deepseek-chat", "deepseek-reasoner"],
        index=0,
        help="deepseek-chat 速度快，deepseek-reasoner 逻辑更强但较慢。",
    )

# ── Process transcript ──────────────────────────────────────────────────

def process_transcript(transcript_text: str, source_title: str = ""):
    """Run the compression pipeline and set session state."""
    try:
        debate_data = compress_transcript(transcript_text, API_KEY, model, base_url=BASE_URL)
        st.session_state.debate_data = debate_data.to_dict()
        st.session_state.transcript = transcript_text
        st.session_state.processing_done = True
        st.session_state.video_title = source_title

        welcome = generate_welcome_message(st.session_state.debate_data)
        st.session_state.messages = [
            {"role": "assistant", "content": welcome}
        ]
        st.rerun()
    except Exception as e:
        st.error(f"分析出错：{e}")

# ── Helpers ─────────────────────────────────────────────────────────────

def build_mermaid_mindmap(debate_data: dict) -> str:
    topic = debate_data.get("topic", "辩题")
    aff_side = debate_data.get("affirmative_side", "正方")
    neg_side = debate_data.get("negative_side", "反方")
    qv = debate_data.get("quick_view", {})
    lines = ["```mermaid", "mindmap", f"  root({topic})"]
    lines.append(f"    正方：{aff_side}")
    for i, p in enumerate(qv.get("affirmative_top3", []), 1):
        text = _escape_mermaid(p)
        if text:
            lines.append(f"      论点{i}：{text}")
    lines.append(f"    反方：{neg_side}")
    for i, p in enumerate(qv.get("negative_top3", []), 1):
        text = _escape_mermaid(p)
        if text:
            lines.append(f"      论点{i}：{text}")
    hottest = qv.get("hottest_clash", "")
    if hottest:
        lines.append(f"    🔥交锋")
        lines.append(f"      {_escape_mermaid(hottest)}")
    unresolved = qv.get("key_unresolved", "")
    if unresolved:
        lines.append(f"    ⚠️未回应")
        lines.append(f"      {_escape_mermaid(unresolved)}")
    lines.append("```")
    return "\n".join(lines)

def _escape_mermaid(text: str) -> str:
    return text.replace('"', "'").replace("(", "（").replace(")", "）").replace("[", "【").replace("]", "】")

def build_export_report(debate_data: dict, messages: list[dict], transcript: str) -> str:
    qv = debate_data.get("quick_view") or {}
    lines = [f"# 辩论分析报告", "", f"## 辩题", f"{debate_data.get('topic', '未知')}"]

    # ── Quick View ──
    lines.extend(["", "## 速览", "",
        f"**一句话总结**：{qv.get('one_sentence_summary', '（未生成）')}",
        f"**正方立场**：{debate_data.get('affirmative_side', '')}",
        f"**反方立场**：{debate_data.get('negative_side', '')}",
        "", "### 正方 Top 3 论点"])
    for i, p in enumerate(qv.get("affirmative_top3", []), 1):
        lines.append(f"{i}. {p}")
    lines.extend(["", "### 反方 Top 3 论点"])
    for i, p in enumerate(qv.get("negative_top3", []), 1):
        lines.append(f"{i}. {p}")
    lines.extend(["", f"**🔥 最激烈交锋**：{qv.get('hottest_clash') or '（未生成）'}",
        f"**⚠️ 关键未回应问题**：{qv.get('key_unresolved') or '（未生成）'}",
        f"**🏷 关键词**：{' | '.join(qv.get('keywords', []))}"])

    # ── Rounds ──
    rounds = debate_data.get("rounds", [])
    if rounds:
        lines.extend(["", "---", "", "## 论点攻防链（逐回合）", ""])
        for r in rounds:
            lines.append(f"### {r.get('round_name', '')} — {r.get('side', '')} {r.get('speaker', '')}")
            lines.append(f"> {r.get('content_summary', '')}")
            for c in r.get("claims", []):
                rebut = f" ↳ 反驳 {c.get('rebuts_claim_id')}" if c.get("rebuts_claim_id") else ""
                status = " ✅已回应" if c.get("responded") else " ⚠️未回应"
                lines.append(f"- **{c.get('content', '')}**{rebut}{status}")
                if c.get("evidence"):
                    lines.append(f"  证据：{c['evidence']}")
                if c.get("response_summary"):
                    lines.append(f"  回应：{c['response_summary']}")
            lines.append("")

    # ── Unresolved Issues ──
    unresolved = debate_data.get("unresolved_issues", [])
    if unresolved:
        lines.extend(["", "## 未解决的问题", ""])
        for u in unresolved:
            lines.append(f"- [{u.get('importance', '中')}] {u.get('issue', '')}（提出方：{u.get('raised_by', '')}）")

    # ── Factual Claims ──
    factual = debate_data.get("factual_claims", [])
    if factual:
        lines.extend(["", "## 事实性主张", ""])
        for f in factual:
            evidence = f" — 证据：{f.get('evidence_detail')}" if f.get("has_evidence") else " — 无证据"
            lines.append(f"- {f.get('claim', '')}（{f.get('speaker', '')}）{evidence}")

    # ── Q&A ──
    qa_msgs = [m for m in messages if m["role"] != "assistant" or not m["content"].startswith("这场辩论我已经分析完了")]
    if qa_msgs:
        lines.extend(["", "---", "", "## 追问记录", ""])
        for m in qa_msgs:
            role = "AI" if m["role"] == "assistant" else "用户"
            lines.append(f"**{role}**：{m['content']}")
            lines.append("")

    # ── Transcript ──
    lines.extend(["", "---", "", "## 辩论逐字稿", "", transcript])
    return "\n".join(lines)

# ── Main UI ─────────────────────────────────────────────────────────────

# --- Header ---
st.markdown("""
<div style="text-align: center; padding: 20px 0 10px 0;">
    <h1 style="font-size: 36px; margin-bottom: 8px;">🎤 辩析 · Debate Lens</h1>
    <p style="font-size: 16px; color: #888; margin-bottom: 4px;">
        一场一小时辩论赛，三分钟看懂论证骨架
    </p>
    <p style="font-size: 14px; color: #bbb;">
        粘贴 B站 / YouTube 视频链接即可
    </p>
</div>
""", unsafe_allow_html=True)

# --- Three Feature Icons ---
_cols_feat = st.columns(3)
with _cols_feat[0]:
    st.markdown("""
    <div class="feature-card">
        <div class="icon">📜</div>
        <h3>一键生成逐字稿</h3>
        <p>粘贴视频链接，自动提取完整字幕<br>说话人分离，标注时间轴</p>
    </div>
    """, unsafe_allow_html=True)
with _cols_feat[1]:
    st.markdown("""
    <div class="feature-card">
        <div class="icon">🧠</div>
        <h3>结构化思维导图</h3>
        <p>正反方论点自动提取<br>反驳链、交锋点、未回应问题一目了然</p>
    </div>
    """, unsafe_allow_html=True)
with _cols_feat[2]:
    st.markdown("""
    <div class="feature-card">
        <div class="icon">📥</div>
        <h3>加入个人知识库</h3>
        <p>分析报告 + AI 对话一键导出<br>积累你的辩论学习档案</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── URL Input ───────────────────────────────────────────────────────────

if not st.session_state.processing_done:
    st.markdown("### 🔗 粘贴视频链接开始分析")

    col_url, col_btn = st.columns([4, 1])
    with col_url:
        video_url = st.text_input(
            "视频链接",
            placeholder="https://www.bilibili.com/video/BV... 或 https://youtube.com/watch?v=...",
            key="video_url_input",
            label_visibility="collapsed",
        )
    with col_btn:
        analyze_disabled = not (API_KEY and video_url.strip())
        analyze_clicked = st.button(
            "🔍 开始分析",
            type="primary",
            disabled=analyze_disabled,
            use_container_width=True,
            key="analyze_btn",
        )

    if analyze_clicked and video_url.strip():
        st.session_state.current_video_url = video_url.strip()
        st.session_state.processing_done = False
        st.session_state.debate_data = None
        st.session_state.messages = []
        st.session_state.video_error = ""
        st.session_state.video_title = ""

        with st.spinner("🎬 正在获取视频字幕..."):
            result = fetch_transcript(video_url.strip())

        if result.error:
            st.error(f"⚠️ 字幕获取失败：{result.error}")
            st.info("💡 该视频可能未开启 AI 字幕。B站视频需开启 AI 字幕才能自动提取文字稿。")
        else:
            with st.spinner("🧠 正在分析论证结构..."):
                process_transcript(result.full_text, result.title)

    # --- Built-in video gallery ---
    st.markdown("### 📺 热门辩论分析")
    st.caption("以下视频已开启 AI 字幕，可直接分析")

    num_cols = min(3, len(BUILT_IN_VIDEOS))
    for i, vid in enumerate(BUILT_IN_VIDEOS):
        col_idx = i % num_cols
        if col_idx == 0:
            cols_videos = st.columns(num_cols)
        cover = get_video_cover(vid["bvid"])
        with cols_videos[col_idx]:
            if cover:
                st.markdown(
                    f"""<div class="video-card">
                    <img class="cover" src="{cover}" alt="cover"/>
                    <div class="body">
                    <div class="title">{vid['title']}</div>
                    <div class="meta"><span class="tag">{vid['type']}</span>辩论赛</div>
                    </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            else:
                # Embed B站 player as fallback cover
                st.markdown(
                    f"""<div class="video-card">
                    <iframe src="https://player.bilibili.com/player.html?bvid={vid['bvid']}&page=1&high_quality=1&autoplay=0"
                    style="width:100%;aspect-ratio:16/10;border:none;" allowfullscreen></iframe>
                    <div class="body">
                    <div class="title">{vid['title']}</div>
                    <div class="meta"><span class="tag">{vid['type']}</span>辩论赛</div>
                    </div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            if st.button(f"分析这场辩论", key=f"builtin_{i}", use_container_width=True):
                st.session_state.current_video_url = vid["url"]
                st.session_state.processing_done = False
                st.session_state.debate_data = None
                st.session_state.messages = []
                st.session_state.video_error = ""
                st.session_state.video_title = vid["title"]

                with st.spinner("📂 正在加载逐字稿..."):
                    try:
                        with open(vid["transcript_file"], "r") as f:
                            transcript_text = f.read()
                        process_transcript(transcript_text, vid["title"])
                    except FileNotFoundError:
                        st.error(f"逐字稿文件未找到：{vid['transcript_file']}")


# ── Results ─────────────────────────────────────────────────────────────

if st.session_state.processing_done and st.session_state.debate_data:
    debate_data = st.session_state.debate_data
    qv = debate_data.get("quick_view", {})
    raw_text = st.session_state.transcript

    st.markdown("---")

    # --- Header ---
    if st.session_state.video_title:
        st.caption(f"📺 {st.session_state.video_title}")

    # --- Function tabs ---
    tab_transcript, tab_mindmap, tab_qa = st.tabs([
        "📜 逐字稿",
        "🧠 思维导图",
        "💬 深度追问",
    ])

    # ── Tab 1: Transcript ───────────────────────────────────────────
    with tab_transcript:
        st.subheader("完整逐字稿")
        if raw_text:
            st.markdown(f"共 {len(raw_text):,} 字")
            st.download_button(
                "📥 下载逐字稿（.txt）",
                data=raw_text,
                file_name=f"辩论逐字稿_{debate_data.get('topic', 'debate')}.txt",
                mime="text/plain",
            )
        else:
            st.info("未获取到逐字稿，可能视频没有字幕。")

    # ── Tab 2: Mind Map ─────────────────────────────────────────────
    with tab_mindmap:
        col_m1, col_m2 = st.columns([3, 1])
        with col_m1:
            st.subheader("论证结构思维导图")
        with col_m2:
            report = build_export_report(debate_data, st.session_state.messages, raw_text)
            st.download_button(
                "📥 导出报告（Markdown）",
                data=report,
                file_name=f"辩论分析_{debate_data.get('topic', 'report')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
            st.download_button(
                "📋 导出原始 JSON",
                data=json.dumps(debate_data, ensure_ascii=False, indent=2),
                file_name=f"辩论分析_{debate_data.get('topic', 'json')}.json",
                mime="application/json",
                use_container_width=True,
            )

        mermaid_code = build_mermaid_mindmap(debate_data)
        st.markdown(mermaid_code)

        st.caption("💡 思维导图展示双方核心论点和交锋结构。切换至「深度追问」tab 可针对任意节点追问。")

        # --- Quick View summary ---
        with st.expander("📋 文字版 3 分钟速览"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**辩题**：{debate_data.get('topic', '未知')}")
                st.markdown(f"**一句话总结**：{qv.get('one_sentence_summary', '')}")
                st.markdown("**🔥 最激烈交锋**")
                st.info(qv.get("hottest_clash", ""))
                st.markdown("**⚠️ 关键未回应问题**")
                st.warning(qv.get("key_unresolved", ""))
            with col_b:
                st.markdown(f"**正方** · {debate_data.get('affirmative_side', '')}")
                for p in qv.get("affirmative_top3", []):
                    st.markdown(f"- {p}")
                st.markdown(f"**反方** · {debate_data.get('negative_side', '')}")
                for p in qv.get("negative_top3", []):
                    st.markdown(f"- {p}")
                keywords = qv.get("keywords", [])
                kw_html = " ".join(
                    f'<code style="background:#f0f2f6;padding:4px 10px;border-radius:12px;margin:2px;">{kw}</code>'
                    for kw in keywords
                )
                st.markdown(kw_html, unsafe_allow_html=True)

        # --- Argument chain detail ---
        with st.expander("🔍 论点攻防链（逐回合）"):
            rounds = debate_data.get("rounds", [])
            if rounds:
                for r in rounds:
                    st.markdown(f"**{r.get('round_name', '')}** — {r.get('side', '')} {r.get('speaker', '')}")
                    st.caption(r.get("content_summary", ""))
                    for c in r.get("claims", []):
                        rebuts = f" ↳ 反驳 {c.get('rebuts_claim_id')}" if c.get("rebuts_claim_id") else ""
                        status = " ✅已回应" if c.get("responded") else " ⚠️未回应"
                        st.markdown(f"- {c.get('content', '')}{rebuts}{status}")
                    st.markdown("---")

    # ── Tab 3: Deep Q&A ─────────────────────────────────────────────
    with tab_qa:
        # Messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Suggestions
        user_msg_count = sum(1 for m in st.session_state.messages if m["role"] == "user")
        if user_msg_count == 0:
            st.caption("💡 试试这些问题：")
            suggestions = get_suggestions()
            cols_s = st.columns(len(suggestions))
            for i, sug in enumerate(suggestions):
                with cols_s[i]:
                    if st.button(sug, key=f"sug_{i}", use_container_width=True):
                        st.session_state.messages.append({"role": "user", "content": sug})
                        st.rerun()

        # Chat input
        if user_input := st.chat_input("追问这场辩论的任何问题..."):
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("🧠 分析中..."):
                    history_for_api = [
                        m for m in st.session_state.messages
                        if not (
                            m["role"] == "assistant"
                            and m["content"].startswith("这场辩论我已经分析完了")
                        )
                    ]
                    history_for_api = history_for_api[:-1]

                    response = run_agent_turn(
                        user_input,
                        debate_data,
                        API_KEY,
                        history_for_api,
                        model,
                        base_url=BASE_URL,
                    )
                    st.markdown(response)

            st.session_state.messages.append({"role": "assistant", "content": response})

    # ── Bottom actions ───────────────────────────────────────────────
    st.markdown("---")
    col_new, _ = st.columns([1, 5])
    with col_new:
        if st.button("🔄 分析新的辩论", use_container_width=True):
            for key in defaults:
                st.session_state[key] = defaults[key]
            st.rerun()


# ── State: No API key ──────────────────────────────────────────────────

if not API_KEY and not st.session_state.processing_done:
    st.warning(
        "⚠️ 未检测到 API Key。请在终端运行：\n\n"
        "```bash\nexport ANTHROPIC_API_KEY=sk-your-key-here\n```\n\n"
        "然后重新启动应用：`streamlit run app.py`"
    )

