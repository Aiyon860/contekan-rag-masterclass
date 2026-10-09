export interface Source {
  document_id: string
  document_name: string
  chunk_index: number
  page: number | null
  text: string
  score: number
  deleted?: boolean
  /** potongan dipakai ulang dari jawaban sebelumnya (pertanyaan lanjutan) */
  reused?: boolean
}

export type MessageStatus = 'streaming' | 'complete' | 'stopped' | 'error'

export interface Attachment {
  document_id: string
  name: string
  ext: string
  deleted?: boolean
}

export interface Msg {
  id: string
  role: 'user' | 'assistant'
  content: string
  status: MessageStatus
  sources: Source[]
  augmented_prompt: string | null
  /** false = dijawab dari pengetahuan model, tanpa potongan dokumen */
  grounded?: boolean
  model: string | null
  /** true setelah event `sources` datang (retrieval selesai), dipakai indikator proses */
  retrieved?: boolean
  attachments?: Attachment[]
  /** nama dokumen lampiran yang sedang ditunggu backend */
  waitingFor?: string[]
}

export interface ChatItem {
  id: string
  title: string
  updated_at: string
}

export interface DocItem {
  id: string
  name: string
  original_filename: string
  ext: string
  size_bytes: number
  source: 'file' | 'text'
  status: 'processing' | 'ready' | 'failed'
  error: string | null
  chunk_count: number
  enabled: boolean
  created_at: string
  /** placeholder optimistic sebelum server membalas */
  pending?: boolean
}

export interface AppSettings {
  top_k: number
  similarity_threshold: number
  max_file_size_mb: number
  chat_model: string
  system_prompt: string
  default_system_prompt: string
}

export interface PreviewData {
  id: string
  name: string
  ext: string
  kind: 'pdf' | 'markdown' | 'text' | 'table'
  url?: string
  text?: string
  sheets?: { name: string; rows: string[][] }[]
}
