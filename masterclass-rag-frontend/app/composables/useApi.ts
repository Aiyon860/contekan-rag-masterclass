export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

export function useApi() {
  const base = (useRuntimeConfig().public.apiBase as string) || ''
  const url = (path: string) => `${base}/api${path}`

  async function api<T = any>(path: string, init: RequestInit & { json?: unknown } = {}): Promise<T> {
    const headers = new Headers(init.headers)
    let body = init.body
    if (init.json !== undefined) {
      headers.set('Content-Type', 'application/json')
      body = JSON.stringify(init.json)
    }
    let res: Response
    try {
      res = await fetch(url(path), { ...init, headers, body })
    } catch {
      throw new ApiError('Nggak bisa terhubung ke server. Cek apakah backend-nya sudah jalan.', 0)
    }
    if (!res.ok) {
      let msg = 'Ada yang salah di server. Coba lagi ya.'
      try {
        const j = await res.json()
        if (typeof j.detail === 'string') msg = j.detail
        else if (Array.isArray(j.detail) && j.detail[0]?.msg) msg = j.detail[0].msg
      } catch {}
      throw new ApiError(msg, res.status)
    }
    if (res.status === 204) return undefined as T
    return res.json()
  }

  return { api, url }
}
