/**
 * Custom hook for managing chat state and interactions.
 */
import { useState, useCallback } from 'react'
import { sendMessage } from '../services/api'

/**
 * @typedef {Object} Message
 * @property {string} id - Unique message ID
 * @property {'user'|'assistant'} role - Message sender
 * @property {string} content - Message text
 * @property {Array} [sources] - Source citations
 * @property {Array} [agent_trail] - Agents involved in response
 * @property {Array} [entities] - Extracted entities
 * @property {number} timestamp - Unix timestamp
 */

export function useChat() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const addMessage = useCallback((message) => {
    setMessages((prev) => [...prev, { ...message, id: Date.now().toString(), timestamp: Date.now() }])
  }, [])

  /**
   * Send a message and receive an AI response.
   * @param {string} query - User's message
   */
  const send = useCallback(async (query) => {
    if (!query.trim() || isLoading) return

    // Add user message immediately
    addMessage({ role: 'user', content: query })
    setIsLoading(true)
    setError(null)

    try {
      const data = await sendMessage(query)
      addMessage({
        role: 'assistant',
        content: data.answer,
        sources: data.sources || [],
        agent_trail: data.steps_taken || [],
        entities: data.entities || [],
      })
    } catch (err) {
      setError(err.message)
      addMessage({
        role: 'assistant',
        content: `⚠️ Error: ${err.message}`,
        sources: [],
        agent_trail: [],
        entities: [],
      })
    } finally {
      setIsLoading(false)
    }
  }, [isLoading, addMessage])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return { messages, isLoading, error, send, clearMessages }
}
