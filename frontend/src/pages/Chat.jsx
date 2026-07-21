import ChatBox from '../components/ChatBox'

export default function Chat() {
  return (
    <div className="h-full flex flex-col space-y-4 max-w-4xl mx-auto">
      <div>
        <h2 className="text-xl font-semibold text-steel-100">AI Assistant</h2>
        <p className="text-sm text-steel-500 mt-1">
          Ask natural-language questions about equipment, faults, and maintenance history
        </p>
      </div>
      <div className="flex-1 min-h-[520px]">
        <ChatBox />
      </div>
    </div>
  )
}
