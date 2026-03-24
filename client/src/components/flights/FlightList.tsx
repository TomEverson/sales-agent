import type { Flight } from '../../types'
import FlightCard from './FlightCard'

interface FlightListProps {
  flights: Flight[]
  loading: boolean
}

export default function FlightList({ flights, loading }: FlightListProps) {
  if (loading) {
    return <p className="text-slate-400 text-sm text-center py-12">Loading flights...</p>
  }
  if (flights.length === 0) {
    return <p className="text-slate-400 text-sm text-center py-12">No flights found.</p>
  }
  return (
    <div className="flex flex-col gap-3">
      {flights.map((f) => (
        <FlightCard key={f.id} flight={f} />
      ))}
    </div>
  )
}
