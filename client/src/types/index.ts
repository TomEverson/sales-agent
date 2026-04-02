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

// Booking response types (returned by server)
export interface FlightBooking {
  id: number
  flight_id: number
  passenger_name: string
  contact_email: string
  booking_reference: string
  status: string
  seats_booked: number
  created_at: string
}

export interface HotelBooking {
  id: number
  hotel_id: number
  guest_name: string
  contact_email: string
  check_in_date: string
  check_out_date: string
  nights: number
  guests: number
  booking_reference: string
  status: string
  created_at: string
}

export interface ActivityBooking {
  id: number
  activity_id: number
  participant_name: string
  contact_email: string
  activity_date: string
  participants: number
  booking_reference: string
  status: string
  created_at: string
}

export interface TransportBooking {
  id: number
  transport_id: number
  passenger_name: string
  contact_email: string
  passengers: number
  booking_reference: string
  status: string
  created_at: string
}

// Booking create types (sent to server)
export interface CreateFlightBooking {
  flight_id: number
  passenger_name: string
  contact_email: string
  seats_booked: number
}

export interface CreateHotelBooking {
  hotel_id: number
  guest_name: string
  contact_email: string
  check_in_date: string
  check_out_date: string
  nights: number
  guests: number
}

export interface CreateActivityBooking {
  activity_id: number
  participant_name: string
  contact_email: string
  activity_date: string
  participants: number
}

export interface CreateTransportBooking {
  transport_id: number
  passenger_name: string
  contact_email: string
  passengers: number
}

// Auth types
export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthToken {
  access_token: string
  token_type: string
}

export interface AuthUser {
  email: string
  is_admin: boolean
}

// Package booking types
export interface BookingPackageItem {
  kind: 'flight' | 'hotel' | 'activity' | 'transport'
  id: number
  passenger_name: string
  contact_email: string
  status: string
  created_at: string
  flight_id?: number
  hotel_id?: number
  activity_id?: number
  transport_id?: number
  seats_booked?: number
  guests?: number
  participants?: number
  check_in_date?: string
  check_out_date?: string
  activity_date?: string
}

export interface BookingPackage {
  booking_reference: string
  items: BookingPackageItem[]
  total_items: number
  created_at: string
}

// Booking statistics
export interface BookingStats {
  total_bookings: number
  unique_users: number
  by_type: {
    flights: number
    hotels: number
    activities: number
    transport: number
  }
}
