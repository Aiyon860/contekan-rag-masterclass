<script setup lang="ts">
const props = withDefaults(defineProps<{
  name: string
  ext: string
  size?: number
  status?: 'uploading' | 'processing' | 'ready' | 'failed'
  error?: string | null
  removable?: boolean
  deleted?: boolean
  clickable?: boolean
}>(), { status: 'ready' })
defineEmits<{ remove: []; open: [] }>()

/** Potong di tengah supaya akhiran (tanggal/versi) tetap terlihat: crm-leads-…121126 */
const label = computed(() => {
  const n = props.name
  return n.length > 26 ? `${n.slice(0, 14)}…${n.slice(-8)}` : n
})
const icon = computed(() => {
  if (props.ext === '.pdf') return 'pdf'
  if (['.xlsx', '.csv'].includes(props.ext)) return 'sheet'
  return 'file'
})
const meta = computed(() => {
  if (props.deleted) return 'dihapus'
  if (props.status === 'uploading') return 'mengunggah…'
  if (props.status === 'processing') return 'memproses…'
  if (props.status === 'failed') return 'gagal'
  return [props.ext.replace('.', ''), props.size ? formatBytes(props.size) : null].filter(Boolean).join(' · ')
})
const interactive = computed(() => props.clickable && !props.deleted && props.status === 'ready')
</script>

<template>
  <div
    class="group relative flex w-[220px] max-w-full shrink-0 items-center gap-3 rounded-lg border bg-iron p-2 pr-3 text-left transition-colors"
    :class="[
      status === 'failed' ? 'border-bone/50' : 'border-slate-edge',
      interactive ? 'cursor-pointer hover:border-smoke' : '',
      deleted ? 'opacity-60' : '',
    ]"
    :title="error || name"
    @click="interactive && $emit('open')"
  >
    <span class="grid size-10 shrink-0 place-items-center rounded-md border border-slate-edge bg-carbon" :class="status === 'failed' ? 'text-bone' : 'text-soft-indigo'">
      <Icon v-if="status === 'uploading' || status === 'processing'" name="loader" :size="18" class="spin" />
      <Icon v-else-if="status === 'failed'" name="warn" :size="18" />
      <Icon v-else :name="icon" :size="18" />
    </span>
    <span class="min-w-0 flex-1">
      <span class="block truncate text-sm font-medium leading-tight" :class="{ 'line-through': deleted }">{{ label }}</span>
      <span class="mt-0.5 block truncate font-mono text-[12px] leading-tight tracking-normal text-ash tabular">{{ meta }}</span>
    </span>
    <button
      v-if="removable"
      type="button"
      class="absolute -right-2 -top-2 grid size-5 place-items-center rounded-full border border-slate-edge bg-graphite text-ash transition-colors hover:bg-bone hover:text-carbon"
      aria-label="Lepas lampiran"
      @click.stop="$emit('remove')"
    ><Icon name="x" :size="12" /></button>
  </div>
</template>
