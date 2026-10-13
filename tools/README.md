# Zenith Card Patcher CLI (Developer Tool)

Tool otomatisasi pengembang untuk memperbarui terjemahan kartu Honor of Kings Ace secara **bit-exact**, **in-memory**, dan **bebas crash**.

---

## ⚡ Alur Penggunaan Cepat

### 1. Tambah Kata Baru ke Kamus
Anda bisa mengedit langsung file [`tools/terms_override.json`](file:///d:/Pribadi/Project/HOKAce/tools/terms_override.json), atau menggunakan perintah CLI:

```powershell
# Menambah istilah Bahasa Indonesia
.venv\Scripts\python.exe tools/patch_cards.py --add-id "Kata Lama" "Kata Baru"

# Menambah istilah Bahasa Inggris
.venv\Scripts\python.exe tools/patch_cards.py --add-en "Old Word" "New Word"
```

---

### 2. Uji Coba Cepat di Memori (< 2 Detik)
Sebelum menyentuh file atau mengunggah ke internet, uji perubahan di RAM:

```powershell
.venv\Scripts\python.exe tools/patch_cards.py
```
> [!NOTE]
> Perintah ini membaca seluruh 23 tabel kartu multi-chunk, memvalidasi integritas ukuran *uncompressed* bit-exact, dan memeriksa apakah terjadi *overflow* slot tanpa mengubah file zip di disk.

---

### 3. Terapkan ke Berkas Lokal
Jika hasil uji coba memuaskan, perbarui arsip ZIP lokal dan manifest SHA-256:

```powershell
.venv\Scripts\python.exe tools/patch_cards.py --apply
```

---

### 4. Deploy Sekaligus ke GitHub Release
Jika ingin langsung menerapkan, meng-commit ke Git, dan mengunggah aset ke GitHub Release `v1.8.2`:

```powershell
.venv\Scripts\python.exe tools/patch_cards.py --deploy
```
