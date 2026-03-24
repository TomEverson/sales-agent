import { useEffect, useState } from 'react'
import type { Activity, ActivityFilters } from '../types'
import { getActivities } from '../services/api'
import ActivityList from '../components/activities/ActivityList'
import FilterPanel from '../components/ui/FilterPanel'

const CATEGORIES = ['adventure', 'culture', 'food', 'nature']
const emptyFilters: ActivityFilters = { city: '', category: '' }

export default function Activities() {
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<ActivityFilters>(emptyFilters)

  async function load(f: ActivityFilters) {
    setLoading(true)
    const cleaned = Object.fromEntries(
      Object.entries(f).filter(([, v]) => v !== '' && v !== undefined)
    ) as ActivityFilters
    setActivities(await getActivities(cleaned))
    setLoading(false)
  }

  useEffect(() => { load(filters) }, [])

  function handleReset() {
    setFilters(emptyFilters)
    load(emptyFilters)
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Activities</h1>
      <FilterPanel onReset={handleReset}>
        <input
          type="text"
          placeholder="City"
          value={filters.city ?? ''}
          onChange={(e) => setFilters((p) => ({ ...p, city: e.target.value }))}
          className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
        <select
          value={filters.category ?? ''}
          onChange={(e) => setFilters((p) => ({ ...p, category: e.target.value }))}
          className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
        >
          <option value="">All categories</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
          ))}
        </select>
        <button
          onClick={() => load(filters)}
          className="px-4 py-1.5 bg-sky-500 text-white text-sm rounded-lg hover:bg-sky-600 transition-colors"
        >
          Search
        </button>
      </FilterPanel>
      <ActivityList activities={activities} loading={loading} />
    </div>
  )
}
