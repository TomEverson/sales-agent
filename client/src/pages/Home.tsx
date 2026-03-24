import { Link } from 'react-router-dom'

const categories = [
  {
    to: '/flights',
    icon: '✈️',
    label: 'Flights',
    description: 'Search available flights across Southeast Asia',
  },
  {
    to: '/hotels',
    icon: '🏨',
    label: 'Hotels',
    description: 'Find hotels from budget stays to 5-star resorts',
  },
  {
    to: '/activities',
    icon: '🎭',
    label: 'Activities',
    description: 'Explore tours, food experiences, and adventures',
  },
  {
    to: '/transport',
    icon: '🚢',
    label: 'Transport',
    description: 'Ferries, trains, buses, and private transfers',
  },
]

export default function Home() {
  return (
    <div className="max-w-6xl mx-auto px-4 py-16">
      <div className="text-center mb-14">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">
          Plan your next trip in Southeast Asia
        </h1>
        <p className="text-slate-500 text-lg max-w-xl mx-auto">
          Browse flights, hotels, activities, and transport options across Bangkok, Bali, Singapore, Phuket, and more.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {categories.map(({ to, icon, label, description }) => (
          <Link
            key={to}
            to={to}
            className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-md hover:border-sky-300 transition-all group"
          >
            <span className="text-3xl mb-3 block">{icon}</span>
            <h2 className="text-lg font-semibold text-slate-900 mb-1 group-hover:text-sky-600 transition-colors">
              {label}
            </h2>
            <p className="text-sm text-slate-500">{description}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
