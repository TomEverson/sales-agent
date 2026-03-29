import { useState } from 'react'
import type { Hotel, HotelBooking } from '../../types'
import BookingModal from '../booking/BookingModal'
import BookingConfirmation from '../booking/BookingConfirmation'
import HotelBookingForm from './HotelBookingForm'

interface HotelCardProps {
  hotel: Hotel
}

export default function HotelCard({ hotel }: HotelCardProps) {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [showConfirmation, setShowConfirmation] = useState(false)
  const [booking, setBooking] = useState<HotelBooking | null>(null)

  const amenities = hotel.amenities.split(',').map((a) => a.trim())

  const handleSuccess = (b: HotelBooking) => {
    setBooking(b)
    setShowConfirmation(true)
  }

  const handleClose = () => {
    setIsModalOpen(false)
    setShowConfirmation(false)
    setBooking(null)
  }

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr)
    return d.toLocaleDateString([], { day: 'numeric', month: 'short' })
  }

  return (
    <>
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
        <div className="flex items-start justify-between gap-4 mb-2">
          <div>
            <h3 className="font-semibold text-slate-900">{hotel.name}</h3>
            <p className="text-sm text-slate-500">{hotel.city}</p>
          </div>
          <div className="text-right shrink-0 flex items-center gap-3">
            <div>
              <p className="text-lg font-bold text-sky-600">${hotel.price_per_night.toFixed(2)}</p>
              <p className="text-xs text-slate-400">per night</p>
            </div>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-3 py-2 bg-sky-500 text-white text-sm rounded-lg font-medium hover:bg-sky-600 transition-colors"
            >
              Book
            </button>
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

      <BookingModal isOpen={isModalOpen} onClose={handleClose} title="Book Hotel">
        {showConfirmation && booking ? (
          <BookingConfirmation
            reference={booking.booking_reference}
            summary={`${hotel.name} | ${'★'.repeat(hotel.stars)} | ${formatDate(booking.check_in_date)} → ${formatDate(booking.check_out_date)} (${booking.nights} night${booking.nights > 1 ? 's' : ''})`}
            email={booking.contact_email}
            onClose={handleClose}
          />
        ) : (
          <HotelBookingForm
            hotel={hotel}
            onSuccess={handleSuccess}
            onCancel={handleClose}
          />
        )}
      </BookingModal>
    </>
  )
}
