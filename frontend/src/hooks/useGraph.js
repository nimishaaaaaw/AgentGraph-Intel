/**
 * Custom hook for managing knowledge graph state.
 */
import { useState, useCallback } from 'react'
import { getGraphNodes, getGraphRelationships, getGraphStats, searchGraph } from '../services/api'

export function useGraph() {
  const [nodes, setNodes] = useState([])
  const [links, setLinks] = useState([])
  const [stats, setStats] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeFilters, setActiveFilters] = useState({
    Person: true,
    Organization: true,
    Concept: true,
    Technology: true,
    Event: true,
  })

  /**
   * Fetch all graph data from the API.
   */
  const fetchGraph = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [nodesData, relsData, statsData] = await Promise.all([
        getGraphNodes(),
        getGraphRelationships(),
        getGraphStats(),
      ])
      setNodes(nodesData)
      setLinks(relsData)
      setStats(statsData)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * Search the graph and highlight matching nodes.
   * @param {string} query
   */
  const search = useCallback(async (query) => {
    if (!query.trim()) return
    try {
      const results = await searchGraph(query)
      return results
    } catch (err) {
      setError(err.message)
    }
  }, [])

  const toggleFilter = useCallback((type) => {
    setActiveFilters((prev) => ({ ...prev, [type]: !prev[type] }))
  }, [])

  // Filtered nodes based on active type filters
  const filteredNodes = nodes.filter((n) => activeFilters[n.type] !== false)

  return {
    nodes: filteredNodes,
    links,
    stats,
    isLoading,
    error,
    activeFilters,
    fetchGraph,
    search,
    toggleFilter,
  }
}
