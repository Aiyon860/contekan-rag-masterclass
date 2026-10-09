export function useHealth() {
  const { api } = useApi()
  const health = useState<{ ollama: boolean; missing_models: string[]; error?: string } | null>('health', () => null)
  async function check() {
    try {
      health.value = await api('/health')
    } catch {
      health.value = { ollama: false, missing_models: [], error: 'backend' }
    }
  }
  return { health, check }
}
