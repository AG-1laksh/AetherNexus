import { useEffect, useRef, useState } from 'react'
import { FiSend } from 'react-icons/fi'
import MessageBubble from './MessageBubble'
import { sendChat } from '../services/api'

const SUGGESTIONS = [
  'Why did Pump P101 fail?',
  'What is the maintenance history for Valve V204?',
  'Recommend a preventive maintenance schedule for Motor M310',
]

export default function ChatBox() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isSending, setIsSending] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, isSending])

  const submit = async (question) => {
    const text = question.trim()
    if (!text || isSending) return

    setMessages((prev) => [...prev, { id: Date.now(), role: 'user', content: text }])
    setInput('')
    setIsSending(true)
    const loadingId = `loading-${Date.now()}`
    setMessages((prev) => [...prev, { id: loadingId, role: 'assistant', isLoading: true }])

    try {
      const res = await sendChat(text)
      setMessages((prev) =>
        prev.map((m) =>
          m.id === loadingId
            ? {
                id: loadingId,
                role: 'assistant',
                content: res.message,
                contextChunks: res.context_chunks,
                graphEntities: res.graph_entities,
              }
            : m
        )
      )
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === loadingId
            ? { id: loadingId, role: 'assistant', content: 'Something went wrong. Please try again.' }
            : m
        )
      )
    } finally {
      setIsSending(false)
    }
  }

  const onSubmit = (e) => {
    e.preventDefault()
    submit(input)
  }

  return (
    <div className="flex flex-col h-full rounded-2xl border border-steel-800 bg-navy-900 overflow-hidden">
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center gap-4 py-12">
            <div className="w-14 h-14 rounded-full bg-accent-500/10 flex items-center justify-center">
              <FiSend className="text-accent-400" size={22} />
            </div>
            <div>
              <p className="text-steel-200 font-medium">Ask about equipment, faults, or maintenance</p>
              <p className="text-steel-500 text-sm mt-1">
                Answers are grounded in your uploaded documents with citations.
              </p>
            </div>
            <div className="flex flex-wrap justify-center gap-2 mt-2 max-w-lg">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => submit(s)}
                  className="text-xs px-3 py-1.5 rounded-full border border-steel-700 text-steel-300 hover:border-accent-500/50 hover:text-accent-400 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m) => <MessageBubble key={m.id} {...m} />)
        )}
      </div>

      <form onSubmit={onSubmit} className="border-t border-steel-800 p-4 flex items-end gap-3">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              submit(input)
            }
          }}
          placeholder="Ask about equipment failures, maintenance schedules, or root causes..."
          rows={1}
          className="flex-1 resize-none rounded-xl bg-navy-800 border border-steel-700 px-4 py-3 text-sm text-steel-100 placeholder-steel-500 focus:outline-none focus:border-accent-500/60 focus:ring-1 focus:ring-accent-500/30"
        />
        <button
          type="submit"
          disabled={!input.trim() || isSending}
          className="w-11 h-11 shrink-0 rounded-xl bg-accent-500 text-white flex items-center justify-center disabled:opacity-40 disabled:cursor-not-allowed hover:bg-accent-600 transition-colors"
        >
          <FiSend size={17} />
        </button>
      </form>
    </div>
  )
}
