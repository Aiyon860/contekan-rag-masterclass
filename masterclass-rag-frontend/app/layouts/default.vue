<script setup lang="ts">
const drawer = ref(false)
const route = useRoute()
const { target } = usePreview()
const { load: loadSettings } = useSettings()
const { load: loadDocs } = useDocuments()
const { load: loadChats } = useChats()
const { check } = useHealth()

onMounted(() => {
  loadSettings(); loadDocs(); loadChats(); check()
  setInterval(check, 20000)
})
watch(() => route.fullPath, () => { drawer.value = false })
</script>

<template>
  <div class="flex h-dvh w-full bg-carbon text-bone">
    <!-- Sidebar desktop -->
    <aside class="hidden md:flex w-[280px] shrink-0 flex-col border-r border-iron bg-graphite">
      <AppSidebar />
    </aside>

    <!-- Drawer mobile -->
    <Transition name="fade">
      <div v-if="drawer" class="fixed inset-0 z-40 bg-pure-black/70 md:hidden" @click="drawer = false" />
    </Transition>
    <Transition name="slide">
      <aside v-if="drawer" class="fixed inset-y-0 left-0 z-50 flex w-[86vw] max-w-[300px] flex-col border-r border-iron bg-graphite md:hidden">
        <AppSidebar @close="drawer = false" />
      </aside>
    </Transition>

    <div class="flex min-w-0 flex-1 flex-col">
      <header class="flex h-12 shrink-0 items-center gap-2 border-b border-iron px-3 md:hidden">
        <button class="btn-icon" aria-label="Buka menu" @click="drawer = true"><Icon name="menu" /></button>
        <span class="text-[15px] font-medium tracking-tight">Contekan</span>
      </header>
      <OllamaBanner />
      <main class="min-h-0 flex-1"><slot /></main>
    </div>

    <DocumentPreview v-if="target" />
    <ToastHost />
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity .25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-enter-active, .slide-leave-active { transition: transform .3s var(--ease-out-expo); }
.slide-enter-from, .slide-leave-to { transform: translateX(-100%); }
</style>
