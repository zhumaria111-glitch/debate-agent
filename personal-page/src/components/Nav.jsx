export default function Nav() {
  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <nav className="nav">
      <div className="nav-inner">
        <span className="nav-brand" onClick={() => scrollTo('hero')}>朱梦媛</span>
        <div className="nav-links">
          <button onClick={() => scrollTo('about')}>About</button>
          <button onClick={() => scrollTo('internship')}>Experience</button>
          <button onClick={() => scrollTo('project')}>Product</button>
          <button onClick={() => scrollTo('learning')}>Learning</button>
          <button onClick={() => scrollTo('contact')}>Contact</button>
        </div>
      </div>
    </nav>
  )
}
