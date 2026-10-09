<script setup lang="ts">
import type { Attachment } from '~/types'

interface Staged { key: string; name: string; ext: string; size: number; docId: string | null }

const props = defineProps<{ busy: boolean; autofocus?: boolean }>()
const emit = defineEmits<{ send: [text: string, attachments: Attachment[]]; stop: [] }>()

const text = ref('')
const area = ref<HTMLTextAreaElement>()
const file = ref<HTMLInputElement>()
const over = ref(false)
const staged = ref<Staged[]>([])
const { docs, upload, allowed, validate } = useDocuments()
const toast = useToast()
const MAX_ATTACH = 5

/** Status tiap lampiran diambil dari daftar dokumen (polling yang sama dengan halaman Memory). */
function statusOf(a: Staged): 'uploading' | 'processing' | 'ready' | 'failed' {
  if (!a.docId) return 'uploading'
  const d = docs.value.find(d => d.id === a.docId)
  return d?.status ?? 'ready'
}
function errorOf(a: Staged) { return docs.value.find(d => d.id === a.docId)?.error ?? null }

const uploading = computed(() => staged.value.some(a => !a.docId))
const hasFailed = computed(() => staged.value.some(a => statusOf(a) === 'failed'))
const processing = computed(() => staged.value.some(a => statusOf(a) === 'processing'))
const canSend = computed(() => text.value.trim().length > 0 && !props.busy && !uploading.value && !hasFailed.value)

function grow() {
  const el = area.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 200) + 'px'
}
function submit() {
  if (!canSend.value) return
  const atts: Attachment[] = staged.value.map(a => ({ document_id: a.docId!, name: a.name, ext: a.ext }))
  emit('send', text.value.trim(), atts)
  text.value = ''
  staged.value = []
  nextTick(grow)
}
function onKey(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); submit() }
}

async function addFiles(files: File[]) {
  for (const f of files) {
    if (staged.value.length >= MAX_ATTACH) { toast.error(`Maksimal ${MAX_ATTACH} lampiran per pesan.`); break }
    const key = uid()
    const name = f.name.replace(/\.[^.]+$/, '')
    const ext = '.' + (f.name.split('.').pop() ?? '').toLowerCase()
    const invalid = validate(f)
    if (invalid) { toast.error(invalid); continue }
    staged.value.push({ key, name, ext, size: f.size, docId: null })
    upload(f).then(doc => {
      const item = staged.value.find(a => a.key === key)
      if (!item) return
      if (doc) item.docId = doc.id
      else staged.value = staged.value.filter(a => a.key !== key)  // ditolak server (duplikat, dll.); toast sudah muncul
    })
  }
}
function onFiles(e: Event) {
  const input = e.target as HTMLInputElement
  addFiles(Array.from(input.files ?? []))
  input.value = ''
}
function onDrop(e: DragEvent) { over.value = false; addFiles(Array.from(e.dataTransfer?.files ?? [])) }
function remove(a: Staged) {
  staged.value = staged.value.filter(x => x.key !== a.key)
  toast.push('Lampiran dilepas dari pesan. Dokumennya tetap ada di Memory.')
}
onMounted(() => { if (props.autofocus) area.value?.focus() })
defineExpose({ focus: () => area.value?.focus() })
</script>

<template>
  <div class="mx-auto w-full max-w-3xl px-3 pb-3 sm:px-4 sm:pb-4">
    <form
      class="rounded-lg border bg-graphite p-2 transition-colors focus-within:border-smoke"
      :class="over ? 'border-soft-indigo' : 'border-slate-edge'"
      @submit.prevent="submit"
      @dragover.prevent="over = true" @dragleave="over = false" @drop.prevent="onDrop"
    >
      <div v-if="staged.length" class="flex gap-3 overflow-x-auto px-1 pb-3 pt-3" aria-label="Lampiran">
        <AttachmentTile
          v-for="a in staged" :key="a.key"
          :name="a.name" :ext="a.ext" :size="a.size" :status="statusOf(a)" :error="errorOf(a)"
          removable @remove="remove(a)"
        />
      </div>

      <textarea
        ref="area" v-model="text" rows="1" maxlength="4000"
        class="block max-h-[200px] min-h-10 w-full resize-none bg-transparent focus-visible:!outline-none px-2 py-2 text-base leading-6 outline-none placeholder:text-mist"
        :placeholder="staged.length ? 'Tanya sesuatu soal lampiranmu…' : 'Tanya sesuatu tentang dokumenmu…'"
        aria-label="Pertanyaan"
        @input="grow" @keydown="onKey"
      />
      <div class="flex items-center gap-1">
        <button type="button" class="btn-icon shrink-0" aria-label="Lampirkan dokumen" @click="file?.click()"><Icon name="attach" /></button>
        <input ref="file" type="file" multiple class="hidden" :accept="allowed.join(',')" @change="onFiles" />
        <span class="flex-1" />
        <ModelPicker :disabled="busy" />
        <button v-if="busy" type="button" class="btn-icon shrink-0 !bg-bone !text-carbon hover:!bg-bone/85" aria-label="Hentikan jawaban" @click="$emit('stop')"><Icon name="stop" :size="14" /></button>
        <button v-else type="submit" class="btn-icon shrink-0 !size-8" :class="canSend ? '!bg-bone !text-carbon' : ''" :disabled="!canSend" aria-label="Kirim"><Icon name="send" /></button>
      </div>
    </form>
    <p v-if="hasFailed" class="mt-2 px-1 text-xs text-ash" role="status">Ada lampiran yang gagal diproses. Lepas dulu (tombol ✕) sebelum mengirim.</p>
    <p v-else-if="processing" class="mt-2 px-1 text-xs text-ash" role="status">Lampiran masih diproses. Kamu bisa kirim sekarang, jawabannya menunggu sampai selesai.</p>
    <p v-else class="mt-2 hidden px-1 text-xs text-mist sm:block">Enter untuk kirim · Shift+Enter untuk baris baru. Jawaban AI bisa keliru, cek sumbernya ya.</p>
  </div>
</template>
