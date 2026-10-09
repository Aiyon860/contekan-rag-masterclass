<script setup lang="ts">
import type { Msg } from '~/types'
const props = defineProps<{ msg: Msg }>()
const { open } = usePreview()
const { settings } = useSettings()
const openState = ref(false)
const empty = computed(() => props.msg.retrieved !== false && props.msg.sources.length === 0)
</script>

<template>
  <div class="mt-3">
    <button
      class="inline-flex items-center gap-1.5 rounded-md py-1 text-sm text-ash transition-colors hover:text-bone"
      :aria-expanded="openState" @click="openState = !openState"
    >
      <Icon :name="openState ? 'down' : 'right'" :size="14" /> Lihat proses RAG
    </button>

    <div v-if="openState" class="rise mt-2 overflow-hidden rounded-lg border border-iron bg-graphite">
      <!-- 1 Retrieval -->
      <section class="border-b border-iron p-4">
        <h4 class="flex items-center gap-2 text-sm font-medium"><Icon name="search" :size="16" class="text-soft-indigo" /> Retrieval <span class="tag">top-{{ settings?.top_k ?? 3 }}</span></h4>
        <p v-if="empty" class="mt-2 text-sm text-ash">Nggak ada potongan dokumen yang cukup mirip dengan pertanyaan ini, jadi AI menjawab dari pengetahuan umumnya.</p>
        <p v-if="msg.sources.some(s => s.reused)" class="mt-2 text-sm text-ash">Pertanyaan ini berupa lanjutan, jadi potongan dari jawaban sebelumnya dipakai ulang.</p>
        <ul v-if="!empty" class="mt-3 space-y-2">
          <li v-for="(s, i) in msg.sources" :key="i">
            <button
              class="w-full rounded-lg border border-iron bg-carbon p-3 text-left transition-colors hover:border-slate-edge disabled:cursor-default"
              :disabled="s.deleted"
              @click="open({ docId: s.document_id, name: s.document_name, chunk: s.text, page: s.page })"
            >
              <span class="flex items-center gap-2 text-xs">
                <span class="tag !text-bone">[{{ i + 1 }}]</span>
                <span class="min-w-0 truncate text-ash">{{ s.document_name }}<template v-if="s.page"> · hlm. {{ s.page }}</template></span>
                <span v-if="s.deleted" class="tag ml-auto">dihapus</span>
                <span v-else class="ml-auto font-mono tabular text-soft-indigo">{{ s.score.toFixed(2) }}</span>
              </span>
              <span class="mt-2 block h-0.5 overflow-hidden rounded-full bg-iron"><span class="block h-full bg-soft-indigo" :style="{ width: Math.max(0, Math.min(1, s.score)) * 100 + '%' }" /></span>
              <span class="mt-2 line-clamp-3 block text-sm leading-relaxed text-ash">{{ s.text }}</span>
            </button>
          </li>
        </ul>
      </section>

      <!-- 2 Augmentation -->
      <section class="border-b border-iron p-4">
        <h4 class="flex items-center gap-2 text-sm font-medium"><Icon name="layers" :size="16" class="text-soft-indigo" /> Augmentation</h4>
        <p v-if="msg.augmented_prompt" class="mt-1 text-sm text-ash">Potongan di atas digabung dengan pertanyaanmu jadi prompt ini:</p>
        <pre v-if="msg.augmented_prompt" class="mt-3 max-h-64 overflow-auto whitespace-pre-wrap rounded-lg border border-iron bg-carbon p-3 font-mono text-[12px] leading-relaxed tracking-normal text-ash">{{ msg.augmented_prompt }}</pre>
        <p v-else class="mt-3 text-sm text-mist">Nggak ada konteks yang ditambahkan, jadi pertanyaanmu dikirim ke LLM apa adanya.</p>
      </section>

      <!-- 3 Generation -->
      <section class="p-4">
        <h4 class="flex items-center gap-2 text-sm font-medium"><Icon name="spark" :size="16" class="text-soft-indigo" /> Generation</h4>
        <p class="mt-1 text-sm text-ash" v-if="msg.augmented_prompt">
          Model <span class="font-mono tracking-normal text-bone">{{ msg.model ?? settings?.chat_model }}</span> menyusun jawaban dari konteks tadi, bukan menebak dari hafalan.
        </p>
        <p class="mt-1 text-sm text-ash" v-else>Model <span class="font-mono tracking-normal text-bone">{{ msg.model ?? settings?.chat_model }}</span> menjawab dari pengetahuan bawaannya, bukan dari dokumen.</p>
      </section>
    </div>
  </div>
</template>
