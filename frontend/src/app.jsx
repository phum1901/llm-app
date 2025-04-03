import './app.css'
import ChatInterface from './chat-interface.jsx'

function App() {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>AltoGPT</h1>
      </header>
      <div className="chat-container">
        <ChatInterface />
      </div>
    </div>
  )
}

export default App
