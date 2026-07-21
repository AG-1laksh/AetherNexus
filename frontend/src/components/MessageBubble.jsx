import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { FiUser, FiCpu, FiCopy, FiCheck, FiFileText, FiTag } from 'react-icons/fi'

function ConfidenceBadge({ confidence }) {
  const pct = Math.round(confidence * 100)
  const color =
    pct >= 85 ? 'text-ok-500 bg-ok-500/10' : pct >= 60 ? 'text-warn-500 bg-warn-500/10' : 'text-danger-500 bg-danger-500/10'
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${color}`}>
      {pct}% confidence
    </span>
  )
}

export default function MessageBubble({ role, content, contextChunks, graphEntities, isLoading }) {
  const [copied, setCopied] = useState(false)
  const isUser = role === 'user'

  const handleCopy = () => {
    const text = contextChunks?.map((c) => c.text_snippet).join('\n\n') || content || ''
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''} animate-fade-in`}>
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
          isUser ? 'bg-steel-700 text-steel-200' : 'bg-accent-500/15 text-accent-400'
        }`}
      >
        {isUser ? <FiUser size={15} /> : <FiCpu size={15} />}
      </div>

      <div className={`max-w-[75%] ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-2`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? 'bg-accent-500 text-white rounded-tr-sm'
              : 'bg-navy-800 border border-steel-800 text-steel-100 rounded-tl-sm'
          }`}
        >
          {isLoading ? (
            <div className="flex gap-1.5 py-1">
              <span className="w-2 h-2 rounded-full bg-steel-400 animate-pulse-dot" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 rounded-full bg-steel-400 animate-pulse-dot" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 rounded-full bg-steel-400 animate-pulse-dot" style={{ animationDelay: '300ms' }} />
            </div>
          ) : isUser ? (
            <div className="prose-chat">
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          ) : (
            <div className="space-y-3">
              {content && <p className="text-steel-300 text-xs">{content}</p>}
              {contextChunks?.length ? (
                contextChunks.map((chunk, i) => (
                  <div key={i} className="border-l-2 border-accent-500/40 pl-3">
                    <ReactMarkdown>{chunk.text_snippet}</ReactMarkdown>
                  </div>
                ))
              ) : (
                <p className="text-steel-400">No matching context found in the Knowledge Graph.</p>
              )}
            </div>
          )}
        </div>

        {!isLoading && !isUser && contextChunks?.length > 0 && (
          <div className="flex flex-wrap items-center gap-2">
            {contextChunks.map((chunk, i) => (
              <span
                key={i}
                className="flex items-center gap-1.5 text-xs text-steel-400 bg-steel-800/60 px-2 py-0.5 rounded-full"
              >
                <FiFileText size={11} />
                {chunk.filename}
                <ConfidenceBadge confidence={chunk.confidence_score} />
              </span>
            ))}
          </div>
        )}

        {!isLoading && !isUser && graphEntities?.length > 0 && (
          <div className="flex flex-wrap items-center gap-2">
            {graphEntities.map((entity, i) => (
              <span
                key={i}
                className="flex items-center gap-1 text-xs text-accent-400 bg-accent-500/10 px-2 py-0.5 rounded-full"
              >
                <FiTag size={11} />
                {entity.name}
              </span>
            ))}
          </div>
        )}

        {!isLoading && !isUser && (
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 text-xs text-steel-500 hover:text-steel-200 transition-colors"
          >
            {copied ? <FiCheck size={12} /> : <FiCopy size={12} />}
            {copied ? 'Copied' : 'Copy answer'}
          </button>
        )}
      </div>
    </div>
  )
}
