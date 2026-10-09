<script setup lang="ts">
const props = withDefaults(defineProps<{
  open: boolean
  title: string
  message?: string
  confirmLabel?: string
  cancelLabel?: string
}>(), { confirmLabel: 'Hapus', cancelLabel: 'Batal' })
const emit = defineEmits<{ confirm: []; cancel: [] }>()

const cancelBtn = ref<HTMLButtonElement>()
const panel = ref<HTMLElement>()
let lastFocus: HTMLElement | null = null

watch(() => props.open, async (v) => {
  if (v) {
    lastFocus = document.activeElement as HTMLElement | null
    await nextTick()
    cancelBtn.value?.focus()  // fokus awal di tombol aman (Batal) supaya Enter tidak langsung menghapus
  } else {
    lastFocus?.focus?.()
  }
})

function onKey(e: KeyboardEvent) {
  if (!props.open) return
  if (e.key === 'Escape') { e.stopPropagation(); emit('cancel'); return }
  if (e.key === 'Tab' && panel.value) {  // jebak fokus di dalam dialog
    const items = Array.from(panel.value.querySelectorAll<HTMLElement>('button:not([disabled])'))
    if (!items.length) return
    const first = items[0], last = items[items.length - 1]
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus() }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus() }
  }
}
onMounted(() => document.addEventListener('keydown', onKey, true))
onBeforeUnmount(() => document.removeEventListener('keydown', onKey, true))
</script>

<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="open" class="fixed inset-0 z-[60] grid place-items-center p-4">
        <div class="absolute inset-0 bg-pure-black/70 backdrop-blur-[2px]" aria-hidden="true" @click="emit('cancel')" />
        <div
          ref="panel" role="alertdialog" aria-modal="true" aria-labelledby="dlg-title" :aria-describedby="message ? 'dlg-msg' : undefined"
          class="dialog-panel relative w-full max-w-sm rounded-lg border border-slate-edge bg-graphite p-6"
        >
          <h2 id="dlg-title" class="text-[20px] font-medium leading-snug tracking-[-0.42px]">{{ title }}</h2>
          <p v-if="message" id="dlg-msg" class="mt-2 text-sm leading-relaxed text-ash [overflow-wrap:anywhere]">{{ message }}</p>
          <div class="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <button ref="cancelBtn" type="button" class="btn btn-ghost" @click="emit('cancel')">{{ cancelLabel }}</button>
            <button type="button" class="btn btn-primary" @click="emit('confirm')">{{ confirmLabel }}</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.dialog-enter-active, .dialog-leave-active { transition: opacity .22s ease; }
.dialog-enter-active .dialog-panel { transition: transform .35s var(--ease-out-expo), opacity .22s ease; }
.dialog-leave-active .dialog-panel { transition: transform .15s ease, opacity .15s ease; }
.dialog-enter-from, .dialog-leave-to { opacity: 0; }
.dialog-enter-from .dialog-panel { transform: translateY(8px) scale(.97); opacity: 0; }
.dialog-leave-to .dialog-panel { transform: scale(.98); opacity: 0; }
</style>
