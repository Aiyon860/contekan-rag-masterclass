import { marked } from 'marked'
import DOMPurify from 'dompurify'

marked.setOptions({ gfm: true, breaks: true })

export function renderMarkdown(src: string): string {
  return DOMPurify.sanitize(marked.parse(src, { async: false }) as string, {
    ADD_ATTR: ['target'],
  })
}

export function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`
  return `${(n / 1024 / 1024).toFixed(1)} MB`
}

export function uid(): string {
  return crypto.randomUUID()
}
