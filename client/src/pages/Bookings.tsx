import { useState, useEffect } from 'react'
import type { BookingPackage } from '../types'
import { getBookingPackages } from '../services/api'

const KIND_ICONS: Record<string, string> = {
  flight: '✈️',
  hotel: '🏨',
  activity: '🎯',
  transport: '🚗',
}

const KIND_LABELS: Record<string, string> = {
  flight: 'Flight',
  hotel: 'Hotel',
  activity: 'Activity',
  transport: 'Transport',
}

function PackageCard({ pkg }: { pkg: BookingPackage }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="text-xs font-mono text-slate-500 bg-slate-100 px-2 py-1 rounded">
            {pkg.booking_reference}
          </span>
        </div>
        <span className="text-sm text-slate-500">
          {new Date(pkg.created_at).toLocaleDateString()}
        </span>
      </div>

      {/* Items */}
      <div className="space-y-3 mb-4">
        {pkg.items.map((item) => (
          <div key={`${item.kind}-${item.id}`} className="flex items-center gap-3 text-sm">
            <span className="text-lg">{KIND_ICONS[item.kind]}</span>
            <div className="flex-1">
              <div className="font-medium text-slate-800">
                {KIND_LABELS[item.kind]}
              </div>
              <div className="text-slate-500">
                {item.passenger_name} · {item.contact_email}
              </div>
            </div>
            <span
              className={`text-xs px-2 py-1 rounded-full ${
                item.status === 'confirmed'
                  ? 'bg-green-100 text-green-700'
                  : item.status === 'pending'
                  ? 'bg-yellow-100 text-yellow-700'
                  : 'bg-slate-100 text-slate-600'
              }`}
            >
              {item.status}
            </span>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
        <span className="text-sm text-slate-500">
          {pkg.total_items} item{pkg.total_items !== 1 ? 's' : ''}
        </span>
        <span className="text-sm font-medium text-slate-700">
          {pkg.items[0]?.contact_email}
        </span>
      </div>
    </div>
  )
}

export default function Bookings() {
  const [packages, setPackages] = useState<BookingPackage[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      setLoading(true)
      const data = await getBookingPackages()
      setPackages(data)
      setLoading(false)
    }
    load()
  }, [])

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-slate-800 mb-6">Booking Packages</h1>

      {loading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-500"></div>
        </div>
      )}

      {!loading && packages.length > 0 && (
        <div className="space-y-4">
          {packages.map((pkg) => (
            <PackageCard key={pkg.booking_reference} pkg={pkg} />
          ))}
        </div>
      )}

      {!loading && packages.length === 0 && (
        <div className="text-center py-12 text-slate-500">
          No booking packages found.
        </div>
      )}
    </div>
  )
}