import React from 'react'

/**
 * Footer with tech stack information.
 */
export default function Footer() {
  const techStack = [
    { label: 'LangGraph', color: 'bg-indigo-600' },
    { label: 'Neo4j', color: 'bg-emerald-600' },
    { label: 'FastAPI', color: 'bg-teal-600' },
    { label: 'React', color: 'bg-sky-600' },
    { label: 'ChromaDB', color: 'bg-purple-600' },
    { label: 'Gemini AI', color: 'bg-amber-600' },
  ]

  return (
    <footer className="bg-slate-900 border-t border-slate-700/50 px-4 py-3">
      <div className="flex flex-wrap items-center justify-center gap-2">
        <span className="text-slate-500 text-xs mr-2">Powered by:</span>
        {techStack.map(({ label, color }) => (
          <span
            key={label}
            className={`${color} text-white text-xs font-medium px-2 py-0.5 rounded-full`}
          >
            {label}
          </span>
        ))}
      </div>
    </footer>
  )
}
