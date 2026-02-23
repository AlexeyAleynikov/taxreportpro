import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../store/authStore'

export default function Layout() {
  const { t } = useTranslation()
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
      isActive ? 'bg-indigo-100 text-indigo-700' : 'text-gray-600 hover:bg-gray-100'
    }`

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-56 bg-white border-r flex flex-col shrink-0">
        <div className="p-4 border-b">
          <span className="font-bold text-indigo-700 text-lg">📊 TaxReport</span>
        </div>

        <nav className="flex-1 p-3 space-y-1">
          <NavLink to="/" end className={navClass}>🏠 {t('dashboard')}</NavLink>
          <NavLink to="/clients" className={navClass}>👥 {t('clients')}</NavLink>
          <NavLink to="/reports" className={navClass}>📄 {t('reports')}</NavLink>
          {user?.role === 'admin' && (
            <NavLink to="/admin" className={navClass}>⚙️ {t('admin')}</NavLink>
          )}
        </nav>

        <div className="p-3 border-t">
          <div className="text-xs text-gray-400 mb-2">
            {user?.first_name} {user?.last_name}
            <span className="ml-1 px-1.5 py-0.5 bg-gray-100 rounded text-gray-500">
              {user?.role}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="w-full text-left text-sm text-red-500 hover:text-red-700 px-2 py-1 rounded hover:bg-red-50"
          >
            ↩ {t('logout')}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-6 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
