<script setup lang="ts">
withDefaults(defineProps<{ size?: number }>(), { size: 40 })
// Delapan sinar bergaris bulat, digambar sebagai SVG sendiri (bukan glyph/emoji).
const rays = Array.from({ length: 8 }, (_, i) => i * 45)
</script>

<template>
  <svg :width="size" :height="size" viewBox="0 0 40 40" fill="none" aria-hidden="true" class="shrink-0 text-soft-indigo">
    <g stroke="currentColor" stroke-width="3" stroke-linecap="round">
      <line v-for="a in rays" :key="a" x1="20" y1="4.5" x2="20" y2="14" :transform="`rotate(${a} 20 20)`" />
    </g>
  </svg>
</template>
