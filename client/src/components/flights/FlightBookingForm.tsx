import { useState } from 'react'
import type { Flight, FlightBooking, CreateFlightBooking } from '../../types'
import { bookFlight } from '../../services/api'

interface FlightBookingFormProps {
  flight: Flight
  onSuccess: (booking: FlightBooking) => void
  onCancel: () => void
}

export default function FlightBookingForm({ flight, onSuccess, onCancel }: FlightBookingFormProps) {
  const [formData, setFormData] = useState<CreateFlightBooking>({
    flight_id: flight.id,
    passenger_name: '',
    contact_email: '',
    seats_booked: 1,
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const [apiError, setApiError] = useState('')

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}
    if (!formData.passenger_name.trim()) {
      newErrors.passenger_name = 'Passenger name is required'
    }
    if (!formData.contact_email.trim()) {
      newErrors.contact_email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.contact_email)) {
      newErrors.contact_email = 'Invalid email format'
    }
    if (formData.seats_booked < 1) {
      newErrors.seats_booked = 'At least 1 seat required'
    } else if (formData.seats_booked > flight.seats_available) {
      newErrors.seats_booked = `Maximum ${flight.seats_available} seats available`
    }
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setApiError('')
    if (!validate()) return

    setLoading(true)
    try {
      const booking = await bookFlight(formData)
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
        {flight.origin} → {flight.destination} | {flight.airline} | {flight.class_type} | ${flight.price.toFixed(2)}
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Passenger Name</label>
        <input
          type="text"
          value={formData.passenger_name}
          onChange={(e) => setFormData({ ...formData, passenger_name: e.target.value })}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
        />
        {errors.passenger_name && <p className="text-red-500 text-xs mt-1">{errors.passenger_name}</p>}
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

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Seats</label>
        <input
          type="number"
          min={1}
          max={flight.seats_available}
          value={formData.seats_booked}
          onChange={(e) => setFormData({ ...formData, seats_booked: parseInt(e.target.value) || 1 })}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
        />
        {errors.seats_booked && <p className="text-red-500 text-xs mt-1">{errors.seats_booked}</p>}
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 bg-sky-500 text-white rounded-lg font-medium hover:bg-sky-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Booking...' : 'Book Flight'}
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
