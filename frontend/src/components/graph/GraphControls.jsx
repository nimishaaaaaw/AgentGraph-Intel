import React from 'react'
import { Search, RefreshCw } from 'lucide-react'

const ENTITY_TYPES = ['Person', 'Organization', 'Concept', 'Technology', 'Event']

const TYPE_COLORS = {
  Person: 'bg-blue-500',
  Organization: 'bg-emerald-500',
  Concept: 'bg-purple-500',
  Technology: 'bg-amber-500',
  Event: 'bg-red-500',
}

/**
 * Graph control panel — filters by entity type and provides search.
 *
 * @param {Object} props
 * @param {Object} props.activeFilters - Map of type → boolean
 * @param {Function} props.onToggleFilter - Toggle filter for a type
 * @param {Function} props.onSearch - Search callback
 * @param {Function} props.onRefresh - Refresh graph data
 */
export default function GraphControls({ activeFilters, onToggleFilter, onSearch, onRefresh }) {
  return (
    <div className="flex flex-col gap-4 p-4 bg-slate-900 border-l border-slate-700/50 w-56">
      <h3 className="font-semibold text-slate-200 text-sm">Graph Controls</h3>

      {/* Search */}
      <div className="relative">
        <Search size={14} className="absolute left-2.5 top-2.5 text-slate-500" />
        <input
          type="text"
          placeholder="Search nodes..."
          onChange={(e) => onSearch?.(e.target.value)}
          className="w-full bg-slate-800 border border-slate-600 text-slate-100 text-sm rounded-lg pl-8 pr-3 py-2 focus:outline-none focus:border-indigo-500 placeholder-slate-500"
        />
      </div>

      {/* Entity type filters */}
      <div>
        <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">Filter by Type</p>
        <div className="space-y-1.5">
          {ENTITY_TYPES.map((type) => (
            <label key={type} className="flex items-center gap-2 cursor-pointer group">
              <input
                type="checkbox"
                checked={activeFilters?.[type] !== false}
                onChange={() => onToggleFilter?.(type)}
                className="sr-only"
              />
              <div
                className={`w-4 h-4 rounded flex items-center justify-center ${
                  activeFilters?.[type] !== false ? TYPE_COLORS[type] : 'bg-slate-700'
                } transition-colors`}
              >
                {activeFilters?.[type] !== false && (
                  <svg className="w-3 h-3 text-white" viewBox="0 0 12 12" fill="currentColor">
                    <path d="M10 3L5 8.5 2 5.5" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" />
                  </svg>
                )}
              </div>
              <span className="text-sm text-slate-300 group-hover:text-white transition-colors">
                {type}
              </span>
              <span className={`ml-auto w-2 h-2 rounded-full ${TYPE_COLORS[type]}`} />
            </label>
          ))}
        </div>
      </div>

      {/* Actions */}
      <button
        onClick={onRefresh}
        className="flex items-center justify-center gap-2 btn-secondary text-sm py-2"
      >
        <RefreshCw size={14} />
        Refresh Graph
      </button>
    </div>
  )
}
