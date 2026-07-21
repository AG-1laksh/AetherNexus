import { useEffect, useState } from 'react'
import GraphViewer from '../components/GraphViewer'
import { getGraph } from '../services/api'

export default function Graph() {
  const [graph, setGraph] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    getGraph()
      .then((res) => mounted && setGraph(res))
      .catch((err) => mounted && setError(err?.message || 'Failed to load graph'))
      .finally(() => mounted && setLoading(false))
    return () => {
      mounted = false
    }
  }, [])

  return (
    <div className="h-full flex flex-col space-y-4">
      <div>
        <h2 className="text-xl font-semibold text-steel-100">Knowledge Graph</h2>
        <p className="text-sm text-steel-500 mt-1">
          Explore relationships between equipment, components, and maintenance documents
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-danger-500/30 bg-danger-500/10 text-danger-500 text-sm px-4 py-3">
          {error} — showing cached data where available.
        </div>
      )}

      <div className="flex-1 min-h-[560px]">
        {loading ? (
          <div className="h-full rounded-2xl border border-steel-800 bg-navy-900 animate-pulse" />
        ) : (
          <GraphViewer graph={graph} />
        )}
      </div>
    </div>
  )
}
