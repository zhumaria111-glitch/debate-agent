export default function Footer() {
  return (
    <footer className="footer" id="contact">
      <div className="section-label">Contact</div>
      <h2 className="section-title">联系我</h2>
      <div className="divider" />

      <p className="footer-cta">如果你对 AI、产品 or 辩论感兴趣，欢迎聊聊</p>

      <div className="footer-links">
        <a href="mailto:ZMY1732195935@163.com" className="footer-link-card">
          <span className="fl-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="4" width="20" height="16" rx="2" />
              <path d="m22 4-10 8L2 4" />
            </svg>
          </span>
          <span className="fl-label">Email</span>
          <span className="fl-value">ZMY1732195935@163.com</span>
        </a>

        <a href="https://github.com/zhumaria111-glitch/debate-agent" target="_blank" rel="noopener noreferrer" className="footer-link-card">
          <span className="fl-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
              <path d="M9 18c-4.51 2-5-2-7-2" />
            </svg>
          </span>
          <span className="fl-label">GitHub</span>
          <span className="fl-value">debate-agent</span>
        </a>

        <a href="https://www.xiaohongshu.com/user/profile/60f26583000000000100a6ed" target="_blank" rel="noopener noreferrer" className="footer-link-card">
          <span className="fl-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="4" />
              <circle cx="10" cy="10" r="2" />
              <path d="M16 16c-.5-2-3-3-6-3s-5.5 1-6 3" />
              <path d="M19 5 5 19" />
            </svg>
          </span>
          <span className="fl-label">小红书</span>
          <span className="fl-value">米队</span>
        </a>
      </div>

      <p className="footer-copy">朱梦媛 &copy; 2026</p>
    </footer>
  )
}
