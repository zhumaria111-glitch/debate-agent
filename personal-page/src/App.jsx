import Nav from './components/Nav'
import Hero from './components/Hero'
import About from './components/About'
import Internship from './components/Internship'
import AIProject from './components/AIProject'
import AILearning from './components/AILearning'
import Awards from './components/Awards'
import Footer from './components/Footer'
import './App.css'

export default function App() {
  return (
    <div className="app">
      <Nav />
      <Hero />
      <About />
      <Internship />
      <AIProject />
      <AILearning />
      <Awards />
      <Footer />
    </div>
  )
}
