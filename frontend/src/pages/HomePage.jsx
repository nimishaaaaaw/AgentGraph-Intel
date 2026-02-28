import React from 'react'
import { useNavigate } from 'react-router-dom'
import { MessageSquare, Network, Database, Zap, ArrowRight } from 'lucide-react'

const features = [
  {
    icon: Zap,
    title: 'Multi-Agent AI',
    description: 'LangGraph orchestrates specialized agents: Router, Researcher, KG Builder, and Analyst for intelligent query processing.',
    color: 'bg-indigo-600/20 text-indigo-400',
    badge: 'LangGraph',
  },
  {
    icon: Network,
    title: 'Knowledge Graph',
    description: 'Neo4j-powered knowledge graph extracts and connects entities from your documents for deep contextual understanding.',
    color: 'bg-emerald-600/20 text-emerald-400',
    badge: 'Neo4j',
  },
  {
    icon: Database,
    title: 'Advanced RAG',
    description: 'Hybrid retrieval combines dense vector search (ChromaDB) with sparse BM25, re-ranked by a cross-encoder for precision.',
    color: 'bg-purple-600/20 text-purple-400',
    badge: 'Hybrid Search',
  },
]

const techStack = [
  { label: 'FastAPI', color: 'bg-teal-600' },
  { label: 'LangGraph', color: 'bg-indigo-600' },
  { label: 'Neo4j', color: 'bg-emerald-600' },
  { label: 'ChromaDB', color: 'bg-purple-600' },
  { label: 'Gemini AI', color: 'bg-amber-600' },
  { label: 'React', color: 'bg-sky-600' },
  { label: 'Vite', color: 'bg-pink-600' },
  { label: 'Tailwind', color: 'bg-cyan-600' },
]

/**
 * Landing page with hero section, feature cards, and tech stack.
 */
export default function HomePage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-full px-6 py-12 max-w-5xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <div className="inline-flex items-center gap-2 bg-indigo-600/10 border border-indigo-500/20 rounded-full px-4 py-1.5 mb-6">
          <span className="text-xs font-medium text-indigo-400">✨ Powered by LangGraph + Neo4j</span>
        </div>
        <h1 className="text-5xl font-bold text-white mb-4 tracking-tight">
          🧠 AgentGraph <span className="text-indigo-400">Intel</span>
        </h1>
        <p className="text-xl text-slate-400 mb-8 max-w-2xl mx-auto leading-relaxed">
          Agentic AI Research Assistant powered by Knowledge Graphs. Upload documents,
          ask complex questions, and get intelligent answers backed by structured knowledge.
        </p>
        <div className="flex items-center justify-center gap-3">
          <button
            onClick={() => navigate('/chat')}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-3 rounded-xl transition-colors duration-200 text-lg"
          >
            Get Started <ArrowRight size={18} />
          </button>
          <button
            onClick={() => navigate('/documents')}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold px-6 py-3 rounded-xl transition-colors duration-200 text-lg border border-slate-600"
          >
            Upload Docs
          </button>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
        {features.map(({ icon: Icon, title, description, color, badge }) => (
          <div
            key={title}
            className="bg-slate-900 border border-slate-700/50 rounded-2xl p-6 hover:border-slate-600 transition-colors duration-200"
          >
            <div className={`w-11 h-11 rounded-xl ${color} flex items-center justify-center mb-4`}>
              <Icon size={22} />
            </div>
            <div className="flex items-center gap-2 mb-2">
              <h3 className="font-semibold text-slate-100">{title}</h3>
              <span className="text-xs bg-slate-700 text-slate-400 px-2 py-0.5 rounded-full">{badge}</span>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed">{description}</p>
          </div>
        ))}
      </div>

      {/* Architecture Overview */}
      <div className="bg-slate-900 border border-slate-700/50 rounded-2xl p-6 mb-12">
        <h2 className="text-lg font-semibold text-slate-200 mb-4">Architecture Overview</h2>
        <div className="font-mono text-xs text-slate-400 bg-slate-950 rounded-xl p-4 overflow-auto">
          <pre>{`
 User Query
     │
     ▼
 ┌─────────────────────────────────────┐
 │       LangGraph Orchestrator        │
 │  ┌─────────┐    ┌──────────────┐   │
 │  │ Router  │───▶│  Researcher  │   │
 │  └─────────┘    └──────┬───────┘   │
 │                        │           │
 │               ┌────────▼────────┐  │
 │               │   KG Builder    │  │
 │               └────────┬────────┘  │
 │                        │           │
 │               ┌────────▼────────┐  │
 │               │    Analyst      │  │
 │               └────────┬────────┘  │
 └────────────────────────┼───────────┘
                          │
              ┌───────────┴────────────┐
              │                        │
    ┌─────────▼──────┐    ┌────────────▼─────┐
    │  ChromaDB RAG  │    │  Neo4j KG Query  │
    │  (Dense+BM25)  │    │  (Graph Traversal)│
    └────────────────┘    └──────────────────┘
          `}</pre>
        </div>
      </div>

      {/* Tech Stack */}
      <div className="text-center">
        <h2 className="text-lg font-semibold text-slate-200 mb-4">Tech Stack</h2>
        <div className="flex flex-wrap justify-center gap-2">
          {techStack.map(({ label, color }) => (
            <span
              key={label}
              className={`${color} text-white text-sm font-medium px-4 py-1.5 rounded-full`}
            >
              {label}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
