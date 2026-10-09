<script setup lang="ts">
const { docs, loaded, addText } = useDocuments()
const showText = ref(false)
const title = ref('')
const content = ref('')
const saving = ref(false)

const active = computed(() => docs.value.filter(d => d.status === 'ready' && d.enabled).length)

async function submitText() {
  if (!title.value.trim() || !content.value.trim()) return
  saving.value = true
  const ok = await addText(title.value.trim(), content.value.trim())
  saving.value = false
  if (ok) { title.value = ''; content.value = ''; showText.value = false }
}
</script>

<template>
  <div class="blueprint h-full overflow-y-auto">
    <div class="mx-auto w-full max-w-3xl px-4 py-8 sm:py-12">
      <h1 class="text-[28px] font-medium leading-tight tracking-[-0.7px] sm:text-[32px]">Memory</h1>
      <p class="mt-2 max-w-[56ch] text-ash">
        Dokumen di sini jadi contekan AI di semua chat, dan tetap tersimpan walau kamu bikin chat baru.
        <span v-if="docs.length" class="tabular">{{ active }} dari {{ docs.length }} dokumen aktif.</span>
      </p>

      <div class="mt-6 space-y-3">
        <UploadDropzone />
        <button v-if="!showText" class="btn btn-ghost w-full sm:w-auto" @click="showText = true"><Icon name="pencil" :size="16" /> Tempel teks langsung</button>
        <form v-else class="rise space-y-3 rounded-lg border border-slate-edge bg-graphite p-4" @submit.prevent="submitText">
          <label class="block text-sm font-medium" for="t-title">Judul</label>
          <input id="t-title" v-model="title" class="input" maxlength="120" placeholder="Misalnya: Catatan rapat Senin" />
          <label class="block text-sm font-medium" for="t-body">Isi teks</label>
          <textarea id="t-body" v-model="content" class="input min-h-40 resize-y" placeholder="Tempel teksnya di sini…" />
          <div class="flex gap-2">
            <button class="btn btn-primary" :disabled="saving || !title.trim() || !content.trim()"><Icon v-if="saving" name="loader" :size="16" class="spin" /> Simpan ke memory</button>
            <button type="button" class="btn btn-ghost" @click="showText = false">Batal</button>
          </div>
        </form>
      </div>

      <section class="mt-8" aria-label="Daftar dokumen">
        <div v-if="!loaded" class="space-y-px overflow-hidden rounded-lg border border-iron">
          <div v-for="n in 3" :key="n" class="h-[68px] animate-pulse bg-graphite" />
        </div>
        <div v-else-if="!docs.length" class="rounded-lg border border-iron bg-graphite p-8 text-center">
          <Icon name="database" :size="22" class="mx-auto text-mist" />
          <p class="mt-3 font-medium">Belum ada dokumen</p>
          <p class="mt-1 text-sm text-ash">Upload file atau tempel teks di atas, nanti muncul di sini lengkap dengan statusnya.</p>
        </div>
        <ul v-else class="overflow-hidden rounded-lg border border-iron bg-graphite">
          <DocumentRow v-for="d in docs" :key="d.id" :doc="d" />
        </ul>
      </section>
    </div>
  </div>
</template>
