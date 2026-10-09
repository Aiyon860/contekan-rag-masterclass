import type { AppSettings } from '~/types'

export function useSettings() {
  const { api } = useApi()
  const toast = useToast()
  const settings = useState<AppSettings | null>('settings', () => null)
  const models = useState<string[]>('models', () => [])

  async function load() {
    try {
      settings.value = await api<AppSettings>('/settings')
      models.value = (await api<{ models: string[] }>('/settings/models')).models
    } catch (e: any) {
      toast.error(e.message)
    }
  }

  async function save(next: Omit<AppSettings, 'default_system_prompt'>): Promise<boolean> {
    const prev = settings.value
    settings.value = { ...(prev as AppSettings), ...next }
    try {
      settings.value = { ...(settings.value as AppSettings), ...(await api<AppSettings>("/settings", { method: "PUT", json: next })) }
      toast.push('Pengaturan tersimpan.')
      return true
    } catch (e: any) {
      settings.value = prev
      toast.error(e.message)
      return false
    }
  }

  return { settings, models, load, save }
}
