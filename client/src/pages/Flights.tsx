import { useEffect, useState } from 'react'
import type { Flight, FlightFilters } from '../types'
import { getFlights } from '../services/api'
import FlightList from '../components/flights/FlightList'
import FilterPanel from '../components/ui/FilterPanel'

const CLASS_TYPES = ['economy', 'business', 'first']

const emptyFilters: FlightFilters = { origin: '', destination: '', class_type: '' }

export default function Flights() {
  const [flights, setFlights] = useState<Flight[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<FlightFilters>(emptyFilters)

  async function load(f: FlightFilters) {
    setLoading(true)
    const cleaned = Object.fromEntries(
      Object.entries(f).filter(([, v]) => v !== '' && v !== undefined)
    ) as FlightFilters
    setFlights(await getFlights(cleaned))
    setLoading(false)
  }

  useEffect(() => { load(filters) }, [])

  function handleChange(key: keyof FlightFilters, value: string) {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  function handleSearch() { load(filters) }

  function handleReset() {
    setFilters(emptyFilters)
    load(emptyFilters)
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Flights</h1>
      <FilterPanel onReset={handleReset}>
        <input
          type="text"
          placeholder="Origin"
          value={filters.origin ?? ''}
          onChange={(e) => handleChange('origin', e.target.value)}
          className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
        <input
          type="text"
          placeholder="Destination"
          value={filters.destination ?? ''}
          onChange={(e) => handleChange('destination', e.target.value)}
          className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
        <select
          value={filters.class_type ?? ''}
          onChange={(e) => handleChange('class_type', e.target.value)}
          className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
        >
          <option value="">All classes</option>
          {CLASS_TYPES.map((c) => (
            <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
          ))}
        </select>
        <button
          onClick={handleSearch}
          className="px-4 py-1.5 bg-sky-500 text-white text-sm rounded-lg hover:bg-sky-600 transition-colors"
        >
          Search
        </button>
      </FilterPanel>
      <FlightList flights={flights} loading={loading} />
    </div>
  )
}
