<script setup lang="ts">
defineEmits<{ close: [] }>()
const { chats, rename, remove } = useChats()
const { docs } = useDocuments()
const route = useRoute()

const editing = ref<string | null>(null)
const draft = ref('')
const confirmId = ref<string | null>(null)

function startRename(id: string, title: string) { editing.value = id; draft.value = title; confirmId.value = null }
function commitRename() {
  if (editing.value) rename(editing.value, draft.value)
  editing.value = null
}
async function del(id: string) {
  if (confirmId.value !== id) { confirmId.value = id; return }
  confirmId.value = null
  const wasActive = route.params.id === id
  remove(id)
  if (wasActive) navigateTo('/')
}
const readyCount = computed(() => docs.value.filter(d => d.status === 'ready' && d.enabled).length)
</script>

<template>
  <div class="flex h-full min-h-0 flex-col">
    <div class="flex items-center justify-between px-4 pt-4 pb-3">
      <NuxtLink to="/" class="flex items-center gap-2 text-[17px] font-medium tracking-[-0.4px]">
        <span class="grid size-7 place-items-center rounded-lg border border-slate-edge bg-carbon text-soft-indigo"><Icon name="layers" :size="16" /></span>
        Contekan
      </NuxtLink>
      <button class="btn-icon md:hidden" aria-label="Tutup menu" @click="$emit('close')"><Icon name="x" /></button>
    </div>

    <div class="px-3 pb-3">
      <NuxtLink to="/" class="btn btn-primary w-full"><Icon name="plus" :size="16" /> Chat baru</NuxtLink>
    </div>

    <nav class="min-h-0 flex-1 overflow-y-auto px-2 pb-2" aria-label="Riwayat chat">
      <p v-if="chats.length" class="label-mono px-2 pb-1 pt-2">Riwayat</p>
      <p v-else class="px-3 py-6 text-sm leading-relaxed text-mist">Belum ada obrolan. Mulai tanya sesuatu, nanti riwayatnya muncul di sini.</p>

      <ul class="space-y-0.5">
        <li v-for="c in chats" :key="c.id" class="group relative">
          <form v-if="editing === c.id" class="px-1" @submit.prevent="commitRename">
            <input v-model="draft" class="input !py-1.5" autofocus maxlength="120" @blur="commitRename" @keydown.esc="editing = null" />
          </form>
          <template v-else>
            <NuxtLink
              :to="`/chat/${c.id}`"
              class="flex min-h-9 items-center rounded-lg py-1.5 pl-3 pr-16 text-sm transition-colors hover:bg-iron"
              :class="route.params.id === c.id ? 'bg-iron text-bone' : 'text-ash'"
            >
              <span class="truncate">{{ c.title }}</span>
            </NuxtLink>
            <div class="absolute right-1 top-1/2 flex -translate-y-1/2 items-center opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100 [@media(hover:none)]:opacity-100">
              <template v-if="confirmId === c.id">
                <button class="rounded-md bg-bone px-2 py-1 text-xs font-medium text-carbon" @click="del(c.id)" @blur="confirmId = null">Yakin hapus?</button>
              </template>
              <template v-else>
                <button class="btn-icon !size-7" aria-label="Ganti nama chat" @click="startRename(c.id, c.title)"><Icon name="pencil" :size="14" /></button>
                <button class="btn-icon !size-7" aria-label="Hapus chat" @click="del(c.id)"><Icon name="trash" :size="14" /></button>
              </template>
            </div>
          </template>
        </li>
      </ul>
    </nav>

    <div class="space-y-1 border-t border-iron p-2">
      <NuxtLink to="/memory" class="pill">
        <Icon name="database" /> Memory
        <span v-if="readyCount" class="tag ml-auto tabular">{{ readyCount }}</span>
      </NuxtLink>
      <NuxtLink to="/settings" class="pill"><Icon name="settings" /> Pengaturan</NuxtLink>
    </div>
  </div>
</template>
