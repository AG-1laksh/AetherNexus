import { useCallback, useRef, useState } from 'react'
import { FiUploadCloud, FiFile, FiCheckCircle, FiXCircle, FiX } from 'react-icons/fi'
import toast from 'react-hot-toast'
import { uploadDocument } from '../services/api'

const ACCEPTED_EXT = ['.pdf', '.docx', '.xlsx', '.xls', '.png', '.jpg', '.jpeg']

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function UploadCard() {
  const [isDragging, setIsDragging] = useState(false)
  const [queue, setQueue] = useState([])
  const inputRef = useRef(null)

  const isAccepted = (file) => {
    const ext = `.${file.name.split('.').pop().toLowerCase()}`
    return ACCEPTED_EXT.includes(ext)
  }

  const handleFiles = useCallback((fileList) => {
    const files = Array.from(fileList)
    const accepted = files.filter(isAccepted)
    const rejected = files.filter((f) => !isAccepted(f))

    if (rejected.length) {
      toast.error(`Unsupported file type: ${rejected.map((f) => f.name).join(', ')}`)
    }
    if (!accepted.length) return

    const items = accepted.map((file) => ({
      id: `${file.name}-${file.size}-${Date.now()}-${Math.random()}`,
      file,
      status: 'uploading',
      progress: 0,
      error: null,
    }))
    setQueue((prev) => [...items, ...prev])

    items.forEach((item) => {
      uploadDocument(item.file, (evt) => {
        const progress = evt.total ? Math.round((evt.loaded / evt.total) * 100) : 50
        setQueue((prev) =>
          prev.map((q) => (q.id === item.id ? { ...q, progress } : q))
        )
      })
        .then(() => {
          setQueue((prev) =>
            prev.map((q) => (q.id === item.id ? { ...q, status: 'done', progress: 100 } : q))
          )
          toast.success(`${item.file.name} uploaded successfully`)
        })
        .catch((err) => {
          setQueue((prev) =>
            prev.map((q) =>
              q.id === item.id ? { ...q, status: 'error', error: err?.message } : q
            )
          )
          toast.error(`Failed to upload ${item.file.name}`)
        })
    })
  }, [])

  const onDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files?.length) handleFiles(e.dataTransfer.files)
  }

  const removeItem = (id) => setQueue((prev) => prev.filter((q) => q.id !== id))

  return (
    <div className="space-y-6">
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={`relative cursor-pointer rounded-2xl border-2 border-dashed p-12 text-center transition-colors ${
          isDragging
            ? 'border-accent-500 bg-accent-500/5'
            : 'border-steel-700 bg-navy-900 hover:border-steel-500'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept={ACCEPTED_EXT.join(',')}
          className="hidden"
          onChange={(e) => e.target.files?.length && handleFiles(e.target.files)}
        />
        <div className="mx-auto w-16 h-16 rounded-full bg-accent-500/10 flex items-center justify-center mb-4">
          <FiUploadCloud className="text-accent-400" size={28} />
        </div>
        <p className="text-steel-100 font-medium">
          Drag & drop industrial documents here, or click to browse
        </p>
        <p className="text-steel-400 text-sm mt-2">
          Supports PDF, Word, Excel, and image files (PNG, JPG)
        </p>
      </div>

      {queue.length > 0 && (
        <div className="space-y-2">
          {queue.map((item) => (
            <div
              key={item.id}
              className="flex items-center gap-3 rounded-lg border border-steel-800 bg-navy-900 px-4 py-3 animate-fade-in"
            >
              <FiFile className="text-steel-400 shrink-0" size={18} />
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm text-steel-100 truncate">{item.file.name}</p>
                  <span className="text-xs text-steel-500 shrink-0">
                    {formatSize(item.file.size)}
                  </span>
                </div>
                {item.status === 'uploading' && (
                  <div className="mt-2 h-1.5 rounded-full bg-steel-800 overflow-hidden">
                    <div
                      className="h-full bg-accent-500 transition-all duration-200"
                      style={{ width: `${item.progress}%` }}
                    />
                  </div>
                )}
                {item.status === 'error' && (
                  <p className="text-xs text-danger-500 mt-1">Upload failed. Try again.</p>
                )}
              </div>
              {item.status === 'done' && (
                <FiCheckCircle className="text-ok-500 shrink-0" size={20} />
              )}
              {item.status === 'error' && (
                <FiXCircle className="text-danger-500 shrink-0" size={20} />
              )}
              <button
                onClick={() => removeItem(item.id)}
                className="text-steel-500 hover:text-steel-200 shrink-0"
                aria-label="Remove"
              >
                <FiX size={16} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
