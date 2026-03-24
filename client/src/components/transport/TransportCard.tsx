import type { Transport } from '../../types'

interface TransportCardProps {
  transport: Transport
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString([], { month: 'short', day: 'numeric' })
}

const typeColors: Record<string, string> = {
  ferry: 'bg-blue-100 text-blue-700',
  train: 'bg-indigo-100 text-indigo-700',
  bus: 'bg-lime-100 text-lime-700',
  car: 'bg-rose-100 text-rose-700',
}

export default function TransportCard({ transport }: TransportCardProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center justify-between gap-4">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${typeColors[transport.type] ?? 'bg-slate-100 text-slate-600'}`}
          >
            {transport.type}
          </span>
          <span className="font-semibold text-slate-900">{transport.origin}</span>
          <span className="text-slate-400">→</span>
          <span className="font-semibold text-slate-900">{transport.destination}</span>
        </div>
        <p className="text-xs text-slate-400">
          {formatDate(transport.departure_time)} · {formatTime(transport.departure_time)} → {formatTime(transport.arrival_time)}
        </p>
        <p className="text-xs text-slate-400 mt-0.5">Capacity: {transport.capacity}</p>
      </div>
      <div className="text-right shrink-0">
        <p className="text-lg font-bold text-sky-600">${transport.price.toFixed(2)}</p>
      </div>
    </div>
  )
}
