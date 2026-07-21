import { useState } from 'react'
import { FiSearch, FiTool } from 'react-icons/fi'
import EquipmentCard from '../components/EquipmentCard'
import EmptyState from '../components/EmptyState'
import { getEquipment } from '../services/api'

const SUGGESTIONS = ['P101', 'V204', 'M310', 'C88']

export default function Equipment() {
  const [query, setQuery] = useState('')
  const [equipment, setEquipment] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searched, setSearched] = useState(false)

  const runSearch = async (id) => {
    const trimmed = id.trim()
    if (!trimmed) return
    setLoading(true)
    setError(null)
    setSearched(true)
    try {
      const res = await getEquipment(trimmed)
      setEquipment(res)
    } catch (err) {
      setError(err?.message || 'Equipment not found')
      setEquipment(null)
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = (e) => {
    e.preventDefault()
    runSearch(query)
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h2 className="text-xl font-semibold text-steel-100">Equipment Search</h2>
        <p className="text-sm text-steel-500 mt-1">
          Look up equipment by ID to view maintenance and failure history
        </p>
      </div>

      <form onSubmit={onSubmit} className="flex gap-3">
        <div className="relative flex-1">
          <FiSearch className="absolute left-3.5 top-1/2 -translate-y-1/2 text-steel-500" size={16} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search Equipment (e.g. P101)"
            className="w-full rounded-xl bg-navy-900 border border-steel-700 pl-10 pr-4 py-3 text-sm text-steel-100 placeholder-steel-500 focus:outline-none focus:border-accent-500/60 focus:ring-1 focus:ring-accent-500/30"
          />
        </div>
        <button
          type="submit"
          disabled={!query.trim() || loading}
          className="px-5 rounded-xl bg-accent-500 text-white text-sm font-medium hover:bg-accent-600 transition-colors disabled:opacity-40"
        >
          Search
        </button>
      </form>

      <div className="flex flex-wrap gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => {
              setQuery(s)
              runSearch(s)
            }}
            className="text-xs px-3 py-1.5 rounded-full border border-steel-700 text-steel-300 hover:border-accent-500/50 hover:text-accent-400 transition-colors"
          >
            {s}
          </button>
        ))}
      </div>

      {loading && (
        <div className="rounded-2xl border border-steel-800 bg-navy-900 p-6 space-y-4 animate-pulse">
          <div className="h-5 w-40 bg-steel-800 rounded" />
          <div className="grid grid-cols-2 gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-14 bg-steel-800 rounded-lg" />
            ))}
          </div>
        </div>
      )}

      {!loading && error && (
        <EmptyState
          icon={FiTool}
          title="Equipment not found"
          description={error}
        />
      )}

      {!loading && !error && equipment && <EquipmentCard equipment={equipment} />}

      {!loading && !searched && (
        <EmptyState
          icon={FiSearch}
          title="Search for an equipment ID"
          description="Try one of the suggestions above or type an equipment ID to view its maintenance history."
        />
      )}
    </div>
  )
}
