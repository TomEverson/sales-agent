import { useState } from 'react'
import type { Transport, TransportBooking } from '../../types'
import BookingModal from '../booking/BookingModal'
import BookingConfirmation from '../booking/BookingConfirmation'
import TransportBookingForm from './TransportBookingForm'

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
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [showConfirmation, setShowConfirmation] = useState(false)
  const [booking, setBooking] = useState<TransportBooking | null>(null)

  const handleSuccess = (b: TransportBooking) => {
    setBooking(b)
    setShowConfirmation(true)
  }

  const handleClose = () => {
    setIsModalOpen(false)
    setShowConfirmation(false)
    setBooking(null)
  }

  const isFull = transport.capacity === 0

  return (
    <>
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
        <div className="text-right shrink-0 flex items-center gap-3">
          <div>
            <p className="text-lg font-bold text-sky-600">${transport.price.toFixed(2)}</p>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            disabled={isFull}
            className="px-3 py-2 bg-sky-500 text-white text-sm rounded-lg font-medium hover:bg-sky-600 transition-colors disabled:bg-slate-300 disabled:cursor-not-allowed"
          >
            {isFull ? 'Full' : 'Book'}
          </button>
        </div>
      </div>

      <BookingModal isOpen={isModalOpen} onClose={handleClose} title="Book Transport">
        {showConfirmation && booking ? (
          <BookingConfirmation
            reference={booking.booking_reference}
            summary={`${transport.type} | ${transport.origin} → ${transport.destination} | ${booking.passengers} passenger${booking.passengers > 1 ? 's' : ''}`}
            email={booking.contact_email}
            onClose={handleClose}
          />
        ) : (
          <TransportBookingForm
            transport={transport}
            onSuccess={handleSuccess}
            onCancel={handleClose}
          />
        )}
      </BookingModal>
    </>
  )
}
