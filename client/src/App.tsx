import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Navbar from './components/ui/Navbar'
import Home from './pages/Home'
import Flights from './pages/Flights'
import Hotels from './pages/Hotels'
import Activities from './pages/Activities'
import Transport from './pages/Transport'
import Bookings from './pages/Bookings'
import Support from './pages/Support'
import Login from './pages/Login'
import type { ReactNode } from 'react'

function PrivateRoute({ children }: { children: ReactNode }) {
  const { user, isLoading } = useAuth()
  if (isLoading) return null
  return user ? <>{children}</> : <Navigate to="/login" replace />
}

function AppRoutes() {
  return (
    <>
      <Navbar />
      <main>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<PrivateRoute><Home /></PrivateRoute>} />
          <Route path="/flights" element={<PrivateRoute><Flights /></PrivateRoute>} />
          <Route path="/hotels" element={<PrivateRoute><Hotels /></PrivateRoute>} />
          <Route path="/activities" element={<PrivateRoute><Activities /></PrivateRoute>} />
          <Route path="/transport" element={<PrivateRoute><Transport /></PrivateRoute>} />
          <Route path="/bookings" element={<PrivateRoute><Bookings /></PrivateRoute>} />
          <Route path="/support" element={<PrivateRoute><Support /></PrivateRoute>} />
        </Routes>
      </main>
    </>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
