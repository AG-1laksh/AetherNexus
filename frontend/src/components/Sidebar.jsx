import { NavLink } from 'react-router-dom'
import {
  FiGrid,
  FiUploadCloud,
  FiMessageSquare,
  FiSearch,
  FiShare2,
} from 'react-icons/fi'

const links = [
  { to: '/', label: 'Dashboard', icon: FiGrid, end: true },
  { to: '/upload', label: 'Upload', icon: FiUploadCloud },
  { to: '/chat', label: 'AI Chat', icon: FiMessageSquare },
  { to: '/equipment', label: 'Equipment', icon: FiSearch },
  { to: '/graph', label: 'Knowledge Graph', icon: FiShare2 },
]

export default function Sidebar({ onNavigate }) {
  return (
    <nav className="flex flex-col gap-1 p-3">
      {links.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          onClick={onNavigate}
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              isActive
                ? 'bg-accent-500/15 text-accent-400 border border-accent-500/30'
                : 'text-steel-400 border border-transparent hover:bg-steel-800/60 hover:text-steel-100'
            }`
          }
        >
          <Icon size={17} />
          {label}
        </NavLink>
      ))}
    </nav>
  )
}
