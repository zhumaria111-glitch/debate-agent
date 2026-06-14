const modules = [
  {
    id: 'prompt',
    period: '3月中旬 — 4月',
    title: 'Prompt Engineering',
    tagline: '从"会用 AI 聊天"到<strong>以开发者视角调 prompt</strong>——这是最大的认知跃迁。',
    insights: [
      '在和 chatbot 对话时，每次新问题要重新输入提示词，会下意识精进。但以开发者视角来看，<strong>prompt 是成本最低的调优手段</strong>——辩论项目 <strong>3 轮迭代从 2.72 提到 4.24</strong>，绝大多数改进靠的不是改代码，而是改提示词。',
      '<strong>System Prompt 写规则，User Message 写数据。</strong>不要把规则和任务混在一起。System Prompt 的四个核心要素：<strong>身份（Who）、任务（What）、约束（How）、输出格式（Output）</strong>。',
      '当 AI 生成效果不好时，不要盲目怀疑"AI 不行"，而是从四个维度系统归因：<strong>代码 → 模型 → 提示词 → 预处理</strong>。核心方法是控制变量法——这就是 PM 的 <strong>"A/B Test 思维"用在 prompt debugging</strong> 上。',
      '好 prompt 是改出来的。每次修改都是在训练 AI 理解你的标准。<strong>对话跑偏时及时开新窗口——AI 的 context 会累积前面的错误，新窗口就是清零。</strong>',
    ],
    techniques: ['XML标签结构化', 'Chain of Thought', 'Few-Shot', 'Thinking Budget', '负向约束优先', '标签化表达输入'],
  },
  {
    id: 'agent',
    period: '4月 — 5月',
    title: 'Agent 与工具架构',
    tagline: '从使用者变成搭建者——<strong>部署自己的 Agent、写 Skill、建 Subagent 协作体系。</strong>',
    insights: [
      '<strong>Claude Code 不是代码补全工具，而是能自主探索代码库、执行多步骤任务的编程 Agent。</strong>CLAUDE.md 是它的核心机制——写得越好，表现越稳定。每次发现 Agent 反复犯同一个错误时就把规则写入 CLAUDE.md。',
      'MCP 让 LLM 能调用外部工具。一句话理解：<strong>API 是程序之间的通信方式，MCP 是 LLM 和外部工具之间的通信方式。</strong>接上 Figma MCP 可以直接把设计稿转成代码，接上飞书可以通过聊天触发开发任务。',
      'OpenClaw 部署实战中踩的最大的坑：在对话框里让 Agent 创建新机器人，<strong>它把原来的主机器人配置搞没了</strong>。教训——<strong>能用 CLI 终端操作的就不在对话框里操作。</strong>每次对话有上下文记忆，累积的 token 消耗远超预期。',
      'Skill 开发的安全原则：在用别人的 Skill 之前，<strong>必须先看懂 Skill 代码</strong>。这是 AI Agent 时代的新安全范式——不是"不要装不明软件"，而是<strong>"不要运行看不懂的 Skill"</strong>。',
      'Trae IDE 的 Solo 模式可以端到端自主执行完整开发任务。但项目框架设计必须做好——好的项目结构，半年后你自己还能看懂。核心原则：<strong>AI 代替执行而非思考，人的判断不可替代。</strong>',
    ],
    techniques: ['Claude Code', 'OpenClaw', 'Trae IDE', 'MCP协议', 'Skill/Rule/Memory', 'CLI优先', 'Plan模式'],
  },
  {
    id: 'vibecoding',
    period: '5月',
    title: 'Vibecoding 项目实践',
    tagline: '<strong>有想法只是第一步，愿不愿意做以及验证可行性才是更重要的。</strong>',
    insights: [
      '美妆文案生成器 V1→V2：V1 只有基础三输入框 + 一键生成。V2 迭代了输入体验（聚焦高亮、字数提示、动效）、结果展示（卡片层级、复制收藏）、历史记录（搜索/删除/标签分类）、深色模式。prompt 的精确程度直接影响 V0 生成代码的质量。',
      'AI 背单词（Word Coach）：V0 生成界面 → Cursor 接入 API → Vercel 上线。输入英文单词 → MiniMax API 返回中文释义 + 联想记忆 + 英文例句 + 四选一选择题。部署时多次报错，让 Trae 自动修复。',
      '<strong>鹦鹉巧辩——2026 年 5 月抖音 AI 创变者计划黑客松联赛山东赛区三等奖。</strong>田忌赛马式卡牌策略对战 + 互换身份复活赛，从自主分析论证 → 策略化对战 → 沉浸式换位思考，完成"判断-思考-转变"的思维蜕变。',
      '<strong>Dify 历史学知识库——759 页《中国厘金史》PDF → 可对话知识库。</strong>完整 RAG 流程：Cursor 做 OCR + 数据清洗 → Dify 做 chunking（父子分段）+ embedding + rerank + 对话机器人。Prompt 三轮迭代——内存崩溃 → 单线程太慢 → 多线程 + 内存直传，和辩论项目的迭代逻辑完全一致。产品上线：udify.app/chat/K583GtGRELKK7AL0。',
      '不懂技术原理的人 vibecoding 出来的东西仅仅是玩具。对于非技术背景的人来说，<strong>更大的收获在于重新整理自己的工作流，以及做 skill 让 AI 替代部分基础性工作。</strong>',
    ],
    techniques: ['V0', 'Cursor', 'MiniMax API', 'Vercel', 'Trae', 'Dify', 'RAG', 'React + Tailwind'],
  },
  {
    id: 'pm-method',
    period: '4月 — 6月',
    title: 'AI 产品方法论',
    tagline: 'AI PM 和传统 PM 的本质区别：<strong>花更多时间在与模型对话上，而非画原型图。</strong>',
    insights: [
      '传统 PM：写 PRD → 提需 → 等研发排期。AI PM：<strong>自己手搓 demo 验证想法 → 把原型当 PRD → 研发介入做工程化。</strong>"亲手做一个小项目比看一百个攻略都有用。"',
      '<strong>Demo 到产品有 12 个 Gap</strong>——数据从静态文件到实时流、标注从无到完整工作流、从不管延迟成本到实时监控、从无异常降级到<strong>每条路径都有兜底流程图</strong>。系统梳理这些 Gap 的能力，就是 AI PM 的核心竞争力。',
      '用户研究三方法组合：<strong>实地观察 → 深度访谈 → 定量问卷。</strong>关键原则：<strong>观察行为，而非倾听需求。</strong>用户说的往往是解决方案，真正的需求藏在挫败感里。深访用行为还原式提问："上周你备了哪节课，能跟我描述一下整个过程吗？"',
      '观看腾讯、美团线上招聘直播，记录 AI PM 岗位的能力要求和业务方向：懂代码逻辑和技术边界、AI Native 思维、用户洞察和品味更加重要。这些反馈帮助验证了自己的学习方向——<strong>动手做项目比看攻略有用，持续学和动手是 AIPM 最看重的特质。</strong>',
    ],
    techniques: ['Demo→Product Gap分析', '消融实验', '行为还原式访谈', 'A/B测试思维', '5维评估框架'],
  },
  {
    id: 'eval',
    period: '5月 — 6月',
    title: '模型评估体系',
    tagline: '评估能力是 AI PM 的基本功——<strong>知道什么是"好"，才能做出好的 AI 产品。</strong>',
    insights: [
      '分类任务四指标：<strong>精确率关注"误杀"、召回率关注"漏网"、F1 是两个的调和平均、AUC 衡量模型本身的区分能力。</strong>回答模板："先看 AUC 判断整体区分能力，再根据业务场景选阈值。"',
      '辩论项目自建了 <strong>5 维度评估框架：论点准确度 / 覆盖完整度 / 逻辑保真度 / 幻觉检测 / 摘要质量。</strong>对 5 场不同类型辩论做了系统评测，每一轮 prompt 迭代后重新打分。<strong>这是从 0 到 1 建立的——没有现成的辩论分析评估标准。</strong>',
      'A/B 测试四个常见坑：<strong>辛普森悖论、新奇效应、网络效应干扰、多重检验问题。</strong>每个坑都有对应的解决方案。P 值 &lt; 0.05 说明改动有效，&gt; 0.05 更可能是随机抖动。',
      '生成式 AI 除了自动指标（BLEU/ROUGE/困惑度），<strong>必须做人工评估。</strong>四个维度：相关性（切题吗）、流畅度（自然吗）、事实性（准确吗）、有用性（解决问题了吗）。<strong>幻觉率需要单独建立评估体系。</strong>',
    ],
    techniques: ['混淆矩阵', 'Precision/Recall/F1/AUC', 'A/B测试统计', '人工评估4维度', '幻觉率'],
  },
  {
    id: 'insights',
    period: '3月 — 6月 · 持续',
    title: '行业视野',
    tagline: '每天拆解一个 AI 应用，看到问题先想<strong>"能不能用 AI 解决"。</strong>',
    insights: [
      'Abridge（AI 语音转病历）的<strong>强制可追溯机制</strong>——模型每生成一句话，都要严格对应原始对话中的音频或文字片段，医生可随时点击验证。AI 替代人类工作的最佳场景：<strong>必要性工作 + 机械重复 + 低价值消耗。</strong>',
      'Anthropic PM Alex Albert：<strong>AI PM 关注的是 Gap——"我们想让它擅长的能力"和"它本身擅长的能力"之间的差距。</strong>AI 有不可预测性，产品规划不能只靠需求列表。Context 决定一切——用户抱怨回答"过快过于简单"，根因是没有给模型足够的 context。',
      'MCP 的"超级工具"方案：与其让模型调用海量独立工具，不如给它 <strong>代码执行工具 + 文档检索工具</strong>。模型直接写代码调用 API SDK，几乎不占用上下文窗口。预测未来是<strong>人机共生体（Cyborg）——一半 LLM 神经网络，一半传统 CPU 代码。</strong>',
      'Anthropic 6% 报告：6% 的用户会向 Claude 寻求个人指导。四大决策赛道——<strong>健康（27%）、职业（26%）、人际关系（12%）、理财（11%）。</strong>AI 决策辅助产品的四个特质：<strong>专业、易懂、中立、隐私保密。</strong>产品边界：AI 负责信息处理和推演，人保留最终选择权。',
    ],
    techniques: ['Abridge', 'Anthropic PM', 'MCP超级工具', 'Cyborg预测', 'AI决策辅助'],
  },
  {
    id: 'meta',
    period: '贯穿整个学习周期',
    title: '学习方法论',
    tagline: '学习和实践相辅相成。<strong>项目给了方向感和验证场，单纯学理论永远到不了那个深度。</strong>',
    insights: [
      '五步循环：<strong>听播客建立认知框架 → 动手改项目验证理解 → 随时记录心得 → 晚上全盘复盘 → 根据复盘补充下一轮学习内容。</strong>',
      '在小红书持续分享 AI 学习笔记，把碎片输入变成体系化输出。准备录制工具教程的过程本身就是学习闭环——必须搞清楚工具的输入/输出/边界才能讲清楚。<strong>Learn in public。</strong>',
      '<strong>Context 是个人最重要的数字资产。</strong>刚开始把与 AI 的全部对话导出来，慢慢让 AI 解释每一步操作。终极目标：<strong>把自己蒸馏给 AI——AI 越熟悉你，就越能成为得力助手。</strong>',
      '学习是先把书读厚，慢慢再变薄。积累 context 也是一样。<strong>很多人说知识库已落后，但对个人来说它仍然重要。</strong>剩下的东西都是自己真正理解的。',
    ],
    techniques: ['5步学习循环', 'Learn in Public', 'Context积累', '讲解驱动学习', '好奇心+动手'],
  },
]

