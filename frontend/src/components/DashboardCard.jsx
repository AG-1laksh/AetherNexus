export default function DashboardCard({ label, value, icon: Icon, accent = false, loading = false }) {
  return (
    <div className="rounded-xl border border-steel-800 bg-navy-900 p-5 flex items-center gap-4">
      <div
        className={`w-11 h-11 rounded-lg flex items-center justify-center shrink-0 ${
          accent ? 'bg-accent-500/15 text-accent-400' : 'bg-steel-800 text-steel-300'
        }`}
      >
        {Icon && <Icon size={20} />}
      </div>
      <div className="min-w-0">
        <p className="text-xs text-steel-400 truncate">{label}</p>
        {loading ? (
          <div className="h-6 w-16 mt-1 rounded bg-steel-800 animate-pulse" />
        ) : (
          <p className="text-2xl font-semibold text-steel-100 truncate">{value}</p>
        )}
      </div>
    </div>
  )
}
