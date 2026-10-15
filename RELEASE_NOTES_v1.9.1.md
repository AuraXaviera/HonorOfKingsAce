# Zenith Launcher v1.9.1 - Official Engine Edition

Shard terjemahan baru (paket 1 dan 4) dibangun dengan mesin resmi PC patcher (`build_device_patch` + `QtsVFS.dll`),
bukan lagi penambalan in-place berukuran terkunci. Hasilnya +-98% teks game terjemah (record Mandarin tersisa di paket 1: 24).

| Berkas | Ukuran (B) | SHA-256 |
|---|---|---|
| golden_shards_id_v2.zip | 49810728 | `B4FA3D4EFEF408F50931855B1F622EF62BC2B3AF9AE79F6A5218D127BEC00246` |
| golden_shards_en_v2.zip | 49876944 | `BE0FDFE92E030AF7485B053E7E9B1B58C1FB1C22DE98632888F6FCA00D6811C6` |

Isi zip: `1/1.db`, `1/1_0.db`, `4/4.db`, `4/4_0.db`. Paket 10 (Lua) TIDAK diubah, jadi tab faksi di Kartu dan nama taktisi tetap Mandarin;
badge faksi kartu, `{Energy}`/`棋手经验`, dan judul tab Pedia dirender oleh game (C#) dan memang tidak terjangkau data.
Launcher menyuntik deskriptor dan shard sebagai pasangan transaksional (rollback otomatis) dan memverifikasi SHA-256 di sandbox.
Tabel ber-row-checksum yang terbukti merusak game (nama taktisi, keyword, efek Pedia) TIDAK ditulis ulang; hanya tabel kecil yang ditulis ulang mesin resmi
dengan digest dihitung ulang dan telah diuji di HP (boot, lobi, Kartu, Taktisi; belum diuji dalam pertandingan).

Shard dibangun di atas data game versi patch resource `20261014190050` (1.6.0.1) dan diuji di HP untuk Indonesia dan Inggris.
Manifest 2.1 menambah `compat` (sidik deskriptor); manifest lama tetap kompatibel lewat bagian `packages` (legacy v1.8.2).

Kecocokan versi: shard hanya cocok dengan data game versi tertentu (sidik deskriptor di manifest `compat`). Bila Tencent merilis patch yang mengubah paket 1/4, launcher menolak menyuntik (tanpa mengubah apa pun) sampai shard baru dirilis.

Catatan: ini modifikasi data game pihak ketiga. Tidak ada jaminan bebas penalti akun; gunakan dengan risiko sendiri (disarankan akun cadangan).
