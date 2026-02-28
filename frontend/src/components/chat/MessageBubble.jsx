import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Copy, Check, ChevronDown, ChevronUp } from 'lucide-react'

/**
 * Individual message bubble component.
 * User messages are right-aligned (indigo), AI messages left-aligned (slate).
 *
 * @param {Object} props
 * @param {Object} props.message - Message data
 */
export default function MessageBubble({ message }) {
  const [copied, setCopied] = useState(false)
  const [showSources, setShowSources] = useState(false)
  const isUser = message.role === 'user'

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Avatar */}
        <div className={`flex items-end gap-2 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
          <div
            className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
              isUser ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-200'
            }`}
          >
            {isUser ? 'U' : '🧠'}
          </div>

          {/* Bubble */}
          <div
            className={`rounded-2xl px-4 py-3 ${
              isUser
                ? 'bg-indigo-600 text-white rounded-br-sm'
                : 'bg-slate-800 text-slate-100 rounded-bl-sm'
            }`}
          >
            {isUser ? (
              <p className="text-sm">{message.content}</p>
            ) : (
              <div className="text-sm prose prose-invert prose-sm max-w-none">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            )}
          </div>
        </div>

        {/* Actions and metadata for AI messages */}
        {!isUser && (
          <div className="mt-1.5 ml-9 flex flex-col gap-1">
            {/* Agent trail */}
            {message.agent_trail && message.agent_trail.length > 0 && (
              <div className="flex items-center gap-1 flex-wrap">
                {message.agent_trail.map((agent, i) => (
                  <span
                    key={i}
                    className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded-full"
                  >
                    {agent}
                  </span>
                ))}
              </div>
            )}

            <div className="flex items-center gap-2">
              {/* Copy button */}
              <button
                onClick={handleCopy}
                className="text-slate-500 hover:text-slate-300 transition-colors"
                aria-label="Copy message"
              >
                {copied ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
              </button>

              {/* Sources toggle */}
              {message.sources && message.sources.length > 0 && (
                <button
                  onClick={() => setShowSources((s) => !s)}
                  className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  {showSources ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                  {message.sources.length} source{message.sources.length > 1 ? 's' : ''}
                </button>
              )}
            </div>

            {/* Sources list */}
            {showSources && message.sources && (
              <div className="mt-1 space-y-1">
                {message.sources.map((source, i) => (
                  <div
                    key={i}
                    className="text-xs bg-slate-800/80 border border-slate-700 rounded-lg px-3 py-2"
                  >
                    <span className="text-slate-400 font-medium">
                      [{i + 1}] {source.document || source.title || 'Source'}
                    </span>
                    {source.chunk && (
                      <p className="text-slate-500 mt-0.5 line-clamp-2">{source.chunk}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
