import React, { useState } from 'react';
import Navbar from './components/Navbar';
import DocumentUploader from './components/DocumentUploader';
import ChatInterface from './components/ChatInterface';

export default function App() {
  const [documents, setDocuments] = useState([]);

  const handleDocumentAdded = (newDoc) => {
    setDocuments((prev) => [newDoc, ...prev]);
  };

  const handleStatusChange = (docId, newStatus) => {
    setDocuments((prev) =>
      prev.map((doc) => (doc.id === docId ? { ...doc, status: newStatus } : doc))
    );
  };

  const indexedCount = documents.filter((d) => d.status === 'ready' || d.status === 'completed').length;

  return (
    <div className="app-container">
      <Navbar documentsCount={indexedCount} />
      
      <main className="workspace-main">
        <section className="panel-left">
          <DocumentUploader 
            documents={documents} 
            onDocumentAdded={handleDocumentAdded}
            onStatusChange={handleStatusChange} 
          />
        </section>

        <section className="panel-right">
          <ChatInterface documents={documents} />
        </section>
      </main>
    </div>
  );
}
