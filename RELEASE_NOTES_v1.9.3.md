# Zenith Launcher v1.9.3 - Official Engine Edition

Shard terjemahan baru (paket 1 dan 4) dibangun dengan mesin resmi PC patcher (`build_device_patch` + `QtsVFS.dll`),
bukan lagi penambalan in-place berukuran terkunci. Hasilnya +-98% teks game terjemah (record Mandarin tersisa di paket 1: 24).

| Berkas | Ukuran (B) | SHA-256 |
|---|---|---|
| golden_shards_id_v2.zip | 59730447 | `024D9F2B82782B362B68DFB3161A3C3310E2AD3D7DACC413A875319CAE03EF37` |
| golden_shards_en_v2.zip | 59796675 | `106CA70EE1E1D454110868054A9047FECA9EDDC329B8A9260D25D67F5002DE9F` |

Isi zip: `1/1.db`, `1/1_0.db`, `4/4.db`, `4/4_0.db`, `10/10.db`, `10/10_0.db`. Paket 10 (Lua) berisi hook yang menerjemahkan nama taktisi dan tab faksi di Kartu (hanya 2 tabel Lua yang berubah; deskriptor identik dengan data game).
Badge faksi di dasar kartu, `{Energy}`/`棋手经验`/`棋手生命值`, dan judul tab Pedia dirender oleh game (C#) dan memang tidak terjangkau data.
Launcher menyuntik deskriptor dan shard sebagai pasangan transaksional (rollback otomatis) dan memverifikasi SHA-256 di sandbox.
Tabel ber-row-checksum yang terbukti merusak game (nama taktisi, keyword, efek Pedia) TIDAK ditulis ulang; hanya tabel kecil yang ditulis ulang mesin resmi
dengan digest dihitung ulang dan telah diuji di HP (boot, lobi, Kartu, Taktisi; belum diuji dalam pertandingan).

Shard dibangun di atas data game versi patch resource `20261014190050` (1.6.0.1) dan diuji di HP untuk Indonesia dan Inggris.
Manifest 2.1 menambah `compat` (sidik deskriptor); manifest lama tetap kompatibel lewat bagian `packages` (legacy v1.8.2).

Kecocokan versi: shard hanya cocok dengan data game versi tertentu (sidik deskriptor di manifest `compat`). Bila Tencent merilis patch yang mengubah paket 1/4, launcher menolak menyuntik (tanpa mengubah apa pun) sampai shard baru dirilis.

Catatan: ini modifikasi data game pihak ketiga. Tidak ada jaminan bebas penalti akun; gunakan dengan risiko sendiri (disarankan akun cadangan).
