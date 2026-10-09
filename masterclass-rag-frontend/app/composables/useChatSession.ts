import type { Attachment, Msg } from '~/types'

/** Satu sesi chat: pesan, streaming SSE, stop, regenerate. */
export function useChatSession(chatId: () => string) {
  const { api, url } = useApi()
  const toast = useToast()
  const chats = useChats()
  const messages = ref<Msg[]>([])
  const busy = ref(false)
  let ctrl: AbortController | null = null

  async function loadMessages() {
    const id = chatId()
    try {
      const rows = await api<any[]>(`/chats/${id}/messages`)
      if (id !== chatId()) return
      messages.value = rows.map(r => ({
        id: r.id, role: r.role, content: r.content, status: r.status,
        sources: r.sources ?? [], augmented_prompt: r.augmented_prompt, grounded: r.grounded, model: r.model,
        retrieved: r.role === 'assistant' ? true : undefined,
        attachments: r.attachments ?? [],
      }))
    } catch (e: any) { toast.error(e.message) }
  }

  async function run(path: string, body: unknown, assistant: Msg) {
    busy.value = true
    ctrl = new AbortController()
    const target = messages.value.find(m => m.id === assistant.id)!
    try {
      const res = await fetch(url(path), {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : undefined, signal: ctrl.signal,
      })
      if (!res.ok || !res.body) {
        let msg = 'Gagal menghubungi server.'
        try { msg = (await res.json()).detail ?? msg } catch {}
        throw new Error(msg)
      }
      for await (const ev of readSse(res)) {
        if (ev.event === 'meta') {
          if (ev.data.assistant_message_id) target.id = ev.data.assistant_message_id
          if (ev.data.title) chats.touch(chatId(), ev.data.title)
        } else if (ev.event === 'waiting') {
          target.waitingFor = ev.data.documents
        } else if (ev.event === 'sources') {
          target.waitingFor = undefined
          if (ev.data.skipped?.length) toast.error(`Lampiran ${ev.data.skipped.join(', ')} gagal diproses, jadi nggak ikut dipakai.`)
          target.sources = ev.data.sources
          target.augmented_prompt = ev.data.augmented_prompt
          target.grounded = ev.data.grounded
          target.retrieved = true
        } else if (ev.event === 'token') {
          target.content += ev.data.text
        } else if (ev.event === 'error') {
          target.status = 'error'
          target.content = target.content || ev.data.message
        } else if (ev.event === 'done') {
          target.status = ev.data.status
        }
      }
      if (target.status === 'streaming') target.status = 'complete'
    } catch (e: any) {
      if (e.name === 'AbortError') target.status = 'stopped'
      else {
        target.status = 'error'
        target.content = target.content || `Maaf, ada kendala: ${e.message}`
        toast.error(e.message)
      }
    } finally {
      busy.value = false
      ctrl = null
      chats.touch(chatId())
    }
  }

  function send(text: string, attachments: Attachment[] = []) {
    const user: Msg = { id: uid(), role: 'user', content: text, status: 'complete', sources: [], augmented_prompt: null, model: null, attachments }
    const asst: Msg = { id: uid(), role: 'assistant', content: '', status: 'streaming', sources: [], augmented_prompt: null, model: null, retrieved: false }
    messages.value.push(user, asst)
    chats.addLocal(chatId(), text.slice(0, 50))
    return run(`/chats/${chatId()}/messages`, { content: text, user_message_id: user.id, assistant_message_id: asst.id, attachment_ids: attachments.map(a => a.document_id) }, asst)
  }

  function regenerate() {
    if (busy.value) return
    const last = messages.value[messages.value.length - 1]
    if (last?.role === 'assistant') messages.value.pop()
    const asst: Msg = { id: uid(), role: 'assistant', content: '', status: 'streaming', sources: [], augmented_prompt: null, model: null, retrieved: false }
    messages.value.push(asst)
    return run(`/chats/${chatId()}/regenerate`, null, asst)
  }

  function stop() { ctrl?.abort() }

  return { messages, busy, loadMessages, send, regenerate, stop }
}
