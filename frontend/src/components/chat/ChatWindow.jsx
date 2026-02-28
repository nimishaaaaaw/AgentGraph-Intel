import React, { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import AgentStatus from './AgentStatus'

/**
 * Main chat window displaying the message history.
 * Auto-scrolls to the latest message.
 *
 * @param {Object} props
 * @param {Array} props.messages - Chat messages
 * @param {boolean} props.isLoading - Whether AI is processing
 */
export default function ChatWindow({ messages, isLoading }) {
  const bottomRef = useRef(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
      {messages.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full text-center py-20">
          <span className="text-6xl mb-4">🧠</span>
          <h2 className="text-xl font-semibold text-slate-200 mb-2">
            Ask me anything
          </h2>
          <p className="text-slate-400 max-w-md text-sm">
            I&apos;m an agentic AI assistant powered by LangGraph and Neo4j. Upload documents
            or ask research questions to get started.
          </p>
        </div>
      )}

      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {isLoading && <AgentStatus />}

      <div ref={bottomRef} />
    </div>
  )
}
