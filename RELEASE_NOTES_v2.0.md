# Zenith Launcher v2.0 - Badge faksi & START GAME

**Wajib Zenith Launcher 2.0.** Data di rilis ini hanya dibaca launcher 2.0 (`packagesV3` di manifest). Launcher 1.9.x tetap memakai data v1.9.11 dan tidak mendapat pembaruan ini.

## Yang baru
- Badge faksi di dasar kartu (Sunset, Central Plains, Riverlands, Three Kingdoms, Zhulu Plateau) dan tombol **START GAME** di lobi kini ikut diterjemahkan.
- Gambar dikirim sebagai **selisih blok** (+-70 MB) atas paket gambar game 15/19/20/1050016095, bukan paket penuh (+-900 MB). Launcher memasangnya hanya bila berkas di HP persis versi dasar (SHA-256), lalu memverifikasi hasilnya.
- **Pulihkan Data** mengembalikan gambar asli dari blok yang disimpan sebelum diubah (terverifikasi SHA-256), tanpa unduh ulang.
- Teks: data terjemahan terbaru (paket 1, 4, 10 berhook) + kamus asisten AI Lingbao.

| Berkas | Ukuran (B) | SHA-256 |
|---|---|---|
| golden_shards_id_v3.zip | 123164620 | `B7B3DEEF8B9703036528D77F84903B47D0C2A9E5A23BBF5C7E009B9F945CABD3` |
| golden_shards_en_v3.zip | 123155764 | `1BCD92E693A57AAA2FFA4055170E0AA60B0791AD081D0755A00AF5628EE5EFD1` |

Isi zip: `1/`, `4/`, `10/` (deskriptor + shard), `delta/<paket>/<berkas>.json|.bin` (selisih gambar), `zenith_ai.lua`.

## Kecocokan
- Dibangun di atas data game **1.8.0.1** (build `20261028201401`). Bila versi data di HP berbeda, teks ditolak gerbang versi; gambar dilewati tanpa mengubah apa pun.
- Diuji di HP (31 Okt 2026): suntik dari data asli -> badge + START GAME tampil, Pulihkan Data -> gambar kembali persis asli, suntik ulang -> berhasil.

## Masih belum terjangkau
`能量` / `棋手经验` / `棋手生命值` di teks kartu tertentu dirender kode game (C#), bukan data.

Catatan: ini modifikasi data game pihak ketiga. Tidak ada jaminan bebas penalti akun; gunakan dengan risiko sendiri.
