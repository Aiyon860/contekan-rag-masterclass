import type { ChatItem } from '~/types'

export function useChats() {
  const { api } = useApi()
  const toast = useToast()
  const chats = useState<ChatItem[]>('chats', () => [])
  const loaded = useState('chats-loaded', () => false)

  async function load() {
    try {
      chats.value = await api<ChatItem[]>('/chats')
      loaded.value = true
    } catch (e: any) {
      toast.error(e.message)
    }
  }

  /** Optimistic: chat langsung muncul di sidebar sebelum server membalas. */
  function addLocal(id: string, title: string) {
    if (!chats.value.some(c => c.id === id)) {
      chats.value.unshift({ id, title, updated_at: new Date().toISOString() })
    }
  }
  function touch(id: string, title?: string) {
    const i = chats.value.findIndex(c => c.id === id)
    if (i < 0) return
    const [c] = chats.value.splice(i, 1)
    if (title) c.title = title
    c.updated_at = new Date().toISOString()
    chats.value.unshift(c)
  }

  async function rename(id: string, title: string) {
    const c = chats.value.find(c => c.id === id)
    if (!c || !title.trim() || c.title === title.trim()) return
    const prev = c.title
    c.title = title.trim()
    try {
      await api(`/chats/${id}`, { method: 'PATCH', json: { title: c.title } })
    } catch (e: any) {
      c.title = prev
      toast.error(`Gagal ganti nama chat. ${e.message}`)
    }
  }

  async function remove(id: string) {
    const snapshot = [...chats.value]
    chats.value = chats.value.filter(c => c.id !== id)
    try {
      await api(`/chats/${id}`, { method: 'DELETE' })
    } catch (e: any) {
      chats.value = snapshot
      toast.error(`Gagal menghapus chat. ${e.message}`)
    }
  }

  return { chats, loaded, load, addLocal, touch, rename, remove }
}
