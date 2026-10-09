export interface ToastItem { id: number; text: string; kind: 'info' | 'error' }

export function useToast() {
  const toasts = useState<ToastItem[]>('toasts', () => [])
  let seq = useState('toast-seq', () => 0)

  function push(text: string, kind: ToastItem['kind'] = 'info', ms = 4000) {
    const id = ++seq.value
    toasts.value.push({ id, text, kind })
    setTimeout(() => dismiss(id), ms)
  }
  function dismiss(id: number) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }
  return { toasts, push, dismiss, error: (t: string) => push(t, 'error', 6000) }
}
