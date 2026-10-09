export interface PreviewTarget {
  docId: string
  name: string
  /** potongan yang dipakai AI, untuk di-highlight */
  chunk?: string
  page?: number | null
}

export function usePreview() {
  const target = useState<PreviewTarget | null>('preview', () => null)
  const open = (t: PreviewTarget) => { target.value = t }
  const close = () => { target.value = null }
  return { target, open, close }
}
