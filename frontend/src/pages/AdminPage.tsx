import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../utils/api'
import { useState } from 'react'

interface Setting {
  value: string | null
  description: string
}

const LABELS: Record<string, string> = {
  registration_open: 'Разрешить самостоятельную регистрацию',
  default_locale: 'Язык по умолчанию',
  session_timeout_minutes: 'Время сессии (минут)',
  require_2fa: 'Требовать 2FA',
}

export default function AdminPage() {
  const qc = useQueryClient()
  const { data: settings } = useQuery<Record<string, Setting>>({
    queryKey: ['admin-settings'],
    queryFn: () => api.get('/admin/settings').then((r) => r.data),
  })

  const { data: users } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => api.get('/admin/users').then((r) => r.data),
  })

  const updateSetting = useMutation({
    mutationFn: ({ key, value }: { key: string; value: string }) =>
      api.put(`/admin/settings/${key}`, { value }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-settings'] }),
  })

  const updateRole = useMutation({
    mutationFn: ({ id, role }: { id: number; role: string }) =>
      api.patch(`/admin/users/${id}/role`, { role }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-users'] }),
  })

  const toggleActive = useMutation({
    mutationFn: ({ id, is_active }: { id: number; is_active: boolean }) =>
      api.patch(`/admin/users/${id}/status`, { is_active }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-users'] }),
  })

  const handleToggle = (key: string, current: string) => {
    const newVal = current === 'true' ? 'false' : 'true'
    updateSetting.mutate({ key, value: newVal })
  }

  return (
    <div className="space-y-10">
      <h1 className="text-2xl font-bold text-gray-900">Настройки системы</h1>

      {/* ── Системные настройки ── */}
      <section className="bg-white rounded-xl border p-6 space-y-4">
        <h2 className="font-semibold text-lg text-gray-800">Параметры системы</h2>
        {settings &&
          Object.entries(settings).map(([key, setting]) => (
            <div key={key} className="flex items-center justify-between py-2 border-b last:border-0">
              <div>
                <p className="font-medium text-gray-700">{LABELS[key] || key}</p>
                <p className="text-xs text-gray-400">{setting.description}</p>
              </div>
              {key === 'registration_open' || key === 'require_2fa' ? (
                <button
                  onClick={() => handleToggle(key, setting.value ?? 'false')}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    setting.value === 'true' ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                      setting.value === 'true' ? 'translate-x-7' : 'translate-x-1'
                    }`}
                  />
                </button>
              ) : (
                <span className="text-gray-600 text-sm font-mono">{setting.value}</span>
              )}
            </div>
          ))}
      </section>

      {/* ── Пользователи ── */}
      <section className="bg-white rounded-xl border p-6">
        <h2 className="font-semibold text-lg text-gray-800 mb-4">Пользователи</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="py-2 pr-4">Пользователь</th>
                <th className="py-2 pr-4">Telegram</th>
                <th className="py-2 pr-4">Роль</th>
                <th className="py-2 pr-4">Последний вход</th>
                <th className="py-2">Статус</th>
              </tr>
            </thead>
            <tbody>
              {users?.map((u: any) => (
                <tr key={u.id} className="border-b hover:bg-gray-50">
                  <td className="py-2 pr-4 font-medium">
                    {u.first_name} {u.last_name}
                  </td>
                  <td className="py-2 pr-4 text-gray-500">@{u.username || u.telegram_id}</td>
                  <td className="py-2 pr-4">
                    <select
                      value={u.role}
                      onChange={(e) => updateRole.mutate({ id: u.id, role: e.target.value })}
                      className="border rounded px-2 py-1 text-xs"
                    >
                      <option value="admin">Администратор</option>
                      <option value="manager">Менеджер</option>
                      <option value="client">Клиент</option>
                    </select>
                  </td>
                  <td className="py-2 pr-4 text-gray-400 text-xs">
                    {u.last_login ? new Date(u.last_login).toLocaleString('ru') : '—'}
                  </td>
                  <td className="py-2">
                    <button
                      onClick={() => toggleActive.mutate({ id: u.id, is_active: !u.is_active })}
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        u.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-600'
                      }`}
                    >
                      {u.is_active ? 'Активен' : 'Заблокирован'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
