# Zenith Launcher v1.9.10 - Official Engine Edition

Shard terjemahan resmi (paket 1, 4, dan paket 10 berhook) disesuaikan penuh dengan **update data game Tencent terbaru 23 Oktober 2026** (Build `20261023124846`, Versi Data `1.7.0.2`).

### 📦 Berkas Golden Shards Rilis

| Berkas | Ukuran (Byte) | SHA-256 |
|---|---|---|
| `golden_shards_id_v2.zip` | 61.329.849 | `E7B2C1053B65E74DB78C310149FBD4EDA0E96B12B87E0F9E3481908A71B1A3EF` |
| `golden_shards_en_v2.zip` | 61.321.283 | `79DE0874B4865672CC7023582B1B5BD8C2DDEE3043988617D0C25F6284C9F8F5` |

### 🔍 Ringkasan Pembaruan (v1.9.10):
1. **Pembaruan Data Game 1.7.0.2**:
   - Seluruh teks baru dari update data game 23 Okt 2026 (termasuk rekomendasi lineup tim dan skin baru Yang Yuhuan 'Chromatic Scales' / 幻彩音阶) telah diterjemahkan lengkap ke Bahasa Indonesia dan English.
   - Sisa teks Mandarin tidak terjemah di paket 1 dan 4: **0 string**.
2. **Peningkatan UX & Solusi Masalah Lapangan**:
   - **Perbaikan Pesan Peringatan Stale Data**: Mengubah instruksi yang sebelumnya menyuruh "Restore Data dulu" menjadi "Cukup tekan 'Suntik Data'" bila game sudah di lobi. Tombol 'Perbaiki otomatis' kini langsung menjalankan injeksi data tanpa mereset data.
   - **Deteksi Mode Akses (Debuggable)**: Menambahkan peringatan kritis dan dialog jika game terdeteksi tertinggal dalam mode akses debuggable akibat proses yang terputus, mencegah crash/force close game.
3. **Integritas Shard & Keamanan**:
   - Paket 10 berhook menyertakan nama taktisi dan tab faksi di menu Kartu.
   - Lolos seluruh gerbang keselamatan (`guard_shards.py`) tanpa modifikasi tabel DataBin ber-row-checksum.
   - 75 unit test lolos 100%.

> **Catatan**: Ini adalah modifikasi data game pihak ketiga. Selalu gunakan akun cadangan.