const galleryImages = [
  { src: './15d8b607c5289c7b4a6ba713a799fbae.jpg', alt: '小红书 AI 学习笔记' },
  { src: './37e9b6a399a44ab98f9214756b4b9201.jpg', alt: '小红书 AI 学习笔记' },
  { src: './52e249de2fab9e59abe9e2def473825b.jpg', alt: '小红书 AI 学习笔记' },
  { src: './59385a6764c7d837253c0c5846842a4c.jpg', alt: '小红书 AI 学习笔记' },
  { src: './69e5d4af7d380bb905a89c15fb04ebb3.jpg', alt: '小红书 AI 学习笔记' },
  { src: './a5389480dd5614d480773254d66afb16.jpg', alt: '小红书 AI 学习笔记' },
]

export default function AILearning() {
  return (
    <section className="ai-learning section-alt" id="learning">
      <div className="section-inner">
        <div className="section-label">Learning</div>
        <h2 className="section-title">AI 学习与思考</h2>
        <div className="divider" />

        {/* ── Intro ─────────────────────────────────────── */}
        <div className="learning-intro">
          <div className="learning-timeline">
            <span className="timeline-dot" />
            <span className="timeline-label">2026.03</span>
            <span className="timeline-line" />
            <span className="timeline-dot" />
            <span className="timeline-label">2026.06</span>
          </div>
          <p className="learning-intro-text">
            四个月系统学习 AI 产品知识。听播客建立认知框架，动手改项目验证理解，在小红书持续输出笔记，晚上复盘沉淀方法论。AIPM 最看重的是<strong>"持续学习和动手能力"</strong>——以下按模块记录这段学习过程中的关键认知。
          </p>
          <div className="learning-stats">
            <span className="stat-item">7 大知识模块</span>
            <span className="stat-sep">·</span>
            <span className="stat-item">30+ 期播客</span>
            <span className="stat-sep">·</span>
            <span className="stat-item">4 个实践项目</span>
            <span className="stat-sep">·</span>
            <span className="stat-item">1 个自建评估体系</span>
          </div>
        </div>

        {/* ── Modules ───────────────────────────────────── */}
        <div className="learning-modules">
          {modules.map((m) => (
            <div className="lm-card" key={m.id}>
              <div className="lm-header">
                <span className="lm-period">{m.period}</span>
                <h3 className="lm-title">{m.title}</h3>
              </div>
              <p className="lm-tagline" dangerouslySetInnerHTML={{ __html: m.tagline }} />
              <div className="lm-insights">
                {m.insights.map((t, j) => (
                  <p className="lm-insight" key={j} dangerouslySetInnerHTML={{ __html: t }} />
                ))}
              </div>
              <div className="lm-tags">
                {m.techniques.map((t) => (
                  <span className="lm-tag" key={t}>{t}</span>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* ── Gallery (kept, slim) ──────────────────────── */}
        <div className="learning-gallery">
          <p className="learning-gallery-note">在小红书持续输出 AI 学习笔记，把碎片输入变成体系化输出</p>
          <div className="notes-gallery notes-gallery-small">
            {galleryImages.map((img, i) => (
              <div className="gallery-item" key={i}>
                <img src={img.src} alt={img.alt} loading="lazy" />
              </div>
            ))}
          </div>
        </div>

        {/* ── Link to full journal ───────────────────────── */}
        <div className="learning-footer">
          <a
            href="https://github.com/zhumaria111-glitch/debate-agent/blob/main/docs/ai-learning-journal.md"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-outline"
            style={{ display: 'inline-block', margin: '0 auto' }}
          >
            查看完整学习笔记（850+ 行，9 章）&rarr;
          </a>
        </div>
      </div>
    </section>
  )
}
