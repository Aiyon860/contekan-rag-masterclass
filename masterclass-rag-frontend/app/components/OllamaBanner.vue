<script setup lang="ts">
const { health } = useHealth()
const msg = computed(() => {
  const h = health.value
  if (!h) return null
  if (h.error === 'backend') return { t: 'Backend belum nyambung.', d: 'Pastikan FastAPI jalan di port 8000.' }
  if (!h.ollama) return { t: 'Ollama belum nyala.', d: 'Jalankan Ollama dulu, baru chat bisa dipakai.' }
  if (h.missing_models.length) return { t: `Model ${h.missing_models.join(', ')} belum ada.`, d: `Jalankan: ollama pull ${h.missing_models[0]}` }
  return null
})
</script>

<template>
  <div v-if="msg" role="status" class="flex shrink-0 items-start gap-2 border-b border-slate-edge bg-iron px-4 py-2 text-sm">
    <Icon name="warn" :size="16" class="mt-0.5 shrink-0 text-soft-indigo" />
    <p class="min-w-0"><span class="font-medium">{{ msg.t }}</span> <span class="text-ash">{{ msg.d }}</span></p>
  </div>
</template>
