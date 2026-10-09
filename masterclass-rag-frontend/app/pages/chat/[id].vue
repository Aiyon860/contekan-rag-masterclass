<script setup lang="ts">
import type { Attachment } from '~/types'
const route = useRoute()
const id = computed(() => route.params.id as string)
const pending = useState<{ id: string; text: string; attachments: Attachment[] } | null>('pending-message', () => null)
const { messages, busy, loadMessages, send, regenerate, stop } = useChatSession(() => id.value)

const scroller = ref<HTMLElement>()
let stick = true
function onScroll() {
  const el = scroller.value!
  stick = el.scrollHeight - el.scrollTop - el.clientHeight < 80
}
function toBottom(force = false) {
  nextTick(() => { if (scroller.value && (stick || force)) scroller.value.scrollTop = scroller.value.scrollHeight })
}
watch(() => messages.value.map(m => m.content.length + m.status).join(), () => toBottom())

async function init() {
  messages.value = []
  if (pending.value?.id === id.value) {
    const { text, attachments } = pending.value
    pending.value = null
    send(text, attachments)
    toBottom(true)
  } else {
    await loadMessages()
    toBottom(true)
  }
}
onMounted(init)
watch(id, init)

function onSend(t: string, a: Attachment[]) { stick = true; send(t, a); toBottom(true) }
const lastAssistant = computed(() => {
  const l = messages.value[messages.value.length - 1]
  return l?.role === 'assistant' ? l : null
})
</script>

<template>
  <div class="flex h-full flex-col">
    <div ref="scroller" class="min-h-0 flex-1 overflow-y-auto" @scroll="onScroll">
      <div class="mx-auto w-full max-w-3xl space-y-8 px-4 py-8">
        <MessageBubble
          v-for="m in messages" :key="m.id" :msg="m"
          :can-regenerate="m === lastAssistant && !busy"
          @regenerate="regenerate"
        />
      </div>
    </div>
    <ChatComposer :busy="busy" autofocus @send="onSend" @stop="stop" />
  </div>
</template>
