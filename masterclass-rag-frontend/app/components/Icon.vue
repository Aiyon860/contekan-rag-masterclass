<script setup lang="ts">
import {
  Menu, Plus, MessageSquare, Database, Settings, Paperclip, ArrowUp, Square, Copy, Check, RefreshCw,
  Pencil, Trash2, X, FileText, FileSpreadsheet, File as FileIcon, ChevronRight, ChevronDown, Upload,
  TriangleAlert, Loader, Eye, Layers, Sparkles, Search, FileType, PanelRightClose,
} from 'lucide-vue-next'

const map: Record<string, any> = {
  menu: Menu, plus: Plus, chat: MessageSquare, database: Database, settings: Settings, attach: Paperclip,
  send: ArrowUp, stop: Square, copy: Copy, check: Check, refresh: RefreshCw, pencil: Pencil, trash: Trash2,
  x: X, file: FileText, sheet: FileSpreadsheet, other: FileIcon, right: ChevronRight, down: ChevronDown,
  upload: Upload, warn: TriangleAlert, loader: Loader, eye: Eye, layers: Layers, spark: Sparkles,
  search: Search, pdf: FileType, close: PanelRightClose,
}
const props = withDefaults(defineProps<{ name: string; size?: number }>(), { size: 18 })
const comp = computed(() => map[props.name] ?? FileIcon)
</script>

<template>
  <component :is="comp" :size="size" :stroke-width="1.5" aria-hidden="true" />
</template>
