# Zenith Launcher v1.9.11 - shard untuk data game 1.8.0.1

Shard terjemahan Indonesia dan Inggris untuk data game **1.8.0.1** (build resource `20261028201401`). APK game tetap versionCode 774472.

| Berkas | Ukuran (B) | SHA-256 |
|---|---|---|
| golden_shards_id_v2.zip | 62189118 | `FF1C69FC3E297CCA0A66B5420C9A232B505B6A55C6228B851825AA093ABD57C4` |
| golden_shards_en_v2.zip | 62178568 | `7A75F23CD42CE4042A0FE0C4DD479C1D979AB05BFAAB67A645B43DA719E40294` |

Isi zip: `1/1.db`, `1/1_0.db`, `4/4.db`, `4/4_0.db`, `10/10.db`, `10/10_0.db` (paket 10 berisi hook Lua nama taktisi dan tab faksi).

## Yang baru
- Dibangun di atas data asli 1.8.0.1 (paket 1, 4, 10 ditarik dari HP uji setelah update sampai lobi).
- Teks baru dari update ini: efek kata kunci [Debut] Lady Sun (ID dan EN). Celah teks setelah build: 0.
- Tabel ber-row-checksum tidak ditulis ulang (guard lulus). Diuji di HP: lobi dan Kartu tampil terjemah, `CheckPackage failed` 0.

## Untuk pengguna
Pengguna yang sudah pernah patch: update game sampai lobi, buka Zenith, Cek Update, lalu Suntik Data.
Shard ini hanya cocok dengan data 1.8.0.1; launcher menolak menyuntik ke data versi lain tanpa mengubah apa pun.

Teks yang dirender kode game (badge faksi di dasar kartu, `能量`/`棋手经验`/`棋手生命值`) memang tidak terjangkau data.
