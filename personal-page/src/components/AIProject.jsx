const highlights = [
  {
    title: '从 90 分钟到 3 分钟',
    desc: '一场辩论赛动辄一个半小时，新手看完记不住谁说了什么。辩析用 Claude API 把比赛压缩成结构化论点地图——辩题、双方立场、Top 3 论点、最激烈交锋、关键未回应问题，三分钟看懂一场比赛。',
  },
  {
    title: '竞品都在做"AI 陪练"，我们做"AI 分析"',
    desc: '市场上辩论类 AI 产品扎堆在"跟 AI 打辩论"（陪练方向），但入门辩手最痛的场景是"看比赛学不会"。辩析是唯一一个做"赛后分析"的产品——不陪练，帮你看懂真人比赛。',
  },
  {
    title: '自建评估体系，3 轮迭代从 2.72 到 4.24',
    desc: 'AIPM 的核心能力不是写 prompt，是知道产品好不好的标准。我设计了 5 维度评估框架（论点准确度 / 覆盖完整度 / 逻辑保真度 / 幻觉检测 / 摘要质量），对 5 场不同类型辩论做了系统评测，3 轮 prompt 迭代把综合分从 2.72 拉到 4.24。',
  },
]

const docs = [
  {
    title: '产品需求文档（PRD）',
    summary: '产品愿景、目标用户、核心功能优先级、用户流程、成功指标、以及 4 个"不做"的产品决策。首发用户选入门辩手而非教练或研究者，产品形态选 Web App 而非浏览器插件。',
    link: 'https://github.com/zhumaria111-glitch/debate-agent/blob/main/docs/prd.md',
  },
  {
    title: 'AI 输出质量评估报告',
    summary: '5 场辩论 × 5 个维度的系统评测。发现分块合并 bug 导致长文本质量断崖下降（4.4 → 1.4），2 小时内定位并修复。3 轮迭代从 2.72 提到 4.24，证明了 prompt 工程的杠杆效应远大于代码改动。',
    link: 'https://github.com/zhumaria111-glitch/debate-agent/blob/main/docs/eval-report-v0.3.1.md',
    extra: {
      label: '流水线评估',
      link: 'https://github.com/zhumaria111-glitch/debate-agent/blob/main/docs/eval-paste-url.md',
    },
  },
  {
    title: '用户画像文档',
    summary: '首发用户是"陈琳式的入门辩手"——靠看比赛自学辩论，投入时间多但收获薄。她的核心场景是"晚上在宿舍打开一场比赛，看完不知道谁说了什么"。这个画像决定了产品的全部功能优先级。',
    link: 'https://github.com/zhumaria111-glitch/debate-agent/blob/main/docs/user-personas.md',
  },
  {
    title: '竞品分析报告',
    summary: '扫描了辩论类 AI 产品的市场格局。发现竞品扎堆在"实时陪练"方向，而"赛后分析"是空白地带。这一定位直接决定了辩析的功能边界——不做实时对战 AI，做结构化分析工具。',
    link: 'https://github.com/zhumaria111-glitch/debate-agent/blob/main/docs/competitive-analysis.md',
  },
  {
    title: '用户建议与问题解决记录',
    summary: '定向内测 20 余人、68 条原始反馈的完整闭环。按 P0/P1/P2 三级优先级分批迭代，19 条已解决，1 条关闭，2 条延后。含优先级评判标准、决策逻辑、三波执行节奏，体现 PM 的用户思维和问题解决意识。',
    link: 'https://github.com/zhumaria111-glitch/debate-agent/blob/main/docs/user-feedback-log.md',
  },
  ]

