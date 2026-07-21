import { useMemo, useState, useCallback } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'

const TYPE_COLORS = {
  equipment: { bg: '#16294a', border: '#f2691a', text: '#eef1f4' },
  document: { bg: '#1f2733', border: '#647186', text: '#d3d9e0' },
  default: { bg: '#0f1c33', border: '#3a4657', text: '#eef1f4' },
}

function toFlowNodes(rawNodes) {
  return rawNodes.map((n) => {
    const type = n.data?.type || 'default'
    const colors = TYPE_COLORS[type] || TYPE_COLORS.default
    return {
      id: n.id,
      position: n.position || { x: 0, y: 0 },
      data: { label: n.data?.label || n.id, raw: n },
      style: {
        background: colors.bg,
        border: `1.5px solid ${colors.border}`,
        color: colors.text,
        borderRadius: 10,
        padding: '8px 14px',
        fontSize: 12,
        fontWeight: 500,
      },
    }
  })
}

function toFlowEdges(rawEdges) {
  return rawEdges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    label: e.label,
    animated: true,
    style: { stroke: '#4c5a6e' },
    labelStyle: { fill: '#b0bac6', fontSize: 10 },
    labelBgStyle: { fill: '#0a1224' },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#4c5a6e' },
  }))
}

export default function GraphViewer({ graph }) {
  const initialNodes = useMemo(() => toFlowNodes(graph?.nodes || []), [graph])
  const initialEdges = useMemo(() => toFlowEdges(graph?.edges || []), [graph])
  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, , onEdgesChange] = useEdgesState(initialEdges)
  const [selected, setSelected] = useState(null)

  const onNodeClick = useCallback((_, node) => setSelected(node.data.raw), [])

  return (
    <div className="relative h-full rounded-2xl border border-steel-800 bg-navy-900 overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onPaneClick={() => setSelected(null)}
        fitView
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#2b3646" gap={20} />
        <Controls className="!bg-navy-800 !border !border-steel-700 [&>button]:!bg-navy-800 [&>button]:!border-steel-700 [&>button]:!text-steel-300" />
        <MiniMap
          pannable
          zoomable
          maskColor="rgba(6,11,22,0.75)"
          nodeColor={(n) => TYPE_COLORS[n.data?.raw?.data?.type]?.border || '#3a4657'}
          className="!bg-navy-900 !border !border-steel-700"
        />
      </ReactFlow>

      {selected && (
        <div className="absolute top-4 right-4 w-64 rounded-xl border border-steel-700 bg-navy-800/95 backdrop-blur p-4 shadow-xl animate-fade-in">
          <p className="text-xs text-steel-500 uppercase tracking-wide">
            {selected.data?.type || 'node'}
          </p>
          <p className="text-sm font-semibold text-steel-100 mt-1">{selected.data?.label}</p>
          <p className="text-xs text-steel-500 mt-2 break-all">ID: {selected.id}</p>
        </div>
      )}
    </div>
  )
}
