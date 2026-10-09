# Masterclass RAG (Retrieval-Augmented Generation)

## Waktu presentasi dan tanya jawab: 15 menit

## Daftar Isi
1. Apa itu RAG?
2. Masalah yang diselesaikan oleh RAG
3. Tahapan-tahapan dalam RAG
4. Demo
5. Glosarium

## Bab 1 Apa itu RAG?
- RAG adalah teknik supaya AI bisa 'buka contekan' dulu sebelum menjawab. Contekannya berupa dokumen/data yang kita sediakan, jadi AI tidak cuma mengandalkan hafalan dari masa training.

## Bab 2 Masalah yang diselesaikan oleh RAG
Model AI bawaan hanya tahu informasi sampai batas waktu training-nya jadi ketika diberi pertanyaan mengenai informasi/berita/kejadian terbaru, AI nya jadi halusinasi tidak sesuai yang kita mau. 

Di sisi lain, melatih ulang model AI itu lama dan mahal, karena butuh spek server/GPU yang tinggi dan waktu berhari-hari sampai berminggu-minggu. Tidak realistis dan kurang cocok dilakukan tiap ada dokumen baru.

Di sinilah RAG membantu: AI cukup diberi dokumen yang relevan saat menjawab, tanpa perlu dilatih ulang, sehingga halu nya berkurang.

## Bab 3 Tahapan-tahapan dalam RAG
### Tahap 1 Persiapan data (diawal):
1. Pecah dokumen (misal PDF) menjadi Chunk (potongan kecil, bisa berupa kalimat atau paragraf)
2. Ubah setiap Chunk jadi deretan angka yang mewakili maknanya (embedding). Teks yang artinya mirip akan punya angka yang berdekatan.
3. Disimpan di vector database (contoh: ChromaDB)

### Tahap 2 Saat user bertanya:
1. Terima input pertanyaan dari user
2. Ubah input pertanyaan jadi embeddings (harus memakai model embedding yang sama dengan di tahap 1 no 2)
3. Cari chunk yang maknanya paling mirip dengan pertanyaan (similarity search), lalu ambil beberapa teratas (Top-K, misalnya 3 teratas) → Retrieval
4. Gabungkan chunk tadi dengan pertanyaan user sebagai bahan jawaban, lalu kirim ke LLM → Augmentation
5. LLM menyusun jawaban berdasarkan chunk tersebut, bukan asal tebak → Generation

# Demo
- Pake platform web, tech stack sebagai berikut (lokal semua, tidak ada yang dicloud):
    - Frontend: Nuxt
    - Backend: FastAPI (pyproject bukan requirements.txt)
    - Database: SQLite (untuk track history chat dan path data eksternal, kemudian pake SQLModel bawaan FastAPI saja yang itu on top of sqlalchemy dan pydantic) ChromaDB
    - AI Model: gemma3:1b dan nomic-embed-text:latest (buat convert ke embeddings) on Ollama
- DESIGN.md: https://styles.refero.design/style/108e2695-6970-47d5-b5b0-eea8fc34e048
- Contraints:
  1. Batasi file nya hanya boleh format .txt, .md, .pdf, .docx, .xlsx, .csv
  2. Ukuran file maks 10MB (default)
  3. Bahasa yang digunakan dalam typography di web ini memakai Bahasa Indonesia yang setengah formal dan setengah informal (seimbang)
- Alur aplikasi:
  1. User membuka aplikasi yang bentukannya mirip dengan web LLM ChatGPT, Gemini, atau Claude (ada tempat box buat chatting prompt kemudian history chat, memory berupa document yang diinputkan untuk RAG nya (jadi walaupun beda chat/bikin chat baru memory documennya tetap persist tidak hilang, jadi memory tetap), streaming output dari AI nya pake server-side events (SSE), bisa buka isi file dokumennya nya di chat nya)
  2. Kalo user belum menginputkan data eksternal, user bisa menginputkan dulu data nya bisa berupa file dokumen maupun teks nanti akan diolah jadi embeddings yang dimasukkan ke ChromaDB dan raw data eksternal nya disimpan di dalam folder projek aja biar simple dengan path ke data eksternal nya itu dimasukkan ke dalam SQLite
  3. User menginputkan prompt kemudian prompt nya digunakan untuk mencari chunk yang paling relevan dan setelah itu diambil top 3 saja dulu hasil yang paling relevan (retrieval)
  4. Setelah itu, chunk yang sudah diambil tadi di-augment ke prompt nya dan dilempar ke LLM (augmentation)
  5. LLM dapat menjawab dengan grounded answer (tidak asal nebak atau halusinasi) (generation)
  6. Setelah itu, history chat user dengan AI terbentuk dan disimpan ke SQLite
- Tambahan:
  1. Buatin menu sendiri terpisah halaman setting untuk mengatur nilai Top-K nya, batas ukuran file input, dan lainnya jika diperlukan
  2. Ada menu sendiri untuk melihat memory dari dokumen-dokumen yang diinputkan oleh user
  3. Buat dokumentasi lengkap mengenai projek ini di readme.md dengan Bahasa Indonesia yang setengah formal dan setengah informal (seimbang)
  4. Hapus file kode yang sekiranya tidak diperlukan dari projek (konfirmasi dulu jangan asal langsung delete)
- Must:
  1. Web harus responsive
  2. Cepat (optimisic ui)
