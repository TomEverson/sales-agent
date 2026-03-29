import axios from 'axios'
import type {
  Flight,
  Hotel,
  Activity,
  Transport,
  FlightFilters,
  HotelFilters,
  ActivityFilters,
  TransportFilters,
  FlightBooking,
  HotelBooking,
  ActivityBooking,
  TransportBooking,
  CreateFlightBooking,
  CreateHotelBooking,
  CreateActivityBooking,
  CreateTransportBooking,
} from '../types'

const api = axios.create({ baseURL: 'http://localhost:8000' })

export async function getFlights(filters: FlightFilters): Promise<Flight[]> {
  try {
    const { data } = await api.get<Flight[]>('/flights', { params: filters })
    return data
  } catch (err) {
    console.error('getFlights error:', err)
    return []
  }
}

export async function getHotels(filters: HotelFilters): Promise<Hotel[]> {
  try {
    const { data } = await api.get<Hotel[]>('/hotels', { params: filters })
    return data
  } catch (err) {
    console.error('getHotels error:', err)
    return []
  }
}

export async function getActivities(filters: ActivityFilters): Promise<Activity[]> {
  try {
    const { data } = await api.get<Activity[]>('/activities', { params: filters })
    return data
  } catch (err) {
    console.error('getActivities error:', err)
    return []
  }
}

export async function getTransports(filters: TransportFilters): Promise<Transport[]> {
  try {
    const { data } = await api.get<Transport[]>('/transport', { params: filters })
    return data
  } catch (err) {
    console.error('getTransports error:', err)
    return []
  }
}

// Booking functions
export async function bookFlight(data: CreateFlightBooking): Promise<FlightBooking> {
  try {
    const response = await api.post<FlightBooking>('/bookings/flights', data)
    return response.data
  } catch (err: unknown) {
    if (axios.isAxiosError(err) && err.response) {
      if (err.response.status === 422) {
        throw new Error('Not enough seats available.')
      }
      if (err.response.status === 404) {
        throw new Error('Flight not found.')
      }
    }
    throw err
  }
}

export async function bookHotel(data: CreateHotelBooking): Promise<HotelBooking> {
  try {
    const response = await api.post<HotelBooking>('/bookings/hotels', data)
    return response.data
  } catch (err: unknown) {
    if (axios.isAxiosError(err) && err.response) {
      if (err.response.status === 422) {
        throw new Error('Not enough rooms available.')
      }
      if (err.response.status === 404) {
        throw new Error('Hotel not found.')
      }
    }
    throw err
  }
}

export async function bookActivity(data: CreateActivityBooking): Promise<ActivityBooking> {
  try {
    const response = await api.post<ActivityBooking>('/bookings/activities', data)
    return response.data
  } catch (err: unknown) {
    if (axios.isAxiosError(err) && err.response) {
      if (err.response.status === 404) {
        throw new Error('Activity not found.')
      }
    }
    throw err
  }
}

export async function bookTransport(data: CreateTransportBooking): Promise<TransportBooking> {
  try {
    const response = await api.post<TransportBooking>('/bookings/transport', data)
    return response.data
  } catch (err: unknown) {
    if (axios.isAxiosError(err) && err.response) {
      if (err.response.status === 422) {
        throw new Error('Not enough capacity available.')
      }
      if (err.response.status === 404) {
        throw new Error('Transport not found.')
      }
    }
    throw err
  }
}

export async function getFlightBookings(email: string): Promise<FlightBooking[]> {
  try {
    const { data } = await api.get<FlightBooking[]>('/bookings/flights', { params: { email } })
    return data
  } catch (err) {
    console.error('getFlightBookings error:', err)
    return []
  }
}

export async function getHotelBookings(email: string): Promise<HotelBooking[]> {
  try {
    const { data } = await api.get<HotelBooking[]>('/bookings/hotels', { params: { email } })
    return data
  } catch (err) {
    console.error('getHotelBookings error:', err)
    return []
  }
}

export async function getActivityBookings(email: string): Promise<ActivityBooking[]> {
  try {
    const { data } = await api.get<ActivityBooking[]>('/bookings/activities', { params: { email } })
    return data
  } catch (err) {
    console.error('getActivityBookings error:', err)
    return []
  }
}

export async function getTransportBookings(email: string): Promise<TransportBooking[]> {
  try {
    const { data } = await api.get<TransportBooking[]>('/bookings/transport', { params: { email } })
    return data
  } catch (err) {
    console.error('getTransportBookings error:', err)
    return []
  }
}
