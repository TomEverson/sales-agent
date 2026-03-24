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
