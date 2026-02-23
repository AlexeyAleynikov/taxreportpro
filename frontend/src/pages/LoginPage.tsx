import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api from '../utils/api'

declare global {
  interface Window {
    TelegramLoginWidget: { dataOnauth: (user: object) => void }
  }
}

export default function LoginPage() {
  const navigate = useNavigate()
  const { setTokens, setUser, accessToken } = useAuthStore()

  useEffect(() => {
    if (accessToken) navigate('/', { replace: true })
  }, [accessToken, navigate])

  useEffect(() => {
    // Колбэк, который вызовет Telegram после авторизации
    window.TelegramLoginWidget = {
      dataOnauth: async (tgData) => {
        try {
          const resp = await api.post('/auth/telegram', tgData)
          setTokens(resp.data.access_token, resp.data.refresh_token)
          setUser(resp.data.user)
          navigate('/', { replace: true })
        } catch (err: any) {
          alert(err?.response?.data?.detail || 'Ошибка входа')
        }
      },
    }

    // Добавляем скрипт виджета динамически
    const BOT = import.meta.env.VITE_TELEGRAM_BOT_USERNAME
    const script = document.createElement('script')
    script.src = 'https://telegram.org/js/telegram-widget.js?22'
    script.setAttribute('data-telegram-login', BOT)
    script.setAttribute('data-size', 'large')
    script.setAttribute('data-radius', '8')
    script.setAttribute('data-onauth', 'TelegramLoginWidget.dataOnauth(user)')
    script.setAttribute('data-request-access', 'write')
    script.async = true

    const container = document.getElementById('telegram-login')
    container?.appendChild(script)
    return () => { container?.removeChild(script) }
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-xl p-10 max-w-md w-full text-center">
        <div className="text-4xl mb-4">📊</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">TaxReport Pro</h1>
        <p className="text-gray-500 mb-8 text-sm">
          Система анализа налоговых данных РФ и США
        </p>
        <div id="telegram-login" className="flex justify-center" />
        <p className="text-xs text-gray-400 mt-6">
          Вход осуществляется через аккаунт Telegram — пароли не используются
        </p>
      </div>
    </div>
  )
}
