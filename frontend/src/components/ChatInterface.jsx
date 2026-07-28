import React, { useState, useRef, useEffect } from 'react';
import { FiSend, FiMessageSquare, FiZap, FiAlertCircle } from 'react-icons/fi';
import MessageBubble from './MessageBubble';
import { queryGraphRAG } from '../services/api';

export default function ChatInterface({ documents }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'bot',
      content: '### Welcome to Aether-Nexus Industrial Copilot ⚙️\n\nI am powered by **Google Gemini AI** connected directly to your **Neo4j Knowledge Graph**. \n\nUpload your document, book, or technical manual on the left, then ask me anything! Example queries:\n- *What are the main topics and core concepts covered in the uploaded document?*\n- *Summarize the key procedures, ethics, guidelines, and takeaways.*',
      citations: [],
      entities: []
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();
    const newUserMsg = { id: Date.now(), role: 'user', content: userText };
    setMessages((prev) => [...prev, newUserMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await queryGraphRAG(userText);
      const newBotMsg = {
        id: Date.now() + 1,
        role: 'bot',
        content: response.answer || 'I examined the knowledge graph and retrieved the context below:',
        citations: response.context_chunks || [],
        entities: response.graph_entities || []
      };
      setMessages((prev) => [...prev, newBotMsg]);
    } catch (error) {
      console.error(error);
      const errorMsg = {
        id: Date.now() + 1,
        role: 'bot',
        content: `⚠️ **Connection Failed**: Could not query the backend server on port 8010. Please verify that \`main.py\` is running via Uvicorn.\n\n*Error details:* \`${error.message}\``,
        citations: [],
        entities: []
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-title-group">
          <h2 className="panel-title">
            <FiMessageSquare style={{ color: '#3b82f6' }} />
            <span>Industrial Knowledge Graph Assistant</span>
          </h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Powered by Google Gemini & Neo4j Vector Embeddings
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '4px 12px', borderRadius: '20px', background: 'rgba(0, 242, 255, 0.08)', border: '1px solid rgba(0, 242, 255, 0.25)', color: '#00f2ff', fontSize: '0.8rem', fontWeight: 500 }}>
          <FiZap />
          <span>Gemini 1.5 Active</span>
        </div>
      </div>

      <div className="chat-messages-area">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        
        {loading && (
          <div className="msg-row bot">
            <div className="msg-avatar" style={{ background: 'var(--accent-blue-gradient)', color: '#000' }}>
              <FiZap className="spin" style={{ animation: 'spin 1.5s linear infinite' }} />
            </div>
            <div className="msg-content-card" style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#94a3b8' }}>
              <span>Traversing Neo4j Graph & synthesizing Gemini response...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-toolbar" onSubmit={handleSend}>
        <div className="input-box-wrapper">
          <input
            type="text"
            className="chat-input"
            placeholder={loading ? 'Synthesizing response from technical documentation...' : 'Ask a technical question about uploaded valves, equipment, or inspection sheets...'}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button type="submit" className="send-btn" disabled={loading || !input.trim()} title="Send Query">
            <FiSend />
          </button>
        </div>
      </form>
    </div>
  );
}
