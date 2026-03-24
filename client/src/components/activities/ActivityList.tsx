import type { Activity } from '../../types'
import ActivityCard from './ActivityCard'

interface ActivityListProps {
  activities: Activity[]
  loading: boolean
}

export default function ActivityList({ activities, loading }: ActivityListProps) {
  if (loading) {
    return <p className="text-slate-400 text-sm text-center py-12">Loading activities...</p>
  }
  if (activities.length === 0) {
    return <p className="text-slate-400 text-sm text-center py-12">No activities found.</p>
  }
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {activities.map((a) => (
        <ActivityCard key={a.id} activity={a} />
      ))}
    </div>
  )
}
