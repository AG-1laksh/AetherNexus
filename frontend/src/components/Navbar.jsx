import React from 'react';
import { FiCpu, FiActivity, FiShield } from 'react-icons/fi';

export default function Navbar({ documentsCount }) {
  return (
    <header className="navbar">
      <div className="brand-section">
        <div className="brand-icon-wrap">
          <FiCpu />
        </div>
        <div>
          <h1 className="brand-title">Aether-Nexus</h1>
          <p className="brand-subtitle">Industrial Knowledge Intelligence & GraphRAG</p>
        </div>
      </div>

      <div className="nav-status">
        <div className="status-badge" title="Neo4j AuraDB & Gemini AI Integration">
          <span className="status-dot"></span>
          <span>Neo4j Graph Active</span>
        </div>
        
        <div className="status-badge" style={{ borderColor: 'rgba(59, 130, 246, 0.3)' }}>
          <FiActivity style={{ color: '#3b82f6', fontSize: '15px' }} />
          <span>{documentsCount} Document{documentsCount === 1 ? '' : 's'} Indexed</span>
        </div>

        <div className="status-badge" style={{ background: 'rgba(0, 242, 255, 0.05)', color: '#00e5ff' }}>
          <FiShield style={{ fontSize: '15px' }} />
          <span>Gemini AI Connected</span>
        </div>
      </div>
    </header>
  );
}
