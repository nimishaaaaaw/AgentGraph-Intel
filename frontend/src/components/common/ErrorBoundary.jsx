import React from 'react'
import { AlertTriangle } from 'lucide-react'

/**
 * React error boundary that catches render errors and shows a fallback UI.
 */
export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary]', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-64 p-8 text-center">
          <AlertTriangle size={40} className="text-amber-400 mb-4" />
          <h2 className="text-lg font-semibold text-slate-200 mb-2">Something went wrong</h2>
          <p className="text-slate-400 text-sm mb-4 max-w-sm">
            {this.state.error?.message || 'An unexpected error occurred.'}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="btn-primary text-sm"
          >
            Try Again
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
