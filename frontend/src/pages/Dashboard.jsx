import { useEffect, useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts'
import { FiFileText, FiTool, FiClipboard, FiAlertTriangle } from 'react-icons/fi'
import DashboardCard from '../components/DashboardCard'
import { getDashboard } from '../services/api'

const PIE_COLORS = ['#f2691a', '#647186', '#8a97a8']

const tooltipStyle = {
  background: '#0f1c33',
  border: '1px solid #3a4657',
  borderRadius: 8,
  fontSize: 12,
  color: '#eef1f4',
}

function ChartCard({ title, children }) {
  return (
    <div className="rounded-xl border border-steel-800 bg-navy-900 p-5">
      <h3 className="text-sm font-semibold text-steel-200 mb-4">{title}</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          {children}
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    getDashboard()
      .then((res) => mounted && setData(res))
      .catch((err) => mounted && setError(err?.message || 'Failed to load dashboard'))
      .finally(() => mounted && setLoading(false))
    return () => {
      mounted = false
    }
  }, [])

  const totals = data?.totals
  const mostFailed = data?.most_failed_equipment
  const charts = data?.charts

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-steel-100">Dashboard</h2>
        <p className="text-sm text-steel-500 mt-1">
          Overview of documents, equipment, and maintenance activity
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-danger-500/30 bg-danger-500/10 text-danger-500 text-sm px-4 py-3">
          {error} — showing cached data where available.
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <DashboardCard
          label="Total Documents"
          value={totals?.documents ?? '—'}
          icon={FiFileText}
          loading={loading}
        />
        <DashboardCard
          label="Total Equipment"
          value={totals?.equipment ?? '—'}
          icon={FiTool}
          loading={loading}
        />
        <DashboardCard
          label="Maintenance Reports"
          value={totals?.maintenance_reports ?? '—'}
          icon={FiClipboard}
          loading={loading}
        />
        <DashboardCard
          label="Most Failed Equipment"
          value={mostFailed ? `${mostFailed.name} (${mostFailed.failures})` : '—'}
          icon={FiAlertTriangle}
          accent
          loading={loading}
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <ChartCard title="Equipment Failures">
          <BarChart data={charts?.equipment_failures || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2b3646" vertical={false} />
            <XAxis dataKey="name" stroke="#8a97a8" fontSize={11} tickLine={false} />
            <YAxis stroke="#8a97a8" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={tooltipStyle} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
            <Bar dataKey="failures" fill="#f2691a" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ChartCard>

        <ChartCard title="Documents Uploaded">
          <AreaChart data={charts?.documents_uploaded || []}>
            <defs>
              <linearGradient id="docsGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#f2691a" stopOpacity={0.4} />
                <stop offset="100%" stopColor="#f2691a" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#2b3646" vertical={false} />
            <XAxis dataKey="month" stroke="#8a97a8" fontSize={11} tickLine={false} />
            <YAxis stroke="#8a97a8" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={tooltipStyle} />
            <Area type="monotone" dataKey="count" stroke="#f2691a" fill="url(#docsGradient)" strokeWidth={2} />
          </AreaChart>
        </ChartCard>

        <ChartCard title="Maintenance Frequency">
          <PieChart>
            <Pie
              data={charts?.maintenance_frequency || []}
              dataKey="value"
              nameKey="name"
              innerRadius={55}
              outerRadius={85}
              paddingAngle={3}
            >
              {(charts?.maintenance_frequency || []).map((_, i) => (
                <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} stroke="none" />
              ))}
            </Pie>
            <Legend wrapperStyle={{ fontSize: 12, color: '#b0bac6' }} />
            <Tooltip contentStyle={tooltipStyle} />
          </PieChart>
        </ChartCard>
      </div>
    </div>
  )
}
