import type { Activity } from '../../types'

interface ActivityCardProps {
  activity: Activity
}

const categoryColors: Record<string, string> = {
  adventure: 'bg-emerald-100 text-emerald-700',
  culture: 'bg-purple-100 text-purple-700',
  food: 'bg-orange-100 text-orange-700',
  nature: 'bg-green-100 text-green-700',
}

export default function ActivityCard({ activity }: ActivityCardProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
      <div className="flex items-start justify-between gap-4 mb-2">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-slate-900">{activity.name}</h3>
          <p className="text-sm text-slate-500">{activity.city}</p>
        </div>
        <p className="text-lg font-bold text-sky-600 shrink-0">${activity.price.toFixed(2)}</p>
      </div>
      <p className="text-sm text-slate-600 mb-3">{activity.description}</p>
      <div className="flex items-center gap-2 flex-wrap">
        <span
          className={`text-xs font-medium px-2 py-0.5 rounded-full ${categoryColors[activity.category] ?? 'bg-slate-100 text-slate-600'}`}
        >
          {activity.category}
        </span>
        <span className="text-xs text-slate-400">{activity.duration_hours}h</span>
        <span className="text-xs text-slate-400">· {activity.availability}</span>
      </div>
    </div>
  )
}
