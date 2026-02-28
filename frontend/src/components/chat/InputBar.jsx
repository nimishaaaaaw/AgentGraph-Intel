import React, { useState, useRef } from 'react'
import { Send, Paperclip } from 'lucide-react'

/**
 * Chat input bar with text field and send button.
 *
 * @param {Object} props
 * @param {Function} props.onSend - Callback with message text
 * @param {boolean} props.disabled - Whether input is disabled
 */
export default function InputBar({ onSend, disabled }) {
  const [value, setValue] = useState('')
  const textareaRef = useRef(null)

  const handleSend = () => {
    if (value.trim() && !disabled) {
      onSend(value.trim())
      setValue('')
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = (e) => {
    setValue(e.target.value)
    // Auto-resize textarea
    const el = textareaRef.current
    if (el) {
      el.style.height = 'auto'
      el.style.height = `${Math.min(el.scrollHeight, 200)}px`
    }
  }

  return (
    <div className="border-t border-slate-700/50 bg-slate-900 px-4 py-3">
      <div className="flex items-end gap-2 bg-slate-800 border border-slate-600 rounded-xl px-3 py-2 focus-within:border-indigo-500 transition-colors">
        {/* File attach button */}
        <button
          className="text-slate-500 hover:text-slate-300 transition-colors mb-1 flex-shrink-0"
          title="Attach file"
        >
          <Paperclip size={18} />
        </button>

        {/* Text input */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Ask a research question... (Shift+Enter for new line)"
          rows={1}
          className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-sm resize-none outline-none leading-relaxed min-h-[24px] max-h-[200px]"
        />

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={!value.trim() || disabled}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white p-1.5 rounded-lg transition-colors flex-shrink-0 mb-0.5"
          aria-label="Send message"
        >
          <Send size={16} />
        </button>
      </div>
      <p className="text-xs text-slate-600 mt-1.5 text-center">
        Powered by LangGraph agents · Enter to send · Shift+Enter for new line
      </p>
    </div>
  )
}
