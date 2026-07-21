import UploadCard from '../components/UploadCard'

export default function Upload() {
  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h2 className="text-xl font-semibold text-steel-100">Upload Documents</h2>
        <p className="text-sm text-steel-500 mt-1">
          Upload PDFs, Excel sheets, or scanned images for AI-powered extraction and indexing
        </p>
      </div>
      <UploadCard />
    </div>
  )
}
