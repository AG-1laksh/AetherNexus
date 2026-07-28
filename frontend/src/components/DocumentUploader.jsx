import React, { useRef, useState, useEffect } from 'react';
import { FiUploadCloud, FiFileText, FiCheckCircle, FiLoader, FiAlertCircle, FiDatabase } from 'react-icons/fi';
import { uploadAndProcessDocument, getDocumentStatus } from '../services/api';

export default function DocumentUploader({ documents, onDocumentAdded, onStatusChange }) {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const processFile = async (file) => {
    if (!file) return;
    setErrorMsg(null);
    setUploading(true);
    setProgress(10);

    try {
      const doc = await uploadAndProcessDocument(file, (percent) => {
        setProgress(Math.max(10, percent));
      });
      
      onDocumentAdded({
        id: doc.document_id,
        name: doc.filename || file.name,
        size: (file.size / (1024 * 1024)).toFixed(2) + ' MB',
        status: 'processing',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });
    } catch (err) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || 'Failed to upload document. Please verify document pipeline is running on port 8000.');
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) await processFile(file);
  };

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (file) await processFile(file);
    e.target.value = null;
  };

  // Poll processing documents until completed
  useEffect(() => {
    const processingDocs = documents.filter((d) => d.status === 'processing');
    if (processingDocs.length === 0) return;

    const interval = setInterval(async () => {
      for (const doc of processingDocs) {
        try {
          const statusInfo = await getDocumentStatus(doc.id);
          if (statusInfo.status === 'completed' || statusInfo.status === 'failed') {
            onStatusChange(doc.id, statusInfo.status);
          }
        } catch (e) {
          // Ignore intermittent networking faults during reload
        }
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [documents, onStatusChange]);

  return (
    <div className="uploader-container">
      <div className="panel-header">
        <h2 className="panel-title">
          <FiDatabase style={{ color: '#00f2ff' }} />
          <span>Knowledge Ingestion Hub</span>
        </h2>
        <span className="file-meta">{documents.length} Files Uploaded</span>
      </div>

      <div 
        className={`dropzone ${isDragging ? 'active' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          onChange={handleFileSelect}
          accept=".pdf,.docx,.xlsx,.xls,.png,.jpg,.jpeg"
        />
        
        {uploading ? (
          <div>
            <div className="dropzone-icon">
              <FiLoader className="spin" style={{ animation: 'spin 1s linear infinite' }} />
            </div>
            <p className="dropzone-text">Uploading & Ingesting ({progress}%)</p>
            <p className="dropzone-subtext">Transferring payload to backend...</p>
          </div>
        ) : (
          <div>
            <div className="dropzone-icon">
              <FiUploadCloud />
            </div>
            <p className="dropzone-text">Click or Drag industrial documents here</p>
            <p className="dropzone-subtext">Supports PDF, Word, Excel, & OCR Scans (PNG/JPG)</p>
          </div>
        )}
      </div>

      {errorMsg && (
        <div style={{ background: 'rgba(244, 63, 94, 0.12)', border: '1px solid #f43f5e', padding: '10px 14px', borderRadius: '10px', fontSize: '0.85rem', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FiAlertCircle style={{ color: '#f43f5e', fontSize: '18px', flexShrink: 0 }} />
          <span>{errorMsg}</span>
        </div>
      )}

      <div className="file-list">
        {documents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
            No technical manuals or inspection sheets indexed yet. Upload a PDF above to start querying!
          </div>
        ) : (
          documents.map((doc) => (
            <div className="file-card" key={doc.id}>
              <div className="file-info">
                <FiFileText style={{ fontSize: '22px', color: '#3b82f6', flexShrink: 0 }} />
                <div>
                  <p className="file-name" title={doc.name}>{doc.name}</p>
                  <p className="file-meta">{doc.size} • Uploaded {doc.timestamp}</p>
                </div>
              </div>

              <div>
                {doc.status === 'processing' && (
                  <span className="status-chip processing">Processing...</span>
                )}
                {(doc.status === 'completed' || doc.status === 'ready') && (
                  <span className="status-chip ready">
                    <FiCheckCircle style={{ display: 'inline', marginRight: '4px', verticalAlign: '-2px' }} />
                    Indexed
                  </span>
                )}
                {doc.status === 'failed' && (
                  <span className="status-chip failed">Failed</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
      
      <style>{`
        @keyframes spin {
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
