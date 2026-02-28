import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Header from './components/layout/Header'
import Sidebar from './components/layout/Sidebar'
import Footer from './components/layout/Footer'
import HomePage from './pages/HomePage'
import ChatPage from './pages/ChatPage'
import GraphPage from './pages/GraphPage'
import DocumentsPage from './pages/DocumentsPage'

/**
 * Main application component with routing and layout.
 */
export default function App() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-950">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/graph" element={<GraphPage />} />
            <Route path="/documents" element={<DocumentsPage />} />
          </Routes>
        </main>
      </div>
      <Footer />
    </div>
  )
}
