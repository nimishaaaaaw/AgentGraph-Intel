import React, { useState, useEffect } from 'react'

const AGENT_STEPS = [
  { emoji: '🔍', label: 'Router analyzing query...', agent: 'router' },
  { emoji: '📚', label: 'Researcher retrieving documents...', agent: 'researcher' },
  { emoji: '🔗', label: 'KG Builder extracting entities...', agent: 'kg_builder' },
  { emoji: '🧠', label: 'Analyst reasoning over context...', agent: 'analyst' },
]

/**
 * Animated status indicator showing which agent is currently active.
 */
export default function AgentStatus() {
  const [stepIndex, setStepIndex] = useState(0)

  // Cycle through agent steps for a realistic animation
  useEffect(() => {
    const interval = setInterval(() => {
      setStepIndex((i) => (i + 1) % AGENT_STEPS.length)
    }, 1800)
    return () => clearInterval(interval)
  }, [])

  const current = AGENT_STEPS[stepIndex]

  return (
    <div className="flex justify-start">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-bl-sm px-4 py-3 max-w-xs">
        <div className="flex items-center gap-2">
          {/* Pulsing dot */}
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500" />
          </span>
          <span className="text-sm text-slate-300">
            {current.emoji} {current.label}
          </span>
        </div>

        {/* Progress dots */}
        <div className="flex gap-1 mt-2">
          {AGENT_STEPS.map((step, i) => (
            <div
              key={step.agent}
              className={`h-1 flex-1 rounded-full transition-all duration-500 ${
                i <= stepIndex ? 'bg-indigo-500' : 'bg-slate-700'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
