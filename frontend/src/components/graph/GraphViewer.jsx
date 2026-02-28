import React, { useRef, useCallback, useState } from 'react'

// Color mapping by entity type
const NODE_COLORS = {
  Person: '#3b82f6',       // blue
  Organization: '#10b981', // emerald
  Concept: '#8b5cf6',      // purple
  Technology: '#f59e0b',   // amber
  Event: '#ef4444',        // red
  default: '#6b7280',      // gray
}

/**
 * Force-directed knowledge graph visualization.
 * Uses a canvas-based renderer via react-force-graph-2d.
 *
 * @param {Object} props
 * @param {Array} props.nodes - Graph nodes
 * @param {Array} props.links - Graph relationships
 * @param {Function} props.onNodeClick - Callback when node is clicked
 */
export default function GraphViewer({ nodes = [], links = [], onNodeClick }) {
  const fgRef = useRef()
  const [ForceGraph, setForceGraph] = useState(null)
  const [highlighted, setHighlighted] = useState(null)

  // Lazy-load react-force-graph-2d to avoid SSR issues
  React.useEffect(() => {
    import('react-force-graph-2d').then((mod) => {
      setForceGraph(() => mod.default)
    })
  }, [])

  const handleNodeClick = useCallback(
    (node) => {
      setHighlighted(node.id)
      onNodeClick?.(node)
    },
    [onNodeClick]
  )

  const getNodeColor = useCallback(
    (node) => (highlighted === node.id ? '#f472b6' : NODE_COLORS[node.type] || NODE_COLORS.default),
    [highlighted]
  )

  // Format graph data for react-force-graph-2d
  const graphData = {
    nodes: nodes.map((n) => ({ ...n, id: n.id || n.name })),
    links: links.map((l) => ({
      source: l.source || l.from,
      target: l.target || l.to,
      label: l.type || l.relationship,
    })),
  }

  if (nodes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center py-16">
        <span className="text-5xl mb-4">🕸️</span>
        <h3 className="text-lg font-medium text-slate-300 mb-2">No graph data yet</h3>
        <p className="text-slate-500 text-sm max-w-xs">
          Upload documents and chat with the assistant to build the knowledge graph.
        </p>
      </div>
    )
  }

  if (!ForceGraph) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-slate-400">Loading graph engine...</div>
      </div>
    )
  }

  return (
    <ForceGraph
      ref={fgRef}
      graphData={graphData}
      nodeColor={getNodeColor}
      nodeLabel={(node) => `${node.type}: ${node.name || node.id}`}
      linkLabel={(link) => link.label || ''}
      nodeRelSize={6}
      linkColor={() => '#475569'}
      linkWidth={1.5}
      backgroundColor="#0f172a"
      onNodeClick={handleNodeClick}
      nodeCanvasObject={(node, ctx, globalScale) => {
        const label = node.name || node.id || ''
        const fontSize = Math.max(10 / globalScale, 4)
        ctx.font = `${fontSize}px Inter, sans-serif`
        const color = getNodeColor(node)

        // Draw node circle
        ctx.beginPath()
        ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI)
        ctx.fillStyle = color
        ctx.fill()
        ctx.strokeStyle = 'rgba(255,255,255,0.2)'
        ctx.lineWidth = 0.5
        ctx.stroke()

        // Draw label
        if (globalScale > 0.8) {
          ctx.textAlign = 'center'
          ctx.textBaseline = 'top'
          ctx.fillStyle = '#e2e8f0'
          ctx.fillText(label.slice(0, 20), node.x, node.y + 7)
        }
      }}
    />
  )
}
