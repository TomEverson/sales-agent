import type { Transport } from '../../types'
import TransportCard from './TransportCard'

interface TransportListProps {
  transports: Transport[]
  loading: boolean
}

export default function TransportList({ transports, loading }: TransportListProps) {
  if (loading) {
    return <p className="text-slate-400 text-sm text-center py-12">Loading transport...</p>
  }
  if (transports.length === 0) {
    return <p className="text-slate-400 text-sm text-center py-12">No transport options found.</p>
  }
  return (
    <div className="flex flex-col gap-3">
      {transports.map((t) => (
        <TransportCard key={t.id} transport={t} />
      ))}
    </div>
  )
}
