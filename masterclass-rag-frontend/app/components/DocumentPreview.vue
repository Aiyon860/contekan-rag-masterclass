<script setup lang="ts">
import type { PreviewData } from '~/types'
const { target, close } = usePreview()
const { api, url } = useApi()
const toast = useToast()

const data = ref<PreviewData | null>(null)
const loading = ref(false)
const sheet = ref(0)

watch(() => target.value?.docId, async (id) => {
  if (!id) return
  data.value = null; sheet.value = 0; loading.value = true
  try { data.value = await api<PreviewData>(`/documents/${id}/preview`) }
  catch (e: any) { toast.error(e.message); close() }
  finally { loading.value = false }
}, { immediate: true })

const pdfSrc = computed(() => data.value?.kind === 'pdf'
  ? `${url(`/documents/${data.value.id}/file`).replace(/^\/api/, '/api')}#page=${target.value?.page ?? 1}` : '')

/** Sisipkan <mark> di teks mentah bila potongan yang dipakai AI ketemu. */
const parts = computed(() => {
  const text = data.value?.text ?? ''
  const chunk = target.value?.chunk
  if (!text || !chunk) return { before: text, hit: '', after: '' }
  const needle = chunk.replace(/\s+/g, ' ').trim().slice(0, 60)
  const flat = text.replace(/\s+/g, ' ')
  const flatIdx = flat.indexOf(needle)
  if (flatIdx < 0) return { before: text, hit: '', after: '' }
  // petakan indeks teks yang sudah dipadatkan kembali ke teks asli
  let orig = 0, f = 0
  while (f < flatIdx && orig < text.length) {
    if (/\s/.test(text[orig]) && /\s/.test(text[orig + 1] ?? '')) { orig++; continue }
    orig++; f++
  }
  const end = Math.min(text.length, orig + chunk.length)
  return { before: text.slice(0, orig), hit: text.slice(orig, end), after: text.slice(end) }
})
const hitEl = ref<HTMLElement>()
watch(parts, () => nextTick(() => hitEl.value?.scrollIntoView({ block: 'center' })), { flush: 'post' })
</script>

<template>
  <div class="contents">
    <div class="fixed inset-0 z-40 bg-pure-black/60 lg:hidden" @click="close" />
    <aside
      class="fixed inset-y-0 right-0 z-50 flex w-full flex-col border-l border-iron bg-carbon sm:w-[520px] lg:static lg:z-auto lg:w-[460px] lg:shrink-0 xl:w-[520px]"
      aria-label="Isi dokumen"
    >
      <header class="flex h-12 shrink-0 items-center gap-2 border-b border-iron px-4">
        <Icon name="file" :size="16" class="text-ash" />
        <h2 class="min-w-0 flex-1 truncate text-sm font-medium">{{ target?.name }}</h2>
        <button class="btn-icon" aria-label="Tutup panel" @click="close"><Icon name="x" /></button>
      </header>

      <div class="min-h-0 flex-1 overflow-auto">
        <div v-if="loading" class="grid h-full place-items-center text-ash"><Icon name="loader" class="spin" /></div>

        <template v-else-if="data">
          <div v-if="target?.chunk" class="m-4 rounded-lg border border-slate-edge bg-graphite p-3">
            <p class="label-mono">Potongan yang dipakai AI</p>
            <p class="mt-2 max-h-40 overflow-auto whitespace-pre-wrap text-sm leading-relaxed text-ash">{{ target.chunk }}</p>
          </div>

          <iframe v-if="data.kind === 'pdf'" :src="pdfSrc" class="h-[calc(100%-1px)] min-h-[60vh] w-full border-0 bg-graphite" title="Pratinjau PDF" />

          <article v-else-if="data.kind === 'markdown'" class="md px-4 pb-8" v-html="renderMarkdown(data.text ?? '')" />

          <pre v-else-if="data.kind === 'text'" class="whitespace-pre-wrap px-4 pb-8 text-sm leading-relaxed tracking-normal text-ash [overflow-wrap:anywhere]">{{ parts.before }}<mark v-if="parts.hit" ref="hitEl" class="rounded-sm bg-soft-indigo/25 text-bone">{{ parts.hit }}</mark>{{ parts.after }}</pre>

          <div v-else-if="data.kind === 'table'" class="pb-8">
            <div v-if="(data.sheets?.length ?? 0) > 1" class="flex gap-1 overflow-x-auto px-4 pb-3">
              <button v-for="(s, i) in data.sheets" :key="i" class="pill !py-1 whitespace-nowrap" :class="{ 'bg-iron !text-bone': sheet === i }" @click="sheet = i">{{ s.name }}</button>
            </div>
            <div class="overflow-x-auto px-4">
              <table class="w-full border-collapse text-sm tabular">
                <thead>
                  <tr><th v-for="(h, i) in data.sheets?.[sheet]?.rows[0]" :key="i" class="whitespace-nowrap border border-iron bg-graphite px-3 py-2 text-left font-medium">{{ h }}</th></tr>
                </thead>
                <tbody>
                  <tr v-for="(r, ri) in data.sheets?.[sheet]?.rows.slice(1)" :key="ri">
                    <td v-for="(c, ci) in r" :key="ci" class="border border-iron px-3 py-1.5 text-ash">{{ c }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p class="px-4 pt-3 text-xs text-mist">Menampilkan maksimal 200 baris pertama.</p>
          </div>
        </template>
      </div>
    </aside>
  </div>
</template>
