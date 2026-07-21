import axios from 'axios'

// document_pipeline: parsing/OCR/upload service
const PIPELINE_BASE_URL = import.meta.env.VITE_PIPELINE_BASE_URL || 'http://127.0.0.1:8000'
// backend: Neo4j GraphRAG service (query, ingest, dashboard, equipment, graph)
const GRAPH_BASE_URL = import.meta.env.VITE_GRAPH_BASE_URL || 'http://127.0.0.1:8010'

export const pipelineApi = axios.create({
  baseURL: PIPELINE_BASE_URL,
  timeout: 30000,
})

export const graphApi = axios.create({
  baseURL: GRAPH_BASE_URL,
  timeout: 30000,
})

export async function uploadDocument(file, onUploadProgress) {
  const formData = new FormData()
  formData.append('file', file)
  const { data: uploaded } = await pipelineApi.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress,
  })

  await pipelineApi.post('/process', { document_id: uploaded.document_id })

  return uploaded
}

export async function sendChat(question, topK = 3) {
  const { data } = await graphApi.post('/api/query/', { question, top_k: topK })
  return data
}

export async function getDashboard() {
  const { data } = await graphApi.get('/api/dashboard/')
  return data
}

export async function getEquipment(id) {
  const { data } = await graphApi.get(`/api/equipment/${encodeURIComponent(id)}`)
  return data
}

export async function getGraph() {
  const { data } = await graphApi.get('/api/graph/')
  return data
}
