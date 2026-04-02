import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import type { BookingStats } from '../types'
import { getBookingStats } from '../services/api'

const categories = [
  {
    to: '/flights',
    icon: '✈️',
    label: 'Flights',
    description: 'Search available flights across Southeast Asia',
  },
  {
    to: '/hotels',
    icon: '🏨',
    label: 'Hotels',
    description: 'Find hotels from budget stays to 5-star resorts',
  },
  {
    to: '/activities',
    icon: '🎭',
    label: 'Activities',
    description: 'Explore tours, food experiences, and adventures',
  },
  {
    to: '/transport',
    icon: '🚢',
    label: 'Transport',
    description: 'Ferries, trains, buses, and private transfers',
  },
]

function StatCard({ icon, label, value }: { icon: string; label: string; value: number | string }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
      <div className="flex items-center gap-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <div className="text-2xl font-bold text-slate-800">{value}</div>
          <div className="text-sm text-slate-500">{label}</div>
        </div>
      </div>
    </div>
  )
}

function TypeBreakdown({ stats }: { stats: BookingStats }) {
  const total = stats.total_bookings || 1
  const items = [
    { label: 'Flights', count: stats.by_type.flights, icon: '✈️' },
    { label: 'Hotels', count: stats.by_type.hotels, icon: '🏨' },
    { label: 'Activities', count: stats.by_type.activities, icon: '🎭' },
    { label: 'Transport', count: stats.by_type.transport, icon: '🚢' },
  ]

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-700 mb-4">Bookings by Type</h3>
      <div className="space-y-3">
        {items.map(({ label, count, icon }) => (
          <div key={label} className="flex items-center gap-3">
            <span className="text-lg">{icon}</span>
            <div className="flex-1">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-600">{label}</span>
                <span className="font-medium text-slate-800">{count}</span>
              </div>
              <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-sky-400 rounded-full"
                  style={{ width: `${(count / total) * 100}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function Home() {
  const [stats, setStats] = useState<BookingStats | null>(null)

  useEffect(() => {
    getBookingStats().then(setStats)
  }, [])

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      {/* Statistics */}
      {stats && (
        <div className="mb-10">
          <h2 className="text-lg font-semibold text-slate-700 mb-4">Dashboard Overview</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <StatCard icon="📦" label="Total Bookings" value={stats.total_bookings} />
            <StatCard icon="👥" label="Unique Users" value={stats.unique_users} />
            <StatCard icon="✈️" label="Flights" value={stats.by_type.flights} />
            <StatCard icon="🏨" label="Hotels" value={stats.by_type.hotels} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <TypeBreakdown stats={stats} />
          </div>
        </div>
      )}

      {/* Hero */}
      <div className="text-center mb-14">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">
          Plan your next trip in Southeast Asia
        </h1>
        <p className="text-slate-500 text-lg max-w-xl mx-auto">
          Browse flights, hotels, activities, and transport options across Bangkok, Bali, Singapore, Phuket, and more.
        </p>
      </div>

      {/* Category Links */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {categories.map(({ to, icon, label, description }) => (
          <Link
            key={to}
            to={to}
            className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-md hover:border-sky-300 transition-all group"
          >
            <span className="text-3xl mb-3 block">{icon}</span>
            <h2 className="text-lg font-semibold text-slate-900 mb-1 group-hover:text-sky-600 transition-colors">
              {label}
            </h2>
            <p className="text-sm text-slate-500">{description}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}