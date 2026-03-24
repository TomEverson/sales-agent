interface FilterPanelProps {
  children: React.ReactNode
  onReset: () => void
}

export default function FilterPanel({ children, onReset }: FilterPanelProps) {
  return (
    <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-6">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-slate-700">Filters</span>
        <button
          onClick={onReset}
          className="text-xs text-sky-500 hover:text-sky-600 font-medium"
        >
          Reset
        </button>
      </div>
      <div className="flex flex-wrap gap-3">{children}</div>
    </div>
  )
}
