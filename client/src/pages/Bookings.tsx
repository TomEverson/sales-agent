import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import type { FlightBooking, HotelBooking, ActivityBooking, TransportBooking } from '../types'
import {
  getFlightBookings,
  getHotelBookings,
  getActivityBookings,
  getTransportBookings,
} from '../services/api'
import BookingCard from '../components/booking/BookingCard'

export default function Bookings() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [email, setEmail] = useState(searchParams.get('email') || '')
  const [loading, setLoading] = useState(false)
  const [flightBookings, setFlightBookings] = useState<FlightBooking[]>([])
  const [hotelBookings, setHotelBookings] = useState<HotelBooking[]>([])
  const [activityBookings, setActivityBookings] = useState<ActivityBooking[]>([])
  const [transportBookings, setTransportBookings] = useState<TransportBooking[]>([])

  const handleSearch = useCallback(async (searchEmail: string) => {
    if (!searchEmail.trim()) return
    setLoading(true)
    setSearchParams({ email: searchEmail })

    const [flights, hotels, activities, transports] = await Promise.all([
      getFlightBookings(searchEmail),
      getHotelBookings(searchEmail),
      getActivityBookings(searchEmail),
      getTransportBookings(searchEmail),
    ])

    setFlightBookings(flights)
    setHotelBookings(hotels)
    setActivityBookings(activities)
    setTransportBookings(transports)
    setLoading(false)
  }, [setSearchParams])

  useEffect(() => {
    const emailParam = searchParams.get('email')
    if (emailParam) {
      setEmail(emailParam)
      handleSearch(emailParam)
    }
  }, [searchParams, handleSearch])

  const sortByDate = <T extends { created_at: string }>(bookings: T[]): T[] => {
    return [...bookings].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  }

  const hasAnyBookings =
    flightBookings.length > 0 ||
    hotelBookings.length > 0 ||
    activityBookings.length > 0 ||
    transportBookings.length > 0

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-slate-800 mb-6">My Bookings</h1>

      <div className="flex gap-3 mb-8">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
          className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
        />
        <button
          onClick={() => handleSearch(email)}
          disabled={loading || !email.trim()}
          className="px-6 py-2 bg-sky-500 text-white rounded-lg font-medium hover:bg-sky-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {loading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-500"></div>
        </div>
      )}

      {!loading && email && hasAnyBookings && (
        <div className="space-y-6">
          {flightBookings.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold text-slate-700 mb-3 flex items-center gap-2">
                ✈️ Flights ({flightBookings.length})
              </h2>
              <div className="space-y-3">
                {sortByDate(flightBookings).map((b) => (
                  <BookingCard key={b.id} booking={{ ...b, kind: 'flight' }} />
                ))}
              </div>
            </section>
          )}

          {hotelBookings.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold text-slate-700 mb-3 flex items-center gap-2">
                🏨 Hotels ({hotelBookings.length})
              </h2>
              <div className="space-y-3">
                {sortByDate(hotelBookings).map((b) => (
                  <BookingCard key={b.id} booking={{ ...b, kind: 'hotel' }} />
                ))}
              </div>
            </section>
          )}

          {activityBookings.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold text-slate-700 mb-3 flex items-center gap-2">
                🎯 Activities ({activityBookings.length})
              </h2>
              <div className="space-y-3">
                {sortByDate(activityBookings).map((b) => (
                  <BookingCard key={b.id} booking={{ ...b, kind: 'activity' }} />
                ))}
              </div>
            </section>
          )}

          {transportBookings.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold text-slate-700 mb-3 flex items-center gap-2">
                🚗 Transport ({transportBookings.length})
              </h2>
              <div className="space-y-3">
                {sortByDate(transportBookings).map((b) => (
                  <BookingCard key={b.id} booking={{ ...b, kind: 'transport' }} />
                ))}
              </div>
            </section>
          )}
        </div>
      )}

      {!loading && email && !hasAnyBookings && (
        <div className="text-center py-12 text-slate-500">
          No bookings found for this email.
        </div>
      )}

      {!loading && !email && (
        <div className="text-center py-12 text-slate-500">
          Enter your email to view your bookings.
        </div>
      )}
    </div>
  )
}
