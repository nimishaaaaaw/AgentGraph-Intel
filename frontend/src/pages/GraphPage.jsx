import React, { useEffect, useState } from 'react'
import GraphViewer from '../components/graph/GraphViewer'
import GraphControls from '../components/graph/GraphControls'
import ErrorBoundary from '../components/common/ErrorBoundary'
import Loader from '../components/common/Loader'
import { useGraph } from '../hooks/useGraph'
import { Network } from 'lucide-react'

/**
 * Knowledge graph visualization page.
 */
export default function GraphPage() {
  const { nodes, links, stats, isLoading, error, activeFilters, fetchGraph, search, toggleFilter } =
    useGraph()
  const [selectedNode, setSelectedNode] = useState(null)

  useEffect(() => {
    fetchGraph()
  }, [fetchGraph])

  return (
    <ErrorBoundary>
      <div className="flex h-[calc(100vh-4rem-3rem)]">
        {/* Main graph area */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-2 border-b border-slate-700/50 bg-slate-900/50">
            <div className="flex items-center gap-2">
              <Network size={16} className="text-indigo-400" />
              <h1 className="font-semibold text-slate-200 text-sm">Knowledge Graph</h1>
            </div>
            {stats && (
              <div className="flex items-center gap-4 text-xs text-slate-500">
                <span className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400 inline-block" />
                  {stats.node_count || nodes.length} nodes
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block" />
                  {stats.relationship_count || links.length} edges
                </span>
              </div>
            )}
          </div>

          {/* Graph canvas */}
          <div className="flex-1 bg-slate-950 relative">
            {isLoading ? (
              <div className="absolute inset-0 flex items-center justify-center">
                <Loader text="Loading graph..." />
              </div>
            ) : error ? (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-8">
                <p className="text-red-400 mb-2">Failed to load graph</p>
                <p className="text-slate-500 text-sm mb-4">{error}</p>
                <button onClick={fetchGraph} className="btn-secondary text-sm">
                  Retry
                </button>
              </div>
            ) : (
              <GraphViewer nodes={nodes} links={links} onNodeClick={setSelectedNode} />
            )}
          </div>

          {/* Selected node details */}
          {selectedNode && (
            <div className="border-t border-slate-700/50 bg-slate-900 px-4 py-3">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-slate-200 text-sm">
                    {selectedNode.name || selectedNode.id}
                  </p>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Type: {selectedNode.type} · ID: {selectedNode.id}
                  </p>
                  {selectedNode.description && (
                    <p className="text-xs text-slate-400 mt-1">{selectedNode.description}</p>
                  )}
                </div>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="text-slate-600 hover:text-slate-400 text-lg"
                >
                  ×
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Controls sidebar */}
        <GraphControls
          activeFilters={activeFilters}
          onToggleFilter={toggleFilter}
          onSearch={search}
          onRefresh={fetchGraph}
        />
      </div>
    </ErrorBoundary>
  )
}
