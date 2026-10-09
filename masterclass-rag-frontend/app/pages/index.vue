<script setup lang="ts">
import type { Attachment } from '~/types'
const { docs } = useDocuments()
const chats = useChats()
const pending = useState<{ id: string; text: string; attachments: Attachment[] } | null>('pending-message', () => null)

const { name } = useProfileName()
const greeting = ref(greetingFor())
onMounted(() => { greeting.value = greetingFor() })

const ready = computed(() => docs.value.filter(d => d.status === 'ready' && d.enabled))
const suggestions = [
  'Ringkas isi dokumen yang barusan aku upload.',
  'Apa poin terpenting dari dokumen ini?',
  'Cari bagian yang membahas ... dan jelaskan singkat.',
]

function start(text: string, attachments: Attachment[] = []) {
  const id = uid()
  chats.addLocal(id, text.slice(0, 50))
  pending.value = { id, text, attachments }
  navigateTo(`/chat/${id}`)
}
</script>

<template>
  <div class="blueprint backdrop-glow flex h-full flex-col">
    <div class="flex min-h-0 flex-1 flex-col items-center justify-center overflow-y-auto px-4 py-10">
      <div class="rise w-full max-w-2xl">
        <h1 class="flex items-center gap-3 text-balance text-[30px] font-medium leading-[1.15] tracking-[-0.84px] sm:gap-4 sm:text-[40px]">
          <SparkMark :size="40" class="size-8 sm:size-10" />
          <span>{{ greeting }}<template v-if="name">, {{ name }}</template></span>
        </h1>
        <p class="mt-4 max-w-[52ch] text-ash">
          Mau tanya apa hari ini? Contekan bakal buka dokumenmu dulu sebelum menjawab, jadi jawabannya nyambung dan bukan asal tebak.
        </p>

        <div v-if="!ready.length" class="mt-6 flex flex-wrap items-center gap-3 rounded-lg border border-slate-edge bg-graphite p-4">
          <Icon name="database" class="text-soft-indigo" />
          <p class="min-w-0 flex-1 basis-56 text-sm text-ash">Memory masih kosong. Tambahkan dokumen dulu supaya AI punya bahan buat dijawab.</p>
          <NuxtLink to="/memory" class="btn btn-ghost">Tambah dokumen</NuxtLink>
        </div>
        <p v-else class="mt-6 text-sm text-ash"><span class="tabular text-bone">{{ ready.length }}</span> dokumen aktif di memory siap dipakai.</p>

        <ul class="mt-6 flex flex-wrap gap-2">
          <li v-for="s in suggestions" :key="s">
            <button class="rounded-lg border border-slate-edge px-3 py-1.5 text-left text-sm text-ash transition-colors hover:border-smoke hover:bg-iron hover:text-bone" @click="start(s)">{{ s }}</button>
          </li>
        </ul>
      </div>
    </div>
    <ChatComposer :busy="false" autofocus @send="start" />
  </div>
</template>
