import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { FiUser, FiCpu, FiTag, FiBookOpen, FiChevronDown, FiChevronUp } from 'react-icons/fi';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  const [showCitations, setShowCitations] = useState(true);

  return (
    <div className={`msg-row ${isUser ? 'user' : 'bot'}`}>
      <div className="msg-avatar">
        {isUser ? <FiUser /> : <FiCpu />}
      </div>

      <div className="msg-content-card">
        {isUser ? (
          <div>{message.content}</div>
        ) : (
          <div className="markdown-body">
            <ReactMarkdown>{message.content || 'No text content returned.'}</ReactMarkdown>
            
            {/* Knowledge Graph Entities & Source Citations Footer */}
            {(message.entities?.length > 0 || message.citations?.length > 0) && (
              <div className="msg-metadata-footer">
                
                {/* Extracted Graph Entities */}
                {message.entities?.length > 0 && (
                  <div className="entities-bar">
                    <span className="entity-label">
                      <FiTag style={{ color: '#f59e0b' }} />
                      Graph Entities:
                    </span>
                    {message.entities.map((ent, idx) => (
                      <span className="entity-pill" key={idx}>
                        {ent.name || ent}
                      </span>
                    ))}
                  </div>
                )}

                {/* Retrieved Document Citations */}
                {message.citations?.length > 0 && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div 
                      style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', color: '#94a3b8', fontSize: '0.8rem', fontWeight: 600 }}
                      onClick={() => setShowCitations(!showCitations)}
                    >
                      <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#a5f3fc' }}>
                        <FiBookOpen style={{ color: '#00f2ff' }} />
                        Retrieved RAG Sources ({message.citations.length})
                      </span>
                      {showCitations ? <FiChevronUp /> : <FiChevronDown />}
                    </div>

                    {showCitations && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '4px' }}>
                        {message.citations.map((cite, index) => (
                          <div className="citation-card" key={index}>
                            <div className="citation-header">
                              <span>📄 {cite.filename}</span>
                              <span style={{ fontSize: '0.75rem', color: '#10b981' }}>
                                Confidence: {Math.round((cite.confidence_score || 0.95) * 100)}%
                              </span>
                            </div>
                            <p className="citation-snippet">"{cite.text_snippet}"</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
