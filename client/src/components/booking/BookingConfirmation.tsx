import { useState } from 'react'

interface BookingConfirmationProps {
  reference: string
  summary: string
  email: string
  onClose: () => void
}

export default function BookingConfirmation({ reference, summary, email, onClose }: BookingConfirmationProps) {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(reference)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Fallback for older browsers
    }
  }

  return (
    <div className="text-center">
      <div className="text-5xl mb-4">✅</div>
      <h3 className="text-2xl font-bold text-slate-800 mb-4">Booking Confirmed!</h3>
      
      <div className="bg-slate-50 rounded-lg p-4 mb-4">
        <p className="text-sm text-slate-500 mb-1">Reference</p>
        <div className="flex items-center justify-center gap-2">
          <code className="text-lg font-mono text-sky-600">{reference}</code>
          <button
            onClick={copyToClipboard}
            className="text-slate-400 hover:text-sky-500"
            title="Copy to clipboard"
          >
            {copied ? '✓' : '📋'}
          </button>
        </div>
      </div>

      <p className="text-slate-600 mb-2">{summary}</p>
      <p className="text-sm text-slate-500 mb-6">Confirmation sent to: {email}</p>

      <button
        onClick={onClose}
        className="w-full py-3 bg-sky-500 text-white rounded-lg font-medium hover:bg-sky-600 transition-colors"
      >
        Close
      </button>
    </div>
  )
}
