import { FiCpu, FiWifi } from 'react-icons/fi'

export default function Navbar() {
  return (
    <header className="h-16 shrink-0 border-b border-steel-800 bg-navy-900/80 backdrop-blur flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-accent-500 flex items-center justify-center shadow-lg shadow-accent-500/20">
          <FiCpu className="text-white" size={18} />
        </div>
        <div>
          <h1 className="text-sm font-semibold text-steel-100 leading-tight">
            AetherNexus
          </h1>
          <p className="text-[11px] text-steel-400 leading-tight">
            Industrial Knowledge Intelligence
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 text-xs text-steel-400">
        <FiWifi className="text-ok-500" size={14} />
        <span className="hidden sm:inline">Backend connected</span>
      </div>
    </header>
  )
}
