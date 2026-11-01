# Zenith Launcher v2.0 - Badge faksi & START GAME

**Wajib Zenith Launcher 2.0.** Data di rilis ini hanya dibaca launcher 2.0 (`packagesV3` di manifest). Launcher 1.9.x tetap memakai data v1.9.11 dan tidak mendapat pembaruan ini.

## Yang baru
- Badge faksi di dasar kartu (Sunset, Central Plains, Riverlands, Three Kingdoms, Zhulu Plateau) dan tombol **START GAME** di lobi kini ikut diterjemahkan.
- Gambar dikirim sebagai **selisih blok** (+-70 MB) atas paket gambar game 15/19/20/1050016095, bukan paket penuh (+-900 MB). Launcher memasangnya hanya bila berkas di HP persis versi dasar (SHA-256), lalu memverifikasi hasilnya.
- **Pulihkan Data** mengembalikan gambar asli dari blok yang disimpan sebelum diubah (terverifikasi SHA-256), tanpa unduh ulang.
- Teks: data terjemahan terbaru (paket 1, 4, 10 berhook); nama taktisi Lady Sun dan asisten Lingbao diseragamkan (sebelumnya ada "wangi", "fragrant", "Dolia", dll.).
- Asisten AI Lingbao: 125 kalimat formasi baru diterjemahkan.
- Launcher: tab Sinergi dan HUD in-game kini memakai **10 formasi resmi** dari menu Lineup game; pemberitahuan otomatis bila ada versi launcher baru; unduhan data bisa dilanjutkan bila terputus.

| Berkas | Ukuran (B) | SHA-256 |
|---|---|---|
| golden_shards_id_v3.zip | 123179416 | `5083AF17BB92F179588941E245EE1716A314DCB612830DCF407CC44F5D518490` |
| golden_shards_en_v3.zip | 123169213 | `D6C92B488FE80EE2CFFB28CEC3532FF2C05BB0D22B444E6F079E5F8F7351FEAD` |

Isi zip: `1/`, `4/`, `10/` (deskriptor + shard), `delta/<paket>/<berkas>.json|.bin` (selisih gambar), `zenith_ai.lua`.

## Kecocokan
- Dibangun di atas data game **1.8.0.1** (build `20261028201401`). Bila versi data di HP berbeda, teks ditolak gerbang versi; gambar dilewati tanpa mengubah apa pun.
- Diuji di HP (31 Okt 2026): suntik dari data asli -> badge + START GAME tampil, Pulihkan Data -> gambar kembali persis asli, suntik ulang -> berhasil.

## Masih belum terjangkau
`能量` / `棋手经验` / `棋手生命值` di teks kartu tertentu dirender kode game (C#), bukan data.

Catatan: ini modifikasi data game pihak ketiga. Tidak ada jaminan bebas penalti akun; gunakan dengan risiko sendiri.

## Pembaruan 1 Nov 2026 (aset v2.0 diganti)

- Dibangun ulang di atas data game terbaru: Tencent mengubah paket 4, 10 dan 1050016095 tanpa mengganti versi build (`20261028201401`). Pulihkan Data kembali bisa menyimpan cadangan asli; keempat paket gambar terpasang.
- Pencarian lineup menerima nama Indonesia/Inggris (hero, taktisi, kata kunci), gabungan kata, dan ketikan yang belum selesai.
- Label Toko dan penulis lineup resmi ("-Rekomendasi resmi") diterjemahkan; nama pemain tidak diubah.
- Kamus Lingbao & lineup bertambah.
- Diuji di HP: lobi, START GAME, Kartu, Taktisi, Battle Pass, Lineup + pencarian.

| Berkas | SHA-256 |
|---|---|
| golden_shards_id_v3.zip | `0944A45E88A3E724E3DE8B56A05B9CBE8D2206ABB0EE90E6A2E548815BE074AA` |
| golden_shards_en_v3.zip | `81C4D54184A4233E41093365CACAD13583A69F3986945972E98BD15A86DB169A` |
