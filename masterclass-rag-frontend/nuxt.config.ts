import tailwindcss from '@tailwindcss/vite'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  ssr: false,
  css: ['~/assets/css/main.css'],
  vite: { plugins: [tailwindcss() as any] },
  runtimeConfig: {
    // Kosong = lewat proxy Nuxt (/api -> FastAPI). Isi NUXT_PUBLIC_API_BASE=http://localhost:8000
    // kalau streaming SSE ternyata ke-buffer oleh proxy.
    public: { apiBase: '' },
  },
  routeRules: {
    '/api/**': { proxy: 'http://localhost:8000/api/**' },
  },
  app: {
    head: {
      htmlAttrs: { lang: 'id' },
      title: 'Contekan — Masterclass RAG',
      meta: [{ name: 'theme-color', content: '#0a0a0a' }],
    },
  },
})
