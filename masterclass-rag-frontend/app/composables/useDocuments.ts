import type { DocItem } from '~/types'

const ALLOWED = ['.txt', '.md', '.pdf', '.docx', '.xlsx', '.csv']

export function useDocuments() {
  const { api } = useApi()
  const toast = useToast()
  const docs = useState<DocItem[]>('docs', () => [])
  const loaded = useState('docs-loaded', () => false)
  const { settings } = useSettings()
  const polling = useState<ReturnType<typeof setInterval> | null>('docs-poll', () => null)

  async function load() {
    try {
      docs.value = await api<DocItem[]>('/documents')
      loaded.value = true
      syncPolling()
    } catch (e: any) {
      toast.error(e.message)
    }
  }

  function syncPolling() {
    const need = docs.value.some(d => d.status === 'processing')
    if (need && !polling.value) {
      polling.value = setInterval(async () => {
        try {
          const fresh = await api<DocItem[]>('/documents')
          const done = docs.value.filter(d => d.status === 'processing' && !d.pending)
          docs.value = [...docs.value.filter(d => d.pending), ...fresh.filter(f => !docs.value.some(d => d.pending && d.original_filename === f.original_filename && f.status === 'processing'))]
          for (const d of done) {
            const now = fresh.find(f => f.id === d.id)
            if (now?.status === 'ready') toast.push(`“${now.name}” sudah siap dipakai (${now.chunk_count} potongan).`)
            if (now?.status === 'failed') toast.error(`“${now.name}” gagal diproses. ${now.error ?? ''}`)
          }
          if (!docs.value.some(d => d.status === 'processing')) stop()
        } catch {}
      }, 1500)
    } else if (!need) stop()
  }
  function stop() {
    if (polling.value) { clearInterval(polling.value); polling.value = null }
  }

  /** Validasi di sisi client; server tetap memvalidasi ulang. */
  function validate(file: File): string | null {
    const ext = '.' + (file.name.split('.').pop() ?? '').toLowerCase()
    if (!ALLOWED.includes(ext)) return `“${file.name}”: format belum didukung. Pakai ${ALLOWED.join(', ')}.`
    const max = settings.value?.max_file_size_mb ?? 10
    if (file.size > max * 1024 * 1024) return `“${file.name}” lebih dari ${max} MB.`
    if (file.size === 0) return `“${file.name}” kosong.`
    return null
  }

  async function upload(file: File): Promise<DocItem | null> {
    const err = validate(file)
    if (err) { toast.error(err); return null }
    // Optimistic: kartu langsung muncul dengan status Memproses
    const tempId = `tmp-${uid()}`
    docs.value.unshift({
      id: tempId, name: file.name.replace(/\.[^.]+$/, ''), original_filename: file.name,
      ext: '.' + file.name.split('.').pop()!.toLowerCase(), size_bytes: file.size, source: 'file',
      status: 'processing', error: null, chunk_count: 0, enabled: true,
      created_at: new Date().toISOString(), pending: true,
    })
    const fd = new FormData()
    fd.append('file', file)
    try {
      const real = await api<DocItem>('/documents', { method: 'POST', body: fd })
      docs.value = docs.value.map(d => (d.id === tempId ? real : d))
      syncPolling()
      return real
    } catch (e: any) {
      docs.value = docs.value.filter(d => d.id !== tempId)
      toast.error(e.message)
      return null
    }
  }

  async function addText(title: string, content: string): Promise<boolean> {
    try {
      const real = await api<DocItem>('/documents/text', { method: 'POST', json: { title, content } })
      docs.value.unshift(real)
      syncPolling()
      return true
    } catch (e: any) {
      toast.error(e.message)
      return false
    }
  }

  async function toggle(d: DocItem) {
    const prev = d.enabled
    d.enabled = !prev
    try {
      await api(`/documents/${d.id}`, { method: 'PATCH', json: { enabled: d.enabled } })
    } catch (e: any) {
      d.enabled = prev
      toast.error(e.message)
    }
  }

  async function remove(d: DocItem) {
    const snapshot = [...docs.value]
    docs.value = docs.value.filter(x => x.id !== d.id)
    try {
      await api(`/documents/${d.id}`, { method: 'DELETE' })
    } catch (e: any) {
      docs.value = snapshot
      toast.error(`Gagal menghapus dokumen. ${e.message}`)
    }
  }

  return { docs, loaded, load, upload, addText, toggle, remove, validate, allowed: ALLOWED }
}
