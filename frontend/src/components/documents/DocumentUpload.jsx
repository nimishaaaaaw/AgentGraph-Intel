import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react'

/**
 * Drag-and-drop document upload component.
 * Accepts PDF, TXT, and Markdown files.
 *
 * @param {Object} props
 * @param {Function} props.onUpload - Callback after successful upload
 */
export default function DocumentUpload({ onUpload }) {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState(null) // 'success' | 'error' | null

  const onDrop = useCallback(
    async (acceptedFiles) => {
      if (!acceptedFiles.length) return

      setUploading(true)
      setStatus(null)
      setProgress(0)

      for (const file of acceptedFiles) {
        try {
          setProgress(20)
          await onUpload(file)
          setProgress(100)
          setStatus('success')
        } catch {
          setStatus('error')
        }
      }

      setUploading(false)
      setTimeout(() => setStatus(null), 3000)
    },
    [onUpload]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    multiple: true,
    disabled: uploading,
  })

  return (
    <div className="p-4">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
          isDragActive
            ? 'border-indigo-400 bg-indigo-950/30'
            : uploading
            ? 'border-slate-600 bg-slate-800/30 cursor-not-allowed'
            : 'border-slate-600 hover:border-indigo-500 hover:bg-slate-800/30'
        }`}
      >
        <input {...getInputProps()} />

        {status === 'success' ? (
          <div className="flex flex-col items-center gap-2">
            <CheckCircle size={40} className="text-emerald-400" />
            <p className="text-emerald-400 font-medium">Document uploaded successfully!</p>
          </div>
        ) : status === 'error' ? (
          <div className="flex flex-col items-center gap-2">
            <AlertCircle size={40} className="text-red-400" />
            <p className="text-red-400 font-medium">Upload failed. Please try again.</p>
          </div>
        ) : uploading ? (
          <div className="flex flex-col items-center gap-3">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-400" />
            <p className="text-slate-300 font-medium">Processing document...</p>
            <div className="w-48 bg-slate-700 rounded-full h-1.5">
              <div
                className="bg-indigo-500 h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className="w-14 h-14 rounded-full bg-slate-700 flex items-center justify-center">
              {isDragActive ? (
                <Upload size={28} className="text-indigo-400" />
              ) : (
                <FileText size={28} className="text-slate-400" />
              )}
            </div>
            <div>
              <p className="text-slate-200 font-medium">
                {isDragActive ? 'Drop files here' : 'Drop files here or click to upload'}
              </p>
              <p className="text-slate-500 text-sm mt-1">Supports PDF, TXT, Markdown</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
