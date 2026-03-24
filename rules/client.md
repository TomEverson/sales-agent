Build a React frontend for a travel inventory website.

## Stack
- React + Vite + TypeScript
- Tailwind CSS
- Axios for API calls
- React Router for navigation

## Setup
- Initialize with: npm create vite@latest client -- --template react-ts
- Install dependencies: npm install axios react-router-dom
- Install and configure Tailwind CSS v4

## Project structure to generate
client/
├── public/
└── src/
    ├── components/
    │   ├── flights/
    │   │   ├── FlightCard.tsx
    │   │   └── FlightList.tsx
    │   ├── hotels/
    │   │   ├── HotelCard.tsx
    │   │   └── HotelList.tsx
    │   ├── activities/
    │   │   ├── ActivityCard.tsx
    │   │   └── ActivityList.tsx
    │   ├── transport/
    │   │   ├── TransportCard.tsx
    │   │   └── TransportList.tsx
    │   └── ui/
    │       ├── Navbar.tsx
    │       ├── SearchBar.tsx
    │       └── FilterPanel.tsx
    ├── pages/
    │   ├── Home.tsx
    │   ├── Flights.tsx
    │   ├── Hotels.tsx
    │   ├── Activities.tsx
    │   └── Transport.tsx
    ├── services/
    │   └── api.ts
    ├── types/
    │   └── index.ts
    ├── App.tsx
    └── main.tsx

## Types (types/index.ts)
Define and export all shared types here:

interface Flight {
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

interface Hotel {
  id: number
  name: string
  location: string
  city: string
  stars: number
  price_per_night: number
  rooms_available: number
  amenities: string
}

interface Activity {
  id: number
  name: string
  city: string
  description: string
  duration_hours: number
  price: number
  category: string
  availability: string
}

interface Transport {
  id: number
  type: string
  origin: string
  destination: string
  price: number
  capacity: number
  departure_time: string
  arrival_time: string
}

interface FlightFilters {
  origin?: string
  destination?: string
  class_type?: string
}

interface HotelFilters {
  city?: string
  stars?: number
  max_price?: number
}

interface ActivityFilters {
  city?: string
  category?: string
}

interface TransportFilters {
  type?: string
  origin?: string
  destination?: string
}

## Design
- Clean and minimal UI
- Color palette: white background, slate/gray text, sky-500 as accent color
- Font: Inter (import from Google Fonts)
- No flashy gradients or heavy imagery
- Cards should have a subtle shadow and rounded corners
- Responsive layout (mobile + desktop)

## Pages

### Home.tsx
- Hero section with a simple headline and short subtext
- 4 category cards linking to /flights, /hotels, /activities, /transport
- Each category card shows an icon, label, and brief description

### Flights.tsx
- FilterPanel at top: origin, destination, class_type (dropdown)
- FlightList below rendering FlightCard for each result
- Show loading state while fetching

### Hotels.tsx
- FilterPanel at top: city, stars (1–5 dropdown), max_price (input)
- HotelList below rendering HotelCard for each result
- Show loading state while fetching

### Activities.tsx
- FilterPanel at top: city, category (dropdown)
- ActivityList below rendering ActivityCard for each result
- Show loading state while fetching

### Transport.tsx
- FilterPanel at top: type (dropdown), origin, destination
- TransportList below rendering TransportCard for each result
- Show loading state while fetching

## Cards

### FlightCard
- Show: origin → destination, airline, departure/arrival time, class type
- Show: price (prominent), seats available
- Clean horizontal layout

### HotelCard
- Show: name, city, star rating (as stars), price per night
- Show: amenities as small tags
- Show: rooms available

### ActivityCard
- Show: name, city, category tag, duration
- Show: price, availability

### TransportCard
- Show: type badge, origin → destination
- Show: departure/arrival time, capacity, price

## services/api.ts
- Base URL: http://localhost:8000
- Export one function per endpoint, all properly typed:
  - getFlights(filters: FlightFilters): Promise<Flight[]>
  - getHotels(filters: HotelFilters): Promise<Hotel[]>
  - getActivities(filters: ActivityFilters): Promise<Activity[]>
  - getTransports(filters: TransportFilters): Promise<Transport[]>
- Filters are passed as query params
- Handle errors gracefully and log to console

## Navbar.tsx
- Logo/site name on the left: "Travelbase"
- Navigation links: Home, Flights, Hotels, Activities, Transport
- Sticky at top, clean white background with a bottom border

## Rules
- No authentication
- No booking or checkout flow — browse only for now
- Keep components small and focused
- Use proper TypeScript types everywhere — no any
- Import all types from types/index.ts
- Use consistent spacing (Tailwind gap/padding scale)
- Empty state message when no results are returned
- No dummy/hardcoded data in components — always fetch from API