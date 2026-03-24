export interface Flight {
  id: number
  origin: string
  destination: string
  airline: string
  departure_time: string
  arrival_time: string
  price: number
  seats_available: number
  class_type: string
}

export interface Hotel {
  id: number
  name: string
  location: string
  city: string
  stars: number
  price_per_night: number
  rooms_available: number
  amenities: string
}

export interface Activity {
  id: number
  name: string
  city: string
  description: string
  duration_hours: number
  price: number
  category: string
  availability: string
}

export interface Transport {
  id: number
  type: string
  origin: string
  destination: string
  price: number
  capacity: number
  departure_time: string
  arrival_time: string
}

export interface FlightFilters {
  origin?: string
  destination?: string
  class_type?: string
}

export interface HotelFilters {
  city?: string
  stars?: number
  max_price?: number
}

export interface ActivityFilters {
  city?: string
  category?: string
}

export interface TransportFilters {
  type?: string
  origin?: string
  destination?: string
}
