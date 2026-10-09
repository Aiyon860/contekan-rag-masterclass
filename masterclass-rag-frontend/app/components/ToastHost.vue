<script setup lang="ts">
const { toasts, dismiss } = useToast()
</script>

<template>
  <div class="pointer-events-none fixed inset-x-0 bottom-4 z-[70] flex flex-col items-center gap-2 px-4" aria-live="polite">
    <TransitionGroup name="toast">
      <div
        v-for="t in toasts" :key="t.id"
        class="pointer-events-auto flex max-w-md items-start gap-3 rounded-lg border bg-graphite px-4 py-3 text-sm"
        :class="t.kind === 'error' ? 'border-bone/60' : 'border-slate-edge'"
        role="status"
      >
        <Icon :name="t.kind === 'error' ? 'warn' : 'check'" :size="16" class="mt-0.5 shrink-0 text-soft-indigo" />
        <span class="min-w-0 flex-1">{{ t.text }}</span>
        <button class="text-mist hover:text-bone" aria-label="Tutup" @click="dismiss(t.id)"><Icon name="x" :size="14" /></button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active { transition: all .35s var(--ease-out-expo); }
.toast-leave-active { transition: all .2s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(8px); }
</style>
