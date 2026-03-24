import { useEffect, useState } from 'react'
import type { Transport, TransportFilters } from '../types'
import { getTransports } from '../services/api'
import TransportList from '../components/transport/TransportList'
import FilterPanel from '../components/ui/FilterPanel'

const TYPES = ['car', 'ferry', 'bus', 'train']
const emptyFilters: TransportFilters = { type: '', origin: '', destination: '' }

export default function TransportPage() {
  const [transports, setTransports] = useState<Transport[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<TransportFilters>(emptyFilters)

  async function load(f: TransportFilters) {
    setLoading(true)
    const cleaned = Object.fromEntries(
      Object.entries(f).filter(([, v]) => v !== '' && v !== undefined)
    ) as TransportFilters
    setTransports(await getTransports(cleaned))
    setLoading(false)
  }

  useEffect(() => { load(filters) }, [])

  function handleReset() {
    setFilters(emptyFilters)
    load(emptyFilters)
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Transport</h1>
      <FilterPanel onReset={handleReset}>
        <select
          value={filters.type ?? ''}
          onChange={(e) => setFilters((p) => ({ ...p, type: e.target.value }))}
          className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
        >
          <option value="">All types</option>
          {TYPES.map((t) => (
            <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
          ))}
        </select>
        <input
          type="text"
          placeholder="Origin"
          value={filters.origin ?? ''}
          onChange={(e) => setFilters((p) => ({ ...p, origin: e.target.value }))}
          className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
        <input
          type="text"
          placeholder="Destination"
          value={filters.destination ?? ''}
          onChange={(e) => setFilters((p) => ({ ...p, destination: e.target.value }))}
          className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
        <button
          onClick={() => load(filters)}
          className="px-4 py-1.5 bg-sky-500 text-white text-sm rounded-lg hover:bg-sky-600 transition-colors"
        >
          Search
        </button>
      </FilterPanel>
      <TransportList transports={transports} loading={loading} />
    </div>
  )
}
