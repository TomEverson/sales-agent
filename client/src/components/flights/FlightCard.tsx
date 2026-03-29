import { useState } from 'react'
import type { Flight, FlightBooking } from '../../types'
import BookingModal from '../booking/BookingModal'
import BookingConfirmation from '../booking/BookingConfirmation'
import FlightBookingForm from './FlightBookingForm'

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
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [showConfirmation, setShowConfirmation] = useState(false)
  const [booking, setBooking] = useState<FlightBooking | null>(null)

  const handleSuccess = (b: FlightBooking) => {
    setBooking(b)
    setShowConfirmation(true)
  }

  const handleClose = () => {
    setIsModalOpen(false)
    setShowConfirmation(false)
    setBooking(null)
  }

  return (
    <>
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
        <div className="text-right shrink-0 flex items-center gap-3">
          <div>
            <p className="text-lg font-bold text-sky-600">${flight.price.toFixed(2)}</p>
            <p className="text-xs text-slate-400">{flight.seats_available} seats left</p>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-3 py-2 bg-sky-500 text-white text-sm rounded-lg font-medium hover:bg-sky-600 transition-colors"
          >
            Book
          </button>
        </div>
      </div>

      <BookingModal isOpen={isModalOpen} onClose={handleClose} title="Book Flight">
        {showConfirmation && booking ? (
          <BookingConfirmation
            reference={booking.booking_reference}
            summary={`${flight.origin} → ${flight.destination} | ${flight.airline} | ${flight.class_type}`}
            email={booking.contact_email}
            onClose={handleClose}
          />
        ) : (
          <FlightBookingForm
            flight={flight}
            onSuccess={handleSuccess}
            onCancel={handleClose}
          />
        )}
      </BookingModal>
    </>
  )
}