export default function AIProject() {
  return (
    <section className="ai-project section" id="project">
      <div className="section-label">Product</div>
      <h2 className="section-title">辩析 · Debate Lens</h2>
      <div className="divider" />

      {/* ── Hero ──────────────────────────────────────────── */}
      <div className="project-hero">
        <div className="project-hero-content">
          <p className="project-desc">
            新手想通过视频学习辩论，缺乏好的工具——于是自学 AI 工具链从零搭建出来：把 90 分钟的比赛压缩成结构化论点，支持 RAG 跨视频检索，让学习真正有效。独立完成从产品构思、技术选型、迭代开发到评估体系搭建的全流程。
          </p>
          <div className="tech-tags">
            <span>Streamlit</span><span>Claude API</span><span>ChromaDB</span>
            <span>Sentence Transformers</span><span>Prompt Engineering</span><span>AI Eval</span>
          </div>
          <a
            href="https://debate-agent-khsvnchexjctge4e3kwb8z.streamlit.app"
            target="_blank"
            rel="noopener noreferrer"
            className="btn"
          >
            在线体验 &rarr;
          </a>
        </div>
        <img src="./debate-lens.jpg" alt="Debate Lens" className="project-img" />
      </div>

      {/* ── Highlights ────────────────────────────────────── */}
      <div className="highlights-section">
        <h3 className="highlights-heading">为什么值得看</h3>
        <div className="highlights-list">
          {highlights.map((h, i) => (
            <div className="highlight-item" key={i}>
              <div className="highlight-num">{i + 1}</div>
              <div className="highlight-body">
                <h4 className="highlight-title">{h.title}</h4>
                <p className="highlight-desc">{h.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Documents ─────────────────────────────────────── */}
      <div className="docs-section">
        <h3 className="docs-heading">产品文档</h3>
        <p className="docs-sub">
          以下五份文档记录了从想法到验证的完整过程，也是 AIPM 日常工作的真实样本。
        </p>
        <div className="docs-grid">
          {docs.map((d, i) => (
            <div className="doc-card" key={i}>
              <h4 className="doc-title">{d.title}</h4>
              <p className="doc-summary">{d.summary}</p>
              <div className="doc-links">
                <a href={d.link} target="_blank" rel="noopener noreferrer" className="doc-link">
                  查看全文 &rarr;
                </a>
                {d.extra && (
                  <a href={d.extra.link} target="_blank" rel="noopener noreferrer" className="doc-link doc-link-secondary">
                    {d.extra.label} &rarr;
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Version history (kept, compact) ───────────────── */}
      <div className="version-section">
        <h3>迭代历程</h3>
        <p className="version-note">
          每个版本评测不同能力维度——从单篇分析准确性，到多赛制流水线自动化，再到跨视频知识库检索。
        </p>
        <div className="version-cards">
          {[
            { v: 'v0.1', desc: 'MVP：粘贴链接 → 结构化分析' },
            { v: 'v0.3.1', desc: '修复空白 + 评委过滤，评分 4.24' },
            { v: 'v0.4', desc: '20条用户反馈闭环 + 思维导图渲染 + 进度弹窗' },
            { v: 'v0.5', desc: 'ChromaDB RAG + 跨视频对比' },
          ].map((item) => (
            <div className="version-chip" key={item.v}>
              <span className="version-tag">{item.v}</span>
              <span className="version-desc">{item.desc}</span>
            </div>
          ))}
        </div>
        <div className="eval-links">
          <a href="https://github.com/zhumaria111-glitch/debate-agent/blob/main/docs/eval-report-v0.3.1.md" target="_blank" rel="noopener noreferrer">结构化分析评估</a>
          <span className="link-sep">·</span>
          <a href="https://github.com/zhumaria111-glitch/debate-agent/blob/main/docs/eval-paste-url.md" target="_blank" rel="noopener noreferrer">流水线评估</a>
          <span className="link-sep">·</span>
          <a href="https://github.com/zhumaria111-glitch/debate-agent/blob/main/docs/eval-knowledge-base.md" target="_blank" rel="noopener noreferrer">知识库 RAG 评估</a>
        </div>
      </div>
    </section>
  )
}
