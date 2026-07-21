import { useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { FiMenu, FiX } from 'react-icons/fi'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import Chat from './pages/Chat'
import Equipment from './pages/Equipment'
import Graph from './pages/Graph'

export default function App() {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <BrowserRouter>
      <div className="h-screen flex flex-col bg-navy-950 text-steel-100">
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#0f1c33',
              color: '#eef1f4',
              border: '1px solid #3a4657',
              fontSize: '13px',
            },
          }}
        />

        <div className="flex items-center relative">
          <button
            onClick={() => setMobileOpen(true)}
            className="lg:hidden absolute left-3 top-1/2 -translate-y-1/2 z-30 w-10 h-10 flex items-center justify-center rounded-lg text-steel-300 hover:bg-steel-800"
            aria-label="Open menu"
          >
            <FiMenu size={20} />
          </button>
          <div className="flex-1">
            <Navbar />
          </div>
        </div>

        <div className="flex flex-1 min-h-0">
          {/* Desktop sidebar */}
          <aside className="hidden lg:block w-60 shrink-0 border-r border-steel-800 bg-navy-900 overflow-y-auto">
            <Sidebar />
          </aside>

          {/* Mobile drawer */}
          {mobileOpen && (
            <div className="fixed inset-0 z-40 lg:hidden">
              <div
                className="absolute inset-0 bg-black/60"
                onClick={() => setMobileOpen(false)}
              />
              <div className="absolute left-0 top-0 bottom-0 w-64 bg-navy-900 border-r border-steel-800 animate-fade-in">
                <div className="flex items-center justify-between p-4 border-b border-steel-800">
                  <span className="text-sm font-semibold text-steel-100">Menu</span>
                  <button
                    onClick={() => setMobileOpen(false)}
                    className="text-steel-400 hover:text-steel-100"
                    aria-label="Close menu"
                  >
                    <FiX size={18} />
                  </button>
                </div>
                <Sidebar onNavigate={() => setMobileOpen(false)} />
              </div>
            </div>
          )}

          <main className="flex-1 min-w-0 overflow-y-auto p-4 sm:p-6 lg:p-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/equipment" element={<Equipment />} />
              <Route path="/graph" element={<Graph />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}
