import axios from 'axios';

// Backend endpoints configured for dual-service architecture
const PIPELINE_URL = import.meta.env.VITE_PIPELINE_URL || 'http://127.0.0.1:8000';
const GRAPH_URL = import.meta.env.VITE_GRAPH_URL || 'http://127.0.0.1:8010';

export const pipelineClient = axios.create({
  baseURL: PIPELINE_URL,
  timeout: 60000,
});

export const graphClient = axios.create({
  baseURL: GRAPH_URL,
  timeout: 45000,
});

/**
 * Uploads a document file (PDF/Word/Excel) to the ingestion pipeline service.
 */
export async function uploadAndProcessDocument(file, onProgress) {
  const formData = new FormData();
  formData.append('file', file);

  // 1. Send multipart file to /upload
  const uploadRes = await pipelineClient.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percentCompleted);
      }
    },
  });

  const { document_id, filename } = uploadRes.data;

  // 2. Trigger async OCR & Entity processing pipeline
  await pipelineClient.post('/process', { document_id });

  return { document_id, filename, status: 'processing' };
}

/**
 * Checks document status until completion or failure.
 */
export async function getDocumentStatus(documentId) {
  const { data } = await pipelineClient.get(`/document/${documentId}`);
  return data;
}

/**
 * Submits a question to the GraphRAG service powered by Neo4j & Gemini API.
 */
export async function queryGraphRAG(question, topK = 4) {
  const { data } = await graphClient.post('/api/query/', {
    question,
    top_k: topK,
  });
  return data;
}
