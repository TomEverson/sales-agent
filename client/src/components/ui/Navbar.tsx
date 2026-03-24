import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Home' },
  { to: '/flights', label: 'Flights' },
  { to: '/hotels', label: 'Hotels' },
  { to: '/activities', label: 'Activities' },
  { to: '/transport', label: 'Transport' },
]

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 flex items-center justify-between h-14">
        <NavLink to="/" className="text-sky-500 font-bold text-lg tracking-tight">
          Travelbase
        </NavLink>
        <div className="flex gap-6">
          {links.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `text-sm font-medium transition-colors ${
                  isActive ? 'text-sky-500' : 'text-slate-600 hover:text-slate-900'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  )
}
