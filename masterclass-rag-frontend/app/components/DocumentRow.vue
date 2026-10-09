<script setup lang="ts">
import type { DocItem } from '~/types'
const props = defineProps<{ doc: DocItem }>()
const { toggle, remove } = useDocuments()
const { open } = usePreview()
const confirming = ref(false)

const icon = computed(() => {
  if (props.doc.ext === '.pdf') return 'pdf'
  if (['.xlsx', '.csv'].includes(props.doc.ext)) return 'sheet'
  return 'file'
})
function del() {
  if (!confirming.value) { confirming.value = true; return }
  remove(props.doc)
}
</script>

<template>
  <li class="flex flex-wrap items-center gap-x-4 gap-y-2 border-b border-iron px-4 py-3 last:border-b-0 sm:flex-nowrap" :class="{ 'opacity-60': !doc.enabled && doc.status === 'ready' }">
    <Icon :name="icon" :size="20" class="shrink-0 text-ash" />

    <div class="min-w-0 flex-1 basis-[55%] sm:basis-auto">
      <p class="truncate font-medium">{{ doc.name }}</p>
      <p class="mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-ash">
        <span class="tag">{{ doc.ext }}</span>
        <span class="tabular">{{ formatBytes(doc.size_bytes) }}</span>
        <span v-if="doc.status === 'ready'" class="tabular">· {{ doc.chunk_count }} potongan</span>
        <span v-else-if="doc.status === 'processing'" class="inline-flex items-center gap-1.5 text-soft-indigo"><Icon name="loader" :size="14" class="spin" /> Memproses…</span>
        <span v-else class="inline-flex items-center gap-1.5 text-bone"><Icon name="warn" :size="14" /> Gagal</span>
      </p>
      <p v-if="doc.status === 'failed' && doc.error" class="mt-1 text-sm text-ash">{{ doc.error }}</p>
    </div>

    <div class="ml-auto flex items-center gap-1">
      <button
        v-if="doc.status === 'ready'" role="switch" :aria-checked="doc.enabled"
        :aria-label="doc.enabled ? 'Nonaktifkan dokumen' : 'Aktifkan dokumen'"
        class="relative mr-2 h-5 w-9 rounded-full border transition-colors"
        :class="doc.enabled ? 'border-soft-indigo bg-soft-indigo/20' : 'border-smoke bg-iron'"
        @click="toggle(doc)"
      >
        <span class="absolute top-0.5 size-3.5 rounded-full transition-all duration-200" :class="doc.enabled ? 'left-[18px] bg-soft-indigo' : 'left-0.5 bg-mist'" />
      </button>
      <button class="btn-icon" aria-label="Lihat isi dokumen" :disabled="doc.status !== 'ready' || doc.pending" @click="open({ docId: doc.id, name: doc.name })"><Icon name="eye" /></button>
      <button v-if="confirming" class="rounded-md bg-bone px-2.5 py-1.5 text-xs font-medium text-carbon" @click="del" @blur="confirming = false" autofocus>Yakin hapus?</button>
      <button v-else class="btn-icon" aria-label="Hapus dokumen" :disabled="doc.pending" @click="del"><Icon name="trash" /></button>
    </div>
  </li>
</template>
