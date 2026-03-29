import { useState, useMemo } from 'react'
import type { Hotel, HotelBooking, CreateHotelBooking } from '../../types'
import { bookHotel } from '../../services/api'

interface HotelBookingFormProps {
  hotel: Hotel
  onSuccess: (booking: HotelBooking) => void
  onCancel: () => void
}

export default function HotelBookingForm({ hotel, onSuccess, onCancel }: HotelBookingFormProps) {
  const [formData, setFormData] = useState({
    guest_name: '',
    contact_email: '',
    check_in_date: '',
    check_out_date: '',
    guests: 1,
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const [apiError, setApiError] = useState('')

  const tonight = useMemo(() => {
    const d = new Date()
    d.setDate(d.getDate() + 1)
    return d.toISOString().split('T')[0]
  }, [])

  const nights = useMemo(() => {
    if (!formData.check_in_date || !formData.check_out_date) return 0
    const start = new Date(formData.check_in_date)
    const end = new Date(formData.check_out_date)
    const diff = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))
    return diff > 0 ? diff : 0
  }, [formData.check_in_date, formData.check_out_date])

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}
    if (!formData.guest_name.trim()) {
      newErrors.guest_name = 'Guest name is required'
    }
    if (!formData.contact_email.trim()) {
      newErrors.contact_email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.contact_email)) {
      newErrors.contact_email = 'Invalid email format'
    }
    if (!formData.check_in_date) {
      newErrors.check_in_date = 'Check-in date is required'
    } else if (new Date(formData.check_in_date) < new Date(tonight)) {
      newErrors.check_in_date = 'Check-in cannot be in the past'
    }
    if (!formData.check_out_date) {
      newErrors.check_out_date = 'Check-out date is required'
    } else if (formData.check_in_date && formData.check_out_date <= formData.check_in_date) {
      newErrors.check_out_date = 'Check-out must be after check-in'
    }
    if (formData.guests < 1) {
      newErrors.guests = 'At least 1 guest required'
    }
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setApiError('')
    if (!validate()) return
    if (nights === 0) {
      setErrors({ check_out_date: 'Invalid date range' })
      return
    }

    setLoading(true)
    try {
      const bookingData: CreateHotelBooking = {
        hotel_id: hotel.id,
        guest_name: formData.guest_name,
        contact_email: formData.contact_email,
        check_in_date: formData.check_in_date,
        check_out_date: formData.check_out_date,
        nights,
        guests: formData.guests,
      }
      const booking = await bookHotel(bookingData)
      onSuccess(booking)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setApiError(err.message)
      } else {
        setApiError('Booking failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {apiError && (
        <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg">{apiError}</div>
      )}

      <div className="bg-slate-50 rounded-lg p-3 text-sm text-slate-600 mb-4">
        {hotel.name} | {'★'.repeat(hotel.stars)} | ${hotel.price_per_night.toFixed(2)}/night
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Guest Name</label>
        <input
          type="text"
          value={formData.guest_name}
          onChange={(e) => setFormData({ ...formData, guest_name: e.target.value })}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
        />
        {errors.guest_name && <p className="text-red-500 text-xs mt-1">{errors.guest_name}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
        <input
          type="email"
          value={formData.contact_email}
          onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
        />
        {errors.contact_email && <p className="text-red-500 text-xs mt-1">{errors.contact_email}</p>}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Check-in</label>
          <input
            type="date"
            value={formData.check_in_date}
            min={tonight}
            onChange={(e) => setFormData({ ...formData, check_in_date: e.target.value })}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
          />
          {errors.check_in_date && <p className="text-red-500 text-xs mt-1">{errors.check_in_date}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Check-out</label>
          <input
            type="date"
            value={formData.check_out_date}
            min={formData.check_in_date || tonight}
            onChange={(e) => setFormData({ ...formData, check_out_date: e.target.value })}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
          />
          {errors.check_out_date && <p className="text-red-500 text-xs mt-1">{errors.check_out_date}</p>}
        </div>
      </div>

      {nights > 0 && (
        <p className="text-sm text-slate-500">{nights} night{nights > 1 ? 's' : ''}</p>
      )}

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Guests</label>
        <input
          type="number"
          min={1}
          value={formData.guests}
          onChange={(e) => setFormData({ ...formData, guests: parseInt(e.target.value) || 1 })}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
        />
        {errors.guests && <p className="text-red-500 text-xs mt-1">{errors.guests}</p>}
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 bg-sky-500 text-white rounded-lg font-medium hover:bg-sky-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Booking...' : 'Book Hotel'}
      </button>

      <button
        type="button"
        onClick={onCancel}
        className="w-full text-center text-sm text-slate-500 hover:text-slate-700 mt-2"
      >
        Cancel
      </button>
    </form>
  )
}
