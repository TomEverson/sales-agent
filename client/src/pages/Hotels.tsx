import { useEffect, useState } from 'react'
import type { Hotel, HotelFilters } from '../types'
import { getHotels } from '../services/api'
import HotelList from '../components/hotels/HotelList'
import FilterPanel from '../components/ui/FilterPanel'

const emptyFilters: HotelFilters = { city: '', stars: undefined, max_price: undefined }

export default function Hotels() {
  const [hotels, setHotels] = useState<Hotel[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<HotelFilters>(emptyFilters)

  async function load(f: HotelFilters) {
    setLoading(true)
    const cleaned = Object.fromEntries(
      Object.entries(f).filter(([, v]) => v !== '' && v !== undefined && v !== null)
    ) as HotelFilters
    setHotels(await getHotels(cleaned))
    setLoading(false)
  }

  useEffect(() => { load(filters) }, [])

  function handleReset() {
    setFilters(emptyFilters)
    load(emptyFilters)
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Hotels</h1>
      <FilterPanel onReset={handleReset}>
        <input
          type="text"
          placeholder="City"
          value={filters.city ?? ''}
          onChange={(e) => setFilters((p) => ({ ...p, city: e.target.value }))}
          className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
        <select
          value={filters.stars ?? ''}
          onChange={(e) => setFilters((p) => ({ ...p, stars: e.target.value ? Number(e.target.value) : undefined }))}
          className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
        >
          <option value="">Any stars</option>
          {[1, 2, 3, 4, 5].map((s) => (
            <option key={s} value={s}>{s} star{s > 1 ? 's' : ''}</option>
          ))}
        </select>
        <input
          type="number"
          placeholder="Max price / night"
          value={filters.max_price ?? ''}
          onChange={(e) => setFilters((p) => ({ ...p, max_price: e.target.value ? Number(e.target.value) : undefined }))}
          className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 w-36"
        />
        <button
          onClick={() => load(filters)}
          className="px-4 py-1.5 bg-sky-500 text-white text-sm rounded-lg hover:bg-sky-600 transition-colors"
        >
          Search
        </button>
      </FilterPanel>
      <HotelList hotels={hotels} loading={loading} />
    </div>
  )
}
