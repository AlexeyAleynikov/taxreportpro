import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

const resources = {
  ru: {
    translation: {
      dashboard: 'Дашборд',
      clients: 'Клиенты',
      reports: 'Отчёты',
      admin: 'Администрирование',
      logout: 'Выйти',
      taxYear: 'Налоговый год',
      jurisdiction: 'Юрисдикция',
      grossIncome: 'Совокупный доход',
      taxableIncome: 'Налоговая база',
      taxDue: 'Начисленный налог',
      withheld: 'Удержанный налог',
      refundOrOwe: 'К возврату / доплате',
      effectiveRate: 'Эффективная ставка',
      addClient: 'Добавить клиента',
      save: 'Сохранить',
      cancel: 'Отмена',
    },
  },
  en: {
    translation: {
      dashboard: 'Dashboard',
      clients: 'Clients',
      reports: 'Reports',
      admin: 'Administration',
      logout: 'Log out',
      taxYear: 'Tax Year',
      jurisdiction: 'Jurisdiction',
      grossIncome: 'Gross Income',
      taxableIncome: 'Taxable Income',
      taxDue: 'Tax Due',
      withheld: 'Withheld Tax',
      refundOrOwe: 'Refund / Owe',
      effectiveRate: 'Effective Rate',
      addClient: 'Add Client',
      save: 'Save',
      cancel: 'Cancel',
    },
  },
}

i18n.use(initReactI18next).init({
  resources,
  lng: 'ru',
  fallbackLng: 'ru',
  interpolation: { escapeValue: false },
})

export default i18n
