import { useState } from 'react'
import type { FlightBooking, HotelBooking, ActivityBooking, TransportBooking } from '../../types'

type AnyBooking =
  | (FlightBooking & { kind: 'flight' })
  | (HotelBooking & { kind: 'hotel' })
  | (ActivityBooking & { kind: 'activity' })
  | (TransportBooking & { kind: 'transport' })

interface BookingCardProps {
  booking: AnyBooking
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' })
}

export default function BookingCard({ booking }: BookingCardProps) {
  const [copied, setCopied] = useState(false)

  const copyRef = async () => {
    try {
      await navigator.clipboard.writeText(booking.booking_reference)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Fallback
    }
  }

  const renderContent = () => {
    switch (booking.kind) {
      case 'flight':
        return (
          <>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xl">✈️</span>
              <span className="font-medium text-slate-700">Flight Booking</span>
            </div>
            <p className="text-sm text-slate-600">Passenger: {booking.passenger_name}</p>
            <p className="text-sm text-slate-600">Seats: {booking.seats_booked}</p>
            <p className="text-xs text-slate-400 mt-1">Booked: {formatDate(booking.created_at)}</p>
          </>
        )
      case 'hotel':
        return (
          <>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xl">🏨</span>
              <span className="font-medium text-slate-700">Hotel Booking</span>
            </div>
            <p className="text-sm text-slate-600">Guest: {booking.guest_name}</p>
            <p className="text-sm text-slate-600">
              Check-in: {formatDate(booking.check_in_date)} → Check-out: {formatDate(booking.check_out_date)} ({booking.nights} night{booking.nights > 1 ? 's' : ''})
            </p>
          </>
        )
      case 'activity':
        return (
          <>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xl">🎯</span>
              <span className="font-medium text-slate-700">Activity Booking</span>
            </div>
            <p className="text-sm text-slate-600">Participant: {booking.participant_name}</p>
            <p className="text-sm text-slate-600">
              Date: {formatDate(booking.activity_date)} | Participants: {booking.participants}
            </p>
          </>
        )
      case 'transport':
        return (
          <>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xl">🚗</span>
              <span className="font-medium text-slate-700">Transport Booking</span>
            </div>
            <p className="text-sm text-slate-600">Passenger: {booking.passenger_name}</p>
            <p className="text-sm text-slate-600">Passengers: {booking.passengers}</p>
            <p className="text-xs text-slate-400 mt-1">Booked: {formatDate(booking.created_at)}</p>
          </>
        )
    }
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
      <div className="flex items-center justify-between mb-2">
        {renderContent()}
      </div>
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100">
        <div className="flex items-center gap-2">
          <code className="text-sm font-mono text-sky-600">{booking.booking_reference}</code>
          <button onClick={copyRef} className="text-slate-400 hover:text-sky-500 text-sm">
            {copied ? '✓' : '📋'}
          </button>
        </div>
        <span
          className={`text-xs font-medium px-2 py-1 rounded-full ${
            booking.status === 'confirmed'
              ? 'bg-green-100 text-green-700'
              : 'bg-slate-100 text-slate-600'
          }`}
        >
          {booking.status}
        </span>
      </div>
    </div>
  )
}
