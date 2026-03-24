import type { Flight } from '../../types'

interface FlightCardProps {
  flight: Flight
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString([], { month: 'short', day: 'numeric' })
}

const classColors: Record<string, string> = {
  economy: 'bg-slate-100 text-slate-600',
  business: 'bg-sky-100 text-sky-700',
  first: 'bg-amber-100 text-amber-700',
}

export default function FlightCard({ flight }: FlightCardProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center justify-between gap-4">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-semibold text-slate-900">{flight.origin}</span>
          <span className="text-slate-400">→</span>
          <span className="font-semibold text-slate-900">{flight.destination}</span>
          <span
            className={`ml-2 text-xs font-medium px-2 py-0.5 rounded-full ${classColors[flight.class_type] ?? 'bg-slate-100 text-slate-600'}`}
          >
            {flight.class_type}
          </span>
        </div>
        <p className="text-sm text-slate-500">{flight.airline}</p>
        <p className="text-xs text-slate-400 mt-1">
          {formatDate(flight.departure_time)} · {formatTime(flight.departure_time)} → {formatTime(flight.arrival_time)}
        </p>
      </div>
      <div className="text-right shrink-0">
        <p className="text-lg font-bold text-sky-600">${flight.price.toFixed(2)}</p>
        <p className="text-xs text-slate-400">{flight.seats_available} seats left</p>
      </div>
    </div>
  )
}
