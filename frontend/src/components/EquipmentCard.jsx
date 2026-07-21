import { FiMapPin, FiTool, FiAlertTriangle, FiCalendar, FiCheckCircle } from 'react-icons/fi'

function Stat({ icon: Icon, label, value }) {
  return (
    <div className="flex items-start gap-3 rounded-lg bg-navy-800 border border-steel-800 px-4 py-3">
      <Icon className="text-accent-400 mt-0.5 shrink-0" size={16} />
      <div>
        <p className="text-xs text-steel-400">{label}</p>
        <p className="text-sm text-steel-100 font-medium mt-0.5">{value}</p>
      </div>
    </div>
  )
}

export default function EquipmentCard({ equipment }) {
  if (!equipment) return null
  const {
    id,
    name,
    location,
    maintenance_count,
    failure_count,
    last_inspection,
    last_maintenance,
    status,
  } = equipment

  return (
    <div className="rounded-2xl border border-steel-800 bg-navy-900 p-6 animate-fade-in">
      <div className="flex items-start justify-between mb-5">
        <div>
          <h3 className="text-lg font-semibold text-steel-100">{name}</h3>
          <p className="text-xs text-steel-500 mt-0.5">ID: {id}</p>
        </div>
        {status && (
          <span className="flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full bg-ok-500/10 text-ok-500">
            <FiCheckCircle size={12} />
            {status}
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Stat icon={FiMapPin} label="Location" value={location} />
        <Stat icon={FiTool} label="Maintenance Count" value={maintenance_count} />
        <Stat icon={FiAlertTriangle} label="Failure Count" value={failure_count} />
        <Stat icon={FiCalendar} label="Last Inspection" value={last_inspection} />
        <Stat icon={FiCalendar} label="Last Maintenance" value={last_maintenance} />
      </div>
    </div>
  )
}
