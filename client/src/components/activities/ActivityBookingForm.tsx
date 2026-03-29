import { useState } from 'react'
import type { Activity, ActivityBooking, CreateActivityBooking } from '../../types'
import { bookActivity } from '../../services/api'

interface ActivityBookingFormProps {
  activity: Activity
  onSuccess: (booking: ActivityBooking) => void
  onCancel: () => void
}

export default function ActivityBookingForm({ activity, onSuccess, onCancel }: ActivityBookingFormProps) {
  const [formData, setFormData] = useState({
    participant_name: '',
    contact_email: '',
    activity_date: '',
    participants: 1,
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const [apiError, setApiError] = useState('')

  const today = new Date().toISOString().split('T')[0]

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}
    if (!formData.participant_name.trim()) {
      newErrors.participant_name = 'Your name is required'
    }
    if (!formData.contact_email.trim()) {
      newErrors.contact_email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.contact_email)) {
      newErrors.contact_email = 'Invalid email format'
    }
    if (!formData.activity_date) {
      newErrors.activity_date = 'Activity date is required'
    } else if (new Date(formData.activity_date) < new Date(today)) {
      newErrors.activity_date = 'Activity date cannot be in the past'
    }
    if (formData.participants < 1) {
      newErrors.participants = 'At least 1 participant required'
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
      const bookingData: CreateActivityBooking = {
        activity_id: activity.id,
        participant_name: formData.participant_name,
        contact_email: formData.contact_email,
        activity_date: formData.activity_date,
        participants: formData.participants,
      }
      const booking = await bookActivity(bookingData)
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
        {activity.name} | {activity.category} | {activity.duration_hours}hrs | ${activity.price.toFixed(2)}
        <span className="ml-2 text-xs bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full">
          {activity.availability}
        </span>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Your Name</label>
        <input
          type="text"
          value={formData.participant_name}
          onChange={(e) => setFormData({ ...formData, participant_name: e.target.value })}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
        />
        {errors.participant_name && <p className="text-red-500 text-xs mt-1">{errors.participant_name}</p>}
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
        <label className="block text-sm font-medium text-slate-700 mb-1">Activity Date</label>
        <input
          type="date"
          value={formData.activity_date}
          min={today}
          onChange={(e) => setFormData({ ...formData, activity_date: e.target.value })}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
        />
        {errors.activity_date && <p className="text-red-500 text-xs mt-1">{errors.activity_date}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Participants</label>
        <input
          type="number"
          min={1}
          value={formData.participants}
          onChange={(e) => setFormData({ ...formData, participants: parseInt(e.target.value) || 1 })}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
        />
        {errors.participants && <p className="text-red-500 text-xs mt-1">{errors.participants}</p>}
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 bg-sky-500 text-white rounded-lg font-medium hover:bg-sky-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Booking...' : 'Book Activity'}
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
