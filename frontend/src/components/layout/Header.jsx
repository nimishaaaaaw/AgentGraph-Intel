import React from 'react'
import { NavLink } from 'react-router-dom'
import { MessageSquare, Network, FileText, Home, Github } from 'lucide-react'

/**
 * Top navigation header with logo and nav links.
 */
export default function Header() {
  const navLinks = [
    { to: '/', label: 'Home', icon: Home },
    { to: '/chat', label: 'Chat', icon: MessageSquare },
    { to: '/graph', label: 'Graph', icon: Network },
    { to: '/documents', label: 'Documents', icon: FileText },
  ]

  return (
    <header className="bg-slate-900 border-b border-slate-700/50 px-4 py-3 flex items-center justify-between sticky top-0 z-50">
      {/* Logo */}
      <div className="flex items-center gap-2">
        <span className="text-2xl">🧠</span>
        <span className="font-bold text-lg text-white tracking-tight">
          AgentGraph <span className="text-indigo-400">Intel</span>
        </span>
      </div>

      {/* Navigation */}
      <nav className="hidden md:flex items-center gap-1">
        {navLinks.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors duration-150 ${
                isActive
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700'
              }`
            }
          >
            <Icon size={15} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* GitHub link */}
      <a
        href="https://github.com/nimishaaaaaw/AgentGraph-Intel"
        target="_blank"
        rel="noopener noreferrer"
        className="text-slate-400 hover:text-white transition-colors"
        aria-label="GitHub Repository"
      >
        <Github size={20} />
      </a>
    </header>
  )
}
