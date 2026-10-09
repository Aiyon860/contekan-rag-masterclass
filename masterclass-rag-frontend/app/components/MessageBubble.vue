<script setup lang="ts">
import type { Msg } from '~/types'
const props = defineProps<{ msg: Msg; canRegenerate?: boolean }>()
defineEmits<{ regenerate: [] }>()
const { open } = usePreview()
const copied = ref(false)
const html = computed(() => (props.msg.role === 'assistant' ? renderMarkdown(props.msg.content) : ''))
const waiting = computed(() => props.msg.status === 'streaming' && !props.msg.content)

async function copy() {
  try {
    await navigator.clipboard.writeText(props.msg.content)
    copied.value = true
    setTimeout(() => (copied.value = false), 1500)
  } catch {}
}
</script>

<template>
  <div v-if="msg.role === 'user'" class="rise flex flex-col items-end gap-2">
    <div v-if="msg.attachments?.length" class="flex max-w-[85%] flex-wrap justify-end gap-2">
      <AttachmentTile
        v-for="a in msg.attachments" :key="a.document_id"
        :name="a.name" :ext="a.ext" :deleted="a.deleted" clickable
        @open="open({ docId: a.document_id, name: a.name })"
      />
    </div>
    <p class="max-w-[85%] whitespace-pre-wrap rounded-lg border border-slate-edge bg-iron px-4 py-2.5 [overflow-wrap:anywhere]">{{ msg.content }}</p>
  </div>

  <div v-else class="rise">
    <div v-if="waiting" class="flex items-center gap-2 py-1 text-sm text-ash" role="status">
      <span class="size-1.5 rounded-full bg-soft-indigo pulse-dot" />
      <template v-if="msg.waitingFor?.length">Menunggu {{ msg.waitingFor.join(', ') }} selesai diproses…</template>
      <template v-else>{{ msg.retrieved ? 'Menyusun jawaban…' : 'Mencari di dokumen…' }}</template>
    </div>
    <div v-else class="md" :class="{ caret: msg.status === 'streaming' }" v-html="html" />

    <p v-if="msg.status === 'stopped'" class="mt-2 text-sm text-mist">Dihentikan sebelum selesai.</p>
    <p v-if="msg.status === 'error'" class="mt-2 flex items-center gap-1.5 text-sm text-ash"><Icon name="warn" :size="14" /> Jawabannya gagal dibuat. Coba kirim ulang.</p>

    <p v-if="msg.status !== 'streaming' && msg.grounded === false && msg.content" class="mt-3 inline-flex items-center gap-1.5 rounded-md border border-slate-edge px-2 py-1 text-xs text-ash">
      <Icon name="spark" :size="12" class="text-soft-indigo" /> Dari pengetahuan model, bukan dari dokumen
    </p>

    <div v-if="msg.sources.length" class="mt-3 flex flex-wrap gap-2">
      <button
        v-for="(s, i) in msg.sources" :key="i"
        class="inline-flex max-w-full items-center gap-1.5 rounded-lg border border-slate-edge bg-graphite px-2.5 py-1 text-xs text-ash transition-colors hover:border-smoke hover:text-bone disabled:cursor-default disabled:opacity-60"
        :disabled="s.deleted"
        :title="s.deleted ? 'Dokumen ini sudah dihapus dari memory' : 'Buka dokumen'"
        @click="open({ docId: s.document_id, name: s.document_name, chunk: s.text, page: s.page })"
      >
        <span class="font-mono tracking-normal text-soft-indigo">[{{ i + 1 }}]</span>
        <span class="truncate" :class="{ 'line-through': s.deleted }">{{ s.document_name }}</span>
        <span v-if="s.deleted" class="font-mono tracking-normal">dihapus</span>
      </button>
    </div>

    <template v-if="msg.status !== 'streaming' || msg.retrieved">
      <RagTrace v-if="msg.retrieved !== false && (msg.status !== 'streaming' || msg.sources.length || msg.augmented_prompt)" :msg="msg" />
    </template>

    <div v-if="msg.status !== 'streaming'" class="-ml-2 mt-2 flex items-center gap-0.5">
      <button class="btn-icon" :aria-label="copied ? 'Tersalin' : 'Salin jawaban'" @click="copy"><Icon :name="copied ? 'check' : 'copy'" :size="16" /></button>
      <button v-if="canRegenerate" class="btn-icon" aria-label="Buat ulang jawaban" @click="$emit('regenerate')"><Icon name="refresh" :size="16" /></button>
    </div>
  </div>
</template>
