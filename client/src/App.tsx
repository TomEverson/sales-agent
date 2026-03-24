import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/ui/Navbar'
import Home from './pages/Home'
import Flights from './pages/Flights'
import Hotels from './pages/Hotels'
import Activities from './pages/Activities'
import Transport from './pages/Transport'

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/flights" element={<Flights />} />
          <Route path="/hotels" element={<Hotels />} />
          <Route path="/activities" element={<Activities />} />
          <Route path="/transport" element={<Transport />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}
