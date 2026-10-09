<script setup lang="ts">
const { upload, allowed } = useDocuments()
const { settings } = useSettings()
const input = ref<HTMLInputElement>()
const over = ref(false)

function handle(files: FileList | null) {
  if (!files) return
  Array.from(files).forEach(upload)
}
function onDrop(e: DragEvent) { over.value = false; handle(e.dataTransfer?.files ?? null) }
</script>

<template>
  <div
    class="rounded-lg border border-dashed p-6 text-center transition-colors"
    :class="over ? 'border-soft-indigo bg-iron' : 'border-smoke bg-graphite hover:border-mist'"
    @dragover.prevent="over = true" @dragleave="over = false" @drop.prevent="onDrop"
  >
    <Icon name="upload" :size="22" class="mx-auto text-soft-indigo" />
    <p class="mt-3 font-medium">Tarik file ke sini, atau pilih manual</p>
    <p class="mt-1 text-sm text-ash">
      <span class="font-mono tracking-normal">{{ allowed.join('  ') }}</span> · maks {{ settings?.max_file_size_mb ?? 10 }} MB per file
    </p>
    <button class="btn btn-ghost mt-4" @click="input?.click()">Pilih file</button>
    <input ref="input" type="file" multiple class="hidden" :accept="allowed.join(',')" @change="handle(($event.target as HTMLInputElement).files); ($event.target as HTMLInputElement).value = ''" />
  </div>
</template>
