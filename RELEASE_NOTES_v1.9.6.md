# Zenith Launcher v1.9.6 - Official Engine Edition

Shard terjemahan Bahasa Indonesia dan English (paket 1, 4, 10) untuk data game versi patch resource `20261014190050` (1.6.0.1).

| Berkas | Ukuran (B) | SHA-256 |
|---|---|---|
| golden_shards_id_v2.zip | 59712803 | `3B7C9C7EF566C85329B5EC52AAAB03BB957C08BE6E73B807BE0325148A5B5E93` |
| golden_shards_en_v2.zip | 59778557 | `AF0718A2A82E1EB311CD914DEA12E818E35300C78166707E1A3727F8CBF54468` |

## Baru di rilis ini
- **Deskripsi kartu, talent, dan skill baru di Pedia/Wiki** kini terjemah (mis. Powerful Minion, Friends Galore, Cold Front Resonance, Tide Cycle, Spring Rain, Skill Breakthrough: Arthur, Global Resonance, Gan & Mo · Empower, Inheritance). Penyebab sebelumnya: teks versi Ace berubah tipis dari katalog lama sehingga tidak cocok. 189 terjemahan baru; celah di tabel yang aman diubah: 191 -> 0 (ID dan EN).
- **Tab Kata kunci (Keyword) di Pedia dan panel kata kunci di dalam pertandingan** kini terjemah (nama + deskripsi 15 kata kunci), lewat hook Lua di paket 10. Nama kata kunci disamakan dengan yang dipakai teks kartu.
- Teks event/toko baru (King of Kings, Line Puppy, Rose Bonus, dll.) ikut terjemah.

## Diuji di HP (Infinix X6882)
Boot, lobi, Pedia (Hero, Kartu Efek, Bakat, Taktisi, Kata kunci), dan satu pertandingan latihan sampai selesai, untuk ID dan EN. CheckPackage gagal 0, crash 0, error Lua 0.

## Masih Mandarin (dirender kode game C#/gambar, tidak terjangkau data)
Label statistik hero di pertandingan (HP Maks, ATK Fisik, ...), token `能量` / `棋手经验` / `棋手生命值` di teks kartu, label ronde `第N回合`, badge faksi di dasar kartu, dan gambar thumbnail video.

## Catatan teknis
Tabel DataBin ber-row-checksum TIDAK ditulis ulang (dijaga `guard_shards`). Paket 10: deskriptor identik dengan data game, hanya isi Lua yang berubah (hook nama taktisi, tab faksi, kata kunci). Launcher menyuntik deskriptor dan shard secara transaksional dan memverifikasi SHA-256. Bila Tencent merilis patch yang mengubah paket 1/4, launcher menolak menyuntik sampai shard baru dirilis.

Catatan: ini modifikasi data game pihak ketiga. Tidak ada jaminan bebas penalti akun; gunakan dengan risiko sendiri (disarankan akun cadangan).
