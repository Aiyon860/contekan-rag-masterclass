const KEY = 'contekan:nama'
const DEFAULT_NAME = 'Daniel Aiyon'

/** Nama untuk sapaan di halaman chat baru. Disimpan di browser saja (tidak perlu backend). */
export function useProfileName() {
  const name = useState<string>('profile-name', () => DEFAULT_NAME)

  onMounted(() => {
    try {
      const saved = localStorage.getItem(KEY)
      if (saved !== null) name.value = saved
    } catch {}
  })

  function save(value: string) {
    name.value = value.trim()
    try { localStorage.setItem(KEY, name.value) } catch {}
  }

  return { name, save, DEFAULT_NAME }
}

export function greetingFor(date = new Date()): string {
  const h = date.getHours()
  if (h >= 4 && h < 11) return 'Selamat pagi'
  if (h >= 11 && h < 15) return 'Selamat siang'
  if (h >= 15 && h < 18) return 'Selamat sore'
  return 'Selamat malam'
}
