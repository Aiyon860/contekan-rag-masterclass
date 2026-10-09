<script setup lang="ts">
const { settings, models, save } = useSettings()
const form = reactive({ top_k: 3, similarity_threshold: 0.6, max_file_size_mb: 10, chat_model: 'gemma3:1b', system_prompt: '' })
const saving = ref(false)
const { name: profileName, save: saveName, DEFAULT_NAME } = useProfileName()
const nameDraft = ref(profileName.value)
watch(profileName, v => { nameDraft.value = v })

watch(settings, (s) => { if (s) Object.assign(form, { top_k: s.top_k, similarity_threshold: s.similarity_threshold, max_file_size_mb: s.max_file_size_mb, chat_model: s.chat_model, system_prompt: s.system_prompt }) }, { immediate: true })

const serverDirty = computed(() => !!settings.value && (
  form.top_k !== settings.value.top_k || form.similarity_threshold !== settings.value.similarity_threshold || form.max_file_size_mb !== settings.value.max_file_size_mb ||
  form.chat_model !== settings.value.chat_model || form.system_prompt !== settings.value.system_prompt))
const nameDirty = computed(() => nameDraft.value.trim() !== profileName.value)
const dirty = computed(() => serverDirty.value || nameDirty.value)
const modelOptions = computed(() => Array.from(new Set([form.chat_model, ...models.value])))

async function submit() {
  saving.value = true
  const hadServerChanges = serverDirty.value  // setelah save() nilainya sudah ikut berubah
  let ok = true
  if (hadServerChanges) ok = await save({ ...form })
  if (ok && nameDirty.value) {
    saveName(nameDraft.value)
    if (!hadServerChanges) useToast().push('Pengaturan tersimpan.')  // save() sudah menampilkan toast sendiri
  }
  saving.value = false
}
</script>

<template>
  <div class="blueprint h-full overflow-y-auto">
    <form class="mx-auto w-full max-w-3xl px-4 py-8 sm:py-12" @submit.prevent="submit">
      <h1 class="text-[28px] font-medium leading-tight tracking-[-0.7px] sm:text-[32px]">Pengaturan</h1>
      <p class="mt-2 text-ash">Atur cara Contekan mencari dan menjawab. Perubahan berlaku mulai pertanyaan berikutnya.</p>

      <div v-if="!settings" class="mt-8 h-64 animate-pulse rounded-lg bg-graphite" />
      <div v-else class="mt-8 divide-y divide-iron overflow-hidden rounded-lg border border-iron bg-graphite">
        <div class="grid gap-3 p-5 sm:grid-cols-[1fr_200px] sm:items-center">
          <div>
            <label class="font-medium" for="nama">Namamu</label>
            <p class="mt-1 text-sm text-ash">Dipakai untuk sapaan di halaman chat baru. Disimpan di browser ini saja, dan boleh dikosongkan.</p>
          </div>
          <input id="nama" v-model="nameDraft" class="input" maxlength="40" :placeholder="DEFAULT_NAME" />
        </div>

        <div class="grid gap-3 p-5 sm:grid-cols-[1fr_200px] sm:items-center">
          <div>
            <label class="font-medium" for="topk">Top-K</label>
            <p class="mt-1 text-sm text-ash">Berapa potongan dokumen paling relevan yang dikirim ke AI tiap pertanyaan.</p>
          </div>
          <div class="flex items-center gap-3">
            <input id="topk" v-model.number="form.top_k" type="range" min="1" max="10" class="h-1 w-full cursor-pointer appearance-none rounded-full bg-slate-edge accent-[#6798ff]" />
            <output class="w-6 text-right font-mono tabular">{{ form.top_k }}</output>
          </div>
        </div>

        <div class="grid gap-3 p-5 sm:grid-cols-[1fr_200px] sm:items-center">
          <div>
            <label class="font-medium" for="thr">Ambang kemiripan</label>
            <p class="mt-1 text-sm text-ash">Potongan dengan skor di bawah ini dibuang. Kalau terlalu rendah, AI gampang menjawab hal yang nggak ada di dokumen. Kalau terlalu tinggi, pertanyaan yang sebenarnya relevan ikut ditolak.</p>
          </div>
          <div class="flex items-center gap-3">
            <input id="thr" v-model.number="form.similarity_threshold" type="range" min="0.3" max="0.9" step="0.01" class="h-1 w-full cursor-pointer appearance-none rounded-full bg-slate-edge accent-[#6798ff]" />
            <output class="w-10 text-right font-mono tabular">{{ Number(form.similarity_threshold ?? 0.6).toFixed(2) }}</output>
          </div>
        </div>

        <div class="grid gap-3 p-5 sm:grid-cols-[1fr_200px] sm:items-center">
          <div>
            <label class="font-medium" for="maxsize">Batas ukuran file</label>
            <p class="mt-1 text-sm text-ash">File yang lebih besar dari ini ditolak saat upload.</p>
          </div>
          <div class="flex items-center gap-2">
            <input id="maxsize" v-model.number="form.max_file_size_mb" type="number" min="1" max="100" class="input tabular" />
            <span class="text-sm text-ash">MB</span>
          </div>
        </div>

        <div class="grid gap-3 p-5 sm:grid-cols-[1fr_200px] sm:items-center">
          <div>
            <label class="font-medium" for="model">Model chat</label>
            <p class="mt-1 text-sm text-ash">Diambil dari Ollama di komputermu. Model embedding dikunci ke <span class="font-mono tracking-normal">nomic-embed-text</span> biar vektornya konsisten.</p>
          </div>
          <select id="model" v-model="form.chat_model" class="input font-mono tracking-normal">
            <option v-for="m in modelOptions" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>

        <div class="p-5">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <label class="font-medium" for="sys">System prompt</label>
            <button type="button" class="text-sm text-ash underline underline-offset-4 decoration-smoke hover:text-soft-indigo" @click="form.system_prompt = settings.default_system_prompt">Kembalikan ke bawaan</button>
          </div>
          <p class="mt-1 text-sm text-ash">Instruksi dasar yang selalu dikirim ke AI sebelum konteks dan pertanyaan.</p>
          <textarea id="sys" v-model="form.system_prompt" class="input mt-3 min-h-36 resize-y leading-relaxed" maxlength="4000" />
        </div>
      </div>

      <div v-if="settings" class="sticky bottom-0 -mx-4 mt-6 flex items-center gap-3 border-t border-iron bg-carbon/95 px-4 py-3 backdrop-blur-sm">
        <button class="btn btn-primary" :disabled="!dirty || saving"><Icon v-if="saving" name="loader" :size="16" class="spin" /> Simpan</button>
        <span v-if="dirty" class="text-sm text-ash">Ada perubahan yang belum disimpan.</span>
      </div>
    </form>
  </div>
</template>
