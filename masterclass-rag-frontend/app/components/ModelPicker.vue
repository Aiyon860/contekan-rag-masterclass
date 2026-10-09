<script setup lang="ts">
const props = defineProps<{ disabled?: boolean }>()
const { settings, models, save } = useSettings()
const open = ref(false)
const root = ref<HTMLElement>()

const current = computed(() => settings.value?.chat_model ?? '')
const options = computed(() => Array.from(new Set([current.value, ...models.value].filter(Boolean))))

async function pick(m: string) {
  open.value = false
  if (!settings.value || m === current.value) return
  const { default_system_prompt, ...rest } = settings.value
  await save({ ...rest, chat_model: m })
}
function onDoc(e: MouseEvent) { if (open.value && !root.value?.contains(e.target as Node)) open.value = false }
function onKey(e: KeyboardEvent) { if (e.key === 'Escape') open.value = false }
onMounted(() => { document.addEventListener('mousedown', onDoc); document.addEventListener('keydown', onKey) })
onBeforeUnmount(() => { document.removeEventListener('mousedown', onDoc); document.removeEventListener('keydown', onKey) })
</script>

<template>
  <div v-if="current" ref="root" class="relative">
    <button
      type="button"
      class="inline-flex h-8 max-w-[150px] items-center gap-1.5 rounded-lg px-2 text-ash transition-colors hover:bg-iron hover:text-bone disabled:cursor-not-allowed disabled:opacity-50 sm:max-w-[220px]"
      :aria-expanded="open" aria-haspopup="listbox" :disabled="props.disabled"
      title="Model yang sedang dipakai"
      @click="open = !open"
    >
      <span class="size-1.5 shrink-0 rounded-full bg-soft-indigo" />
      <span class="truncate font-mono text-[12px] tracking-normal">{{ current }}</span>
      <Icon name="down" :size="14" class="shrink-0" />
    </button>

    <div v-if="open" class="rise absolute bottom-full right-0 z-30 mb-2 w-64 max-w-[80vw] overflow-hidden rounded-lg border border-slate-edge bg-graphite" role="listbox" aria-label="Pilih model chat">
      <p class="label-mono px-3 pb-1 pt-3">Model chat</p>
      <ul class="max-h-56 overflow-y-auto p-1">
        <li v-for="m in options" :key="m">
          <button
            type="button" role="option" :aria-selected="m === current"
            class="flex w-full items-center gap-2 rounded-md px-2 py-2 text-left transition-colors hover:bg-iron"
            :class="m === current ? 'text-bone' : 'text-ash'"
            @click="pick(m)"
          >
            <span class="min-w-0 flex-1 truncate font-mono text-[13px] tracking-normal">{{ m }}</span>
            <Icon v-if="m === current" name="check" :size="14" class="shrink-0 text-soft-indigo" />
          </button>
        </li>
      </ul>
      <p class="border-t border-iron px-3 py-2 text-xs leading-relaxed text-mist">
        Embedding tetap <span class="font-mono tracking-normal">nomic-embed-text</span> supaya pencarian dokumen konsisten.
      </p>
    </div>
  </div>
</template>
