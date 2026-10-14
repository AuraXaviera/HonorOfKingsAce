# Zenith Launcher v1.9.0 - Official Engine Edition

Shard terjemahan baru (paket 1 dan 4) dibangun dengan mesin resmi PC patcher (`build_device_patch` + `QtsVFS.dll`),
bukan lagi penambalan in-place berukuran terkunci. Hasilnya +-98% teks game terjemah (record Mandarin tersisa di paket 1: 24).

| Berkas | Ukuran (B) | SHA-256 |
|---|---|---|
| golden_shards_id_v2.zip | 40670375 | `B584D1BE5B89F0AB971E2A8542356842415669E6C12224FF280916861514C491` |
| golden_shards_en_v2.zip | 40736553 | `1ECA745C916EDE5C58D31D81FAB92076C864EB2AEE4A6D10B19DFE2E1FC70B6D` |

Isi zip: `1/1.db`, `1/1_0.db`, `4/4.db`, `4/4_0.db`. Paket 10 (Lua) TIDAK diubah.
Launcher menyuntik deskriptor dan shard sebagai pasangan transaksional (rollback otomatis) dan memverifikasi SHA-256 di sandbox.
Tabel data ber-row-checksum tidak ditulis ulang (menulis ulang tabel itu terbukti membuat game beku/crash).

Manifest 2.0 tetap kompatibel dengan launcher lama: bagian `packages` (legacy v1.8.2) dipertahankan dengan hash aset rilis yang benar.

Catatan: ini modifikasi data game pihak ketiga. Tidak ada jaminan bebas penalti akun; gunakan dengan risiko sendiri (disarankan akun cadangan).
