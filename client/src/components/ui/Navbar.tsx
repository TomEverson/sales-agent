import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const links = [
  { to: '/', label: 'Home' },
  { to: '/flights', label: 'Flights' },
  { to: '/hotels', label: 'Hotels' },
  { to: '/activities', label: 'Activities' },
  { to: '/transport', label: 'Transport' },
  { to: '/bookings', label: 'Bookings' },
  { to: '/support', label: 'Support' },
]

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 flex items-center justify-between h-14">
        <NavLink to="/" className="text-sky-500 font-bold text-lg tracking-tight">
          Travelbase
        </NavLink>
        <div className="flex items-center gap-6">
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
          {user && (
            <button
              onClick={handleLogout}
              className="text-sm font-medium text-slate-600 hover:text-red-600 transition-colors"
            >
              Logout
            </button>
          )}
        </div>
      </div>
    </nav>
  )
}
