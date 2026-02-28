import React from 'react'

/**
 * Spinning loader with optional text.
 *
 * @param {Object} props
 * @param {string} [props.text='Processing...'] - Loading text
 * @param {string} [props.size='md'] - Size: 'sm' | 'md' | 'lg'
 */
export default function Loader({ text = 'Processing...', size = 'md' }) {
  const sizeMap = { sm: 'h-5 w-5', md: 'h-8 w-8', lg: 'h-12 w-12' }

  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8">
      <div
        className={`${sizeMap[size]} animate-spin rounded-full border-2 border-slate-600 border-t-indigo-500`}
      />
      {text && <p className="text-slate-400 text-sm">{text}</p>}
    </div>
  )
}
