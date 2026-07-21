export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center text-center gap-3 py-16 px-6">
      {Icon && (
        <div className="w-14 h-14 rounded-full bg-steel-800 flex items-center justify-center">
          <Icon className="text-steel-400" size={22} />
        </div>
      )}
      <div>
        <p className="text-steel-200 font-medium">{title}</p>
        {description && <p className="text-steel-500 text-sm mt-1 max-w-sm">{description}</p>}
      </div>
      {action}
    </div>
  )
}
