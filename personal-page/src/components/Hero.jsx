export default function Hero() {
  return (
    <section className="hero" id="hero">
      <div className="hero-grid">
        <div className="hero-text">
          <p className="hero-greeting">Hi, 我是</p>
          <h1 className="hero-name">朱梦媛</h1>
          <p className="hero-intro">
            一个对新事物永远保持好奇的人。
            自学 AI 工具链从零搭建产品，
            喜欢追问为什么，也喜欢把想法变成现实。
          </p>
          <div className="hero-philosophy">
            爱问为什么 · 爱想怎么做 · 爱说给你听
          </div>
          <div className="hero-meta">
            <div className="edu-badge">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                <path d="M6 12v5c0 2 4 3 6 3s6-1 6-3v-5" />
              </svg>
              <div className="edu-text">
                <div className="edu-line">2021.09 – 2025.06 山东大学 本科</div>
                <div className="edu-line">2025.09 至今 山东大学 硕士</div>
                <div className="edu-sub">985 本硕 · GPA 4.0</div>
              </div>
            </div>
          </div>
        </div>
        <div className="hero-visual">
          <div className="hero-photo-wrap">
            <img src="./photo.jpg" alt="朱梦媛" className="hero-photo" />
          </div>
          <div className="hero-accent-circle" />
        </div>
      </div>
    </section>
  )
}
