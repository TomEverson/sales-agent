import type { Hotel } from '../../types'
import HotelCard from './HotelCard'

interface HotelListProps {
  hotels: Hotel[]
  loading: boolean
}

export default function HotelList({ hotels, loading }: HotelListProps) {
  if (loading) {
    return <p className="text-slate-400 text-sm text-center py-12">Loading hotels...</p>
  }
  if (hotels.length === 0) {
    return <p className="text-slate-400 text-sm text-center py-12">No hotels found.</p>
  }
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {hotels.map((h) => (
        <HotelCard key={h.id} hotel={h} />
      ))}
    </div>
  )
}
