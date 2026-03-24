import type { Hotel } from '../../types'

interface HotelCardProps {
  hotel: Hotel
}

export default function HotelCard({ hotel }: HotelCardProps) {
  const amenities = hotel.amenities.split(',').map((a) => a.trim())

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
      <div className="flex items-start justify-between gap-4 mb-2">
        <div>
          <h3 className="font-semibold text-slate-900">{hotel.name}</h3>
          <p className="text-sm text-slate-500">{hotel.city}</p>
        </div>
        <div className="text-right shrink-0">
          <p className="text-lg font-bold text-sky-600">${hotel.price_per_night.toFixed(2)}</p>
          <p className="text-xs text-slate-400">per night</p>
        </div>
      </div>
      <div className="flex items-center gap-1 mb-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <span key={i} className={i < hotel.stars ? 'text-amber-400' : 'text-slate-200'}>
            ★
          </span>
        ))}
        <span className="text-xs text-slate-400 ml-1">{hotel.rooms_available} rooms available</span>
      </div>
      <div className="flex flex-wrap gap-1">
        {amenities.map((a) => (
          <span key={a} className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
            {a}
          </span>
        ))}
      </div>
    </div>
  )
}
