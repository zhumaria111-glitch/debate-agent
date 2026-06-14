export default function About() {
  return (
    <section className="about section" id="about">
      <div className="section-label">About</div>
      <h2 className="section-title">关于我</h2>
      <div className="divider" />

      <div className="about-text">
        <p>
          我喜欢把东西搞清楚。
        </p>
        <p>
          一个视频为什么看完什么都没记住，一个工具为什么用起来总差点意思，
          一个 AI 回答为什么听起来对但就是感觉不够——这类问题会一直在我脑子里转，
          直到我动手去试。
        </p>
        <p>
          辩析 · Debate Lens 就是这样来的。我发现新手想通过视频学习辩论，没有好的工具，
          于是自学 AI 工具链，从零把它搭出来——把 90 分钟的比赛压缩成结构化论点，
          支持 RAG 跨视频检索，让学习真正有效。
        </p>
        <p>
          我相信 AI 产品的核心不是技术多酷，而是它解决的问题够不够真实。
        </p>
      </div>

      <div className="traits-row">
        <div className="skill-card">
          <div className="skill-icon">&#128269;</div>
          <h3>好奇心</h3>
          <p>OpenClaw 产生就立马体验使用，主动到各地参加小龙虾交流会</p>
        </div>
        <div className="skill-card">
          <div className="skill-icon">&#9889;</div>
          <h3>行动力</h3>
          <p>自学 AI 工具链，从零搭建辩论分析产品，报名参加多场黑客松</p>
        </div>
        <div className="skill-card">
          <div className="skill-icon">&#9998;</div>
          <h3>复盘习惯</h3>
          <p>每天记录学习心得，让 AI 做学习伙伴一起复盘</p>
        </div>
      </div>
    </section>
  )
}
