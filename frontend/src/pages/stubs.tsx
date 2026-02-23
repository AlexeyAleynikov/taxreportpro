// Заглушки страниц — реализуются в следующих итерациях

export function DashboardPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Дашборд</h1>
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Клиентов', value: '—' },
          { label: 'Открытых лет', value: '—' },
          { label: 'Расчётов за месяц', value: '—' },
        ].map((card) => (
          <div key={card.label} className="bg-white rounded-xl border p-6">
            <p className="text-sm text-gray-500">{card.label}</p>
            <p className="text-3xl font-bold text-indigo-600 mt-1">{card.value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export function ClientsPage() {
  return <div className="text-gray-700">Список клиентов — в разработке</div>
}

export function ClientDetailPage() {
  return <div className="text-gray-700">Профиль клиента — в разработке</div>
}

export function TaxYearPage() {
  return <div className="text-gray-700">Налоговый год — в разработке</div>
}

export function ReportsPage() {
  return <div className="text-gray-700">Отчёты — в разработке</div>
}
