import React from 'react'
import ChatWindow from '../components/chat/ChatWindow'
import InputBar from '../components/chat/InputBar'
import ErrorBoundary from '../components/common/ErrorBoundary'
import { useChat } from '../hooks/useChat'
import { Trash2 } from 'lucide-react'

/**
 * Full chat page layout.
 */
export default function ChatPage() {
  const { messages, isLoading, send, clearMessages } = useChat()

  return (
    <ErrorBoundary>
      <div className="flex flex-col h-[calc(100vh-4rem-3rem)]">
        {/* Chat header */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-slate-700/50 bg-slate-900/50">
          <div>
            <h1 className="font-semibold text-slate-200 text-sm">AI Research Assistant</h1>
            <p className="text-xs text-slate-500">
              {messages.length === 0 ? 'No messages yet' : `${messages.length} message${messages.length !== 1 ? 's' : ''}`}
            </p>
          </div>
          {messages.length > 0 && (
            <button
              onClick={clearMessages}
              className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-red-400 transition-colors"
            >
              <Trash2 size={13} /> Clear
            </button>
          )}
        </div>

        {/* Messages area */}
        <ChatWindow messages={messages} isLoading={isLoading} />

        {/* Input */}
        <InputBar onSend={send} disabled={isLoading} />
      </div>
    </ErrorBoundary>
  )
}
