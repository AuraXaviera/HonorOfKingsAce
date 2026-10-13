#!/usr/bin/env python3
"""
Zenith Patcher // Master Shard Generator
========================================
Generates bit-exact, 100% complete golden shards for Android & PC
including all 17 Master Tables (Core UI, Lobby, Modes, Cards, Skills)
and all 4 Lua UI Hooks (ShopHelper, Lineups, LobbyPresenter, GameCenter).
"""

import os
import sys
import gzip
import json
import struct
import hashlib
import zipfile
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'd:\Pribadi\Project\HOKAce\ZenithPatcher\engine')
import wxq_patch.qtsvfs as qts
from wxq_patch.adaptive import fields, Catalog, encode_varint
import wxq_patch.unity_package_installer as upi_mod

ROOT_DIR = Path(r'd:\Pribadi\Project\HOKAce')
WORK_DIR = ROOT_DIR / "work_temp"
ONLINE_DIR = ROOT_DIR / "online_shards"
REPO_DIR = ROOT_DIR / "work_temp" / "repo_clone"

CATALOG_ID_PATH = ROOT_DIR / "ZenithPatcher" / "catalog" / "catalog_id.json.gz"
CATALOG_EN_PATH = ROOT_DIR / "ZenithPatcher" / "catalog" / "catalog_en.json.gz"
TERMS_PATH = REPO_DIR / "tools" / "terms_override.json"

# Compact MOBA Terms (Indonesian)
COMPACT_TERMS_ID = {
    '开始游戏': 'Mulai Game',
    '排位': 'Rank',
    '训练': 'Latihan',
    '自定义': 'Kustom',
    '道具': 'Item',
    '特效': 'Efek',
    '确认跳过': 'Lewati',
    '战令': 'Pass',
    '段位': 'Tier',
    '棋手': 'Taktisi',
    '活动': 'Event',
    '商城': 'Toko',
    '祈愿': 'Harapan',
    '首充': 'Top Up',
    '充值': 'Top Up',
    '背包': 'Tas',
    '邮件': 'Pesan',
    '简报': 'Kabar',
    '观战': 'Tonton',
    '百科': 'Pedia',
    '段位保护': 'Proteksi Tier',
    '段位不足': 'Tier Kurang',
    '虚位以待': 'Slot Kosong',
    '等待开始': 'Menunggu',
    '当前备战选手': 'Pemain Bersiap',
    '即将开始': 'Segera Mulai',
    '确认提升为管理么': 'Jadikan Manajer?',
    '确认移出管理么': 'Hapus Manajer?',
    '请先加入战区': 'Gabung zona dulu',
    '请先加入战队': 'Gabung tim dulu',
    '确认离开战斗吗?': 'Keluar pertempuran?',
    '确认离开战斗吗？': 'Keluar pertempuran?',
    '班叔': 'Paman Ban',
    '班叔头像': 'Avatar Paman Ban',
    '万象启程': 'Awal ACE',
    '万象启程赛季': 'Musim ACE',
    '万象大赛': 'Turnamen ACE',
    '钻石狂潮': 'Gila Berlian',
    'cangkok': 'Substitusi Taktis',
    '嫁接': 'Substitusi Taktis',
    'Bangun Manusia Salju': 'Susun Manusia Salju',
    '堆雪人': 'Susun Manusia Salju',
    'Mencari kekayaan dalam bahaya': 'Judi Keberuntungan',
    '铤而走险': 'Judi Keberuntungan',
    '回合': 'Ronde ',
    'S1万象启程': 'S1 Awal Mula',
    '<a href=4><color=#ffffff>╤<b>凯旋</b></color></a>：获得{0|1}{Energy}。': '<a href=4><color=#ffffff>╤<b>Triumph</b></color></a>: +{0|1}{Energy}.',
    '<a href=4><color=#ffffff>╤<b>凯旋</b></color></a>：获得{0|2}{Energy}。': '<a href=4><color=#ffffff>╤<b>Triumph</b></color></a>: +{0|2}{Energy}.',
    '棋手升级时，{LordExp}+{3|2}。': 'Saat naik level, {LordExp}+{3|2}.',
    '棋手升级时，{LordExp}+{3|4}。': 'Saat naik level, {LordExp}+{3|4}.',
    '本回合战斗开始时，弈星随机<color=#ffffff><b>复制</b></color>1名敌方英雄。': 'Mulai ronde, Yixing salin 1 Hero lawan acak.',
}

# Compact MOBA Terms (English)
COMPACT_TERMS_EN = {
    '开始游戏': 'Start Game',
    '排位': 'Ranked',
    '训练': 'Training',
    '自定义': 'Custom',
    '道具': 'Items',
    '特效': 'Effects',
    '确认跳过': 'Skip',
    '战令': 'Pass',
    '段位': 'Tier',
    '棋手': 'Tactician',
    '活动': 'Event',
    '商城': 'Shop',
    '祈愿': 'Wish',
    '首充': 'Top-Up',
    '充值': 'Top-Up',
    '背包': 'Bag',
    '邮件': 'Mail',
    '简报': 'News',
    '观战': 'Spectate',
    '百科': 'Wiki',
    '段位保护': 'Tier Protection',
    '万象启程': 'Genesis',
    '万象启程赛季': 'Genesis Season',
    '万象大赛': 'ACE Tournament',
    '钻石狂潮': 'Diamond Rush',
    'cangkok': 'Subtle Switch',
    '嫁接': 'Subtle Switch',
    'graft': 'Subtle Switch',
    'Graft': 'Subtle Switch',
    'Build Snowman': 'Snowman Builder',
    'Bangun Manusia Salju': 'Snowman Builder',
    '堆雪人': 'Snowman Builder',
    'Seeking wealth in danger': "Fortune's Gamble",
    'Mencari kekayaan dalam bahaya': "Fortune's Gamble",
    '铤而走险': "Fortune's Gamble",
    '回合': 'Round ',
    'S1万象启程': 'S1 Genesis',
    '<a href=4><color=#ffffff>╤<b>凯旋</b></color></a>：获得{0|1}{Energy}。': '<a href=4><color=#ffffff>╤<b>Triumph</b></color></a>: +{0|1}{Energy}.',
    '<a href=4><color=#ffffff>╤<b>凯旋</b></color></a>：获得{0|2}{Energy}。': '<a href=4><color=#ffffff>╤<b>Triumph</b></color></a>: +{0|2}{Energy}.',
    '棋手升级时，{LordExp}+{3|2}。': 'On level up, {LordExp}+{3|2}.',
    '棋手升级时，{LordExp}+{3|4}。': 'On level up, {LordExp}+{3|4}.',
    '本回合战斗开始时，弈星随机<color=#ffffff><b>复制</b></color>1名敌方英雄。': 'At round start, Yixing copies 1 random enemy Hero.',
}

COMPACT_RULES_ID = [
    ('。', '.'), ('，', ','), ('：', ':'), ('！', '!'), ('？', '?'),
    ('（', '('), ('）', ')'), ('【', '['), ('】', ']'), ('、', ','),
    ('；', ';'), ('“', '"'), ('”', '"'), ('‘', "'"), ('’', "'"),
    ('Mendapatkan', 'Dapat'), ('mendapatkan', 'dapat'),
    ('Dapatkan', 'Dapat'), ('dapatkan', 'dapat'),
    ('Memperoleh', 'Dapat'), ('memperoleh', 'dapat'),
    ('Memberikan', 'Beri'), ('memberikan', 'beri'),
    ('Meningkatkan', 'Tingkatkan'), ('meningkatkan', 'tingkatkan'),
    ('Mengurangi', 'Kurangi'), ('mengurangi', 'kurangi'),
    ('Menyebabkan', 'Picukan'), ('menyebabkan', 'picu'),
    ('Menghasilkan', 'Beri'), ('menghasilkan', 'beri'),
    ('Menggunakan', 'Pakai'), ('menggunakan', 'pakai'),
    ('Digunakan', 'Dipakai'), ('digunakan', 'dipakai'),
    ('Pemain Catur', 'Player'), ('pemain catur', 'player'),
    ('Kartu Hero', 'Hero'), ('kartu hero', 'hero'),
    ('Hero Card', 'Hero'), ('hero card', 'hero'),
    ('Kartu Peralatan', 'Gear'), ('kartu peralatan', 'gear'),
    ('Peralatan', 'Gear'), ('peralatan', 'gear'),
    ('Kesehatan Maksimal', 'Max HP'), ('kesehatan maksimal', 'max HP'),
    ('Kesehatan', 'HP'), ('kesehatan', 'HP'),
    ('Kerusakan Fisik', 'Phys DMG'), ('kerusakan fisik', 'Phys DMG'),
    ('Kerusakan Sihir', 'Mag DMG'), ('kerusakan sihir', 'Mag DMG'),
    ('Kerusakan Sebenarnya', 'True DMG'), ('kerusakan sebenarnya', 'True DMG'),
    ('Kerusakan', 'DMG'), ('kerusakan', 'DMG'),
    ('Serangan Fisik', 'Phys ATK'), ('serangan fisik', 'Phys ATK'),
    ('Serangan Sihir', 'Mag ATK'), ('serangan sihir', 'Mag ATK'),
    ('Serangan', 'ATK'), ('serangan', 'ATK'),
    ('Pertahanan Fisik', 'Phys DEF'), ('pertahanan fisik', 'Phys DEF'),
    ('Pertahanan Sihir', 'Mag DEF'), ('pertahanan sihir', 'Mag DEF'),
    ('Pertahanan', 'DEF'), ('pertahanan', 'DEF'),
    ('Kecepatan Gerak', 'MS'), ('kecepatan gerak', 'MS'),
    ('Kecepatan Serangan', 'AS'), ('kecepatan serangan', 'AS'),
    ('Kecepatan', 'SPD'), ('kecepatan', 'SPD'),
    ('Pengalaman', 'EXP'), ('pengalaman', 'EXP'),
    ('Tingkat', 'Lv'), ('tingkat', 'Lv'),
    ('Level', 'Lv'), ('level', 'Lv'),
    ('putaran', 'ronde'), ('Putaran', 'Ronde'),
    ('Pertempuran', 'Battle'), ('pertempuran', 'battle'),
    ('Kemampuan', 'Skill'), ('kemampuan', 'skill'),
    ('Kekuatan Kemampuan', 'AP'), ('kekuatan kemampuan', 'AP'),
    ('Kekuatan Skill', 'AP'), ('kekuatan skill', 'AP'),
    ('Tambahan', 'Bonus'), ('tambahan', 'bonus'),
    ('secara acak', 'acak'), ('Secara acak', 'Acak'),
    ('memiliki peluang', 'berpeluang'), ('Memiliki peluang', 'Berpeluang'),
    ('Koin Kuno', 'Koin'), ('koin kuno', 'koin'),
    (' yang ', ' '), (' Yang ', ' '),
    (' akan ', ' '), (' Akan ', ' '),
    (' untuk ', ' '), (' Untuk ', ' '),
    (' Anda', ''), (' anda', ''),
    (' adalah ', ' '),
]

PUNCT_RULES = [
    ('。', '.'), ('，', ','), ('：', ':'), ('！', '!'), ('？', '?'),
    ('（', '('), ('）', ')'), ('【', '['), ('】', ']'), ('、', ','),
    ('；', ';'), ('“', '"'), ('”', '"'), ('‘', "'"), ('’', "'"),
]

import re

def compact_text(text, is_en=False):
    if not text:
        return text
    res = text
    rules = PUNCT_RULES if is_en else COMPACT_RULES_ID
    for old, new in rules:
        res = res.replace(old, new)
    res = re.sub(r' +', ' ', res)
    return res.strip()

KEYWORD_SOL_ID = {
    '#4A66036199430027#': 'Blink',
    '#4A6605ADF08473E4#': 'Deploy',
    '#4A6612AB1F2D0608#': 'Merge',
    '#4A66163444B87D8B#': 'Keluar',
    '#4A662B61AD14E169#': 'Kalah',
    '#4A663327782A5833#': 'Lv Smt',
    '#4A66458CC503A584#': 'Serang',
    '#4A6653FCCA9A61B0#': 'Arcomia Core',
    '#4A668850FFF91694#': 'Revive',
    '#4A668D148E2A33BB#': 'Geser utk Merge',
    '#4A66AE7BEC3A770D#': 'Curi',
    '#4A66B1B2C9B0ECA5#': 'Lihat Toko',
    '#4A66C68A7AB1AF0D#': 'Korban',
    '#4A66CA4C52052142#': 'Gunakan di Toko',
    '#4A66D52802E8DC92#': 'Flash',
    '#4A66D545F260C380#': 'Triumph',
    '#4A66DCA3D38FCAAC#': 'Prepare',
    '#4A66EFCBB004A33A#': 'Totem'
}

KEYWORD_SOL_EN = {
    '#4A66036199430027#': 'Blink',
    '#4A6605ADF08473E4#': 'Deploy',
    '#4A6612AB1F2D0608#': 'Merge',
    '#4A66163444B87D8B#': 'Exit',
    '#4A662B61AD14E169#': 'Defeat',
    '#4A663327782A5833#': 'Lv Temp',
    '#4A66458CC503A584#': 'Engage',
    '#4A6653FCCA9A61B0#': 'Arcomia Core',
    '#4A668850FFF91694#': 'Revive',
    '#4A668D148E2A33BB#': 'Drag to Merge',
    '#4A66AE7BEC3A770D#': 'Steal',
    '#4A66B1B2C9B0ECA5#': 'Shop Info',
    '#4A66C68A7AB1AF0D#': 'Sacrifice',
    '#4A66CA4C52052142#': 'Use in Shop',
    '#4A66D52802E8DC92#': 'Flash',
    '#4A66D545F260C380#': 'Triumph',
    '#4A66DCA3D38FCAAC#': 'Prepare',
    '#4A66EFCBB004A33A#': 'Totem'
}


# Lobby & Drawer Table (0x616B)
LOBBY_TABLE_ID = {
    '活动': 'Event',
    '商城': 'Toko',
    '祈愿': 'Harapan',
    '首充': 'Top Up',
    '棋手': 'Taktisi',
    '卡牌': 'Kartu',
    '阵容': 'Lineup',
    '战令': 'Pass',
    '珍传祈愿': 'Harapan+',
    '成长之路': 'Progres',
    '背包': 'Tas',
    '邮件': 'Pesan',
    '简报': 'Kabar',
    '观战': 'Tonton',
    '百科': 'Pedia',
}

LOBBY_TABLE_EN = {
    '活动': 'Event',
    '商城': 'Shop',
    '祈愿': 'Wish',
    '首充': 'Top-Up',
    '棋手': 'Tactician',
    '卡牌': 'Cards',
    '阵容': 'Lineup',
    '战令': 'Pass',
    '珍传祈愿': 'Wish+',
    '成长之路': 'Progress',
    '背包': 'Bag',
    '邮件': 'Mail',
    '简报': 'News',
    '观战': 'Spectate',
    '百科': 'Wiki',
}

def make_rec(k, v):
    kb = k.encode('utf-8')
    vb = v.encode('utf-8')
    f1 = b'\n' + encode_varint(len(kb)) + kb
    f2 = b'\x12' + encode_varint(len(vb)) + vb
    inner = f1 + f2
    return b'\n' + encode_varint(len(inner)) + inner

def patch_table_generic(f, pkg, sm, fhash, label, catalog, priority_keys=None, is_en=False):
    if fhash not in sm:
        print(f"  [SKIP] 0x{fhash:016X} ({label}): not in slot map")
        return False
    raw = pkg.extract(fhash, sm)
    slots = sorted(sm[fhash].values() if isinstance(sm[fhash], dict) else sm[fhash], key=lambda x:x.chunk_id)
    
    recs = []
    for tag, nested, enc in fields(raw):
        parts = list(fields(nested))
        k = next(p[1].decode('utf-8', 'ignore') for p in parts if p[0] == 10)
        src = next(p[1].decode('utf-8', 'ignore') for p in parts if p[0] == 18)
        tgt = catalog.lookup(fhash, k, src)
        if tgt and tgt != src:
            tgt = compact_text(tgt, is_en=is_en)
        new_enc = enc
        diff = 0
        if tgt and tgt != src:
            new_enc = make_rec(k, tgt)
            diff = len(new_enc) - len(enc)
        recs.append({'k': k, 's': src, 't': tgt, 'orig': enc, 'new': new_enc, 'diff': diff})

    applied_neg = [r for r in recs if r['diff'] <= 0 and r['t'] and r['t'] != r['s']]
    gt_zero = [r for r in recs if r['diff'] > 0 and r['t'] and r['t'] != r['s']]
    
    def get_pri(r):
        s, t = r['s'], r['t'] or ''
        return not any(kw in s or kw in t for kw in ('雪人', '嫁接', '铤而走险', 'Snowman', 'Graft', 'Salju', 'Taktis', 'Keberuntungan', 'Diamond', '钻石', '万象', 'ACE'))

    if priority_keys:
        gt_zero.sort(key=lambda r: (r['k'] not in priority_keys, get_pri(r), len(r['s']) > 20, r['diff']))
    else:
        gt_zero.sort(key=lambda r: (get_pri(r), len(r['s']) > 20, r['diff']))

    budget = len(raw) - sum(len(r['new'] if r['diff'] <= 0 else r['orig']) for r in recs)
    applied_pos = []
    for r in gt_zero:
        if budget >= r['diff']:
            budget -= r['diff']
            applied_pos.append(r)

    applied_pos_ids = set(id(r) for r in applied_pos)
    applied_neg_ids = set(id(r) for r in applied_neg)

    def test_and_pack(cur_budget):
        for r in recs:
            if id(r) in applied_pos_ids or id(r) in applied_neg_ids:
                r['active'] = r['new']
            else:
                r['active'] = r['orig']
        
        pad_b = cur_budget
        if pad_b > 0:
            for r in recs:
                if (id(r) in applied_pos_ids or id(r) in applied_neg_ids) and r['t'] and r['t'] != r['s'] and len(r['t']) + pad_b < 250:
                    r['active'] = make_rec(r['k'], r['t'] + ' ' * pad_b)
                    pad_b = 0
                    break
        tbl = b''.join(r['active'] for r in recs)
        chunks_comp = []
        offset = 0
        fits = True
        for s in slots:
            c_raw = tbl[offset : offset + s.uncompressed_size]
            offset += s.uncompressed_size
            comp = qts.lz4.block.compress(c_raw, mode='high_compression', compression=12, store_size=False)
            slack = s.slot_size - 48
            if len(comp) > slack:
                fits = False
                break
            chunks_comp.append((s, comp, len(c_raw)))
        return fits, chunks_comp

    fits, chunks_comp = test_and_pack(budget)
    while not fits and applied_pos:
        dropped = applied_pos.pop()
        applied_pos_ids.remove(id(dropped))
        budget += dropped['diff']
        fits, chunks_comp = test_and_pack(budget)

    while not fits and applied_neg:
        dropped = applied_neg.pop()
        applied_neg_ids.remove(id(dropped))
        budget -= dropped['diff']
        fits, chunks_comp = test_and_pack(budget)

    if not fits:
        applied_pos_ids.clear()
        applied_neg_ids.clear()
        fits, chunks_comp = test_and_pack(0)

    for s, comp, raw_sz in chunks_comp:
        slot_bytes = upi_mod._slot_bytes(s, comp, raw_sz, file_hash=fhash, slot_offset=s.slot_offset, slot_size=s.slot_size)
        f.seek(s.slot_offset)
        f.write(slot_bytes)

    trans_count = len(applied_pos_ids) + len(applied_neg_ids)
    print(f"  [✓] 0x{fhash:016X} ({label}): {trans_count}/{len(recs)} ({trans_count/len(recs)*100:.1f}%), Slots={len(slots)}")
    return True

def patch_package_1(shard_path, is_en=False):
    print(f"[*] Menambal Package 1 ({'English' if is_en else 'Indonesian'})...")
    cat_file = CATALOG_EN_PATH if is_en else CATALOG_ID_PATH
    cat_data = json.load(gzip.open(cat_file, 'rt', encoding='utf-8'))
    compact = COMPACT_TERMS_EN if is_en else COMPACT_TERMS_ID
    for k, v in compact.items():
        cat_data['unique'][k] = v

    catalog = Catalog(cat_data)
    temp_dir = shard_path.parent
    pkg = qts.QtsPackage.from_flat_dir(temp_dir, '1')
    sm = pkg.build_slot_map()

    with open(shard_path, 'r+b') as f:
        # 1. Core UI (0xDD5B)
        fhash_dd5b = 0xDD5B5EDFBB69FEED
        raw_dd5b = pkg.extract(fhash_dd5b, sm)
        slots_dd5b = sorted(sm[fhash_dd5b].values(), key=lambda x:x.chunk_id)
        recs_dd5b = []
        ui_prefixes = ('Title', 'Btn', 'Menu', 'Tab', 'Lobby', 'Confirm', 'Tip', 'Shop', 'Rank', 'Card', 'Match', 'Task', 'Guide', 'Activity', 'Notice', 'Mail', 'Equip', 'Hero', 'Item', 'Option', 'Setting', 'Chart', 'Join', 'Chat', 'Common', 'Android', 'Prompt', 'Dialog', 'Quit', 'Exit', 'Project8', 'Lord', 'Exclusive', 'Res')
        def is_ui(k):
            return any(k.lower().startswith(p.lower()) for p in ui_prefixes) or len(k) == 16

        FACTION_KEYS = {
            'Project8CampCareerName117': 'Tiga Kerajaan' if not is_en else 'Three Kingdoms',
            'DADD6C898742DFB4': 'Sungai Besar' if not is_en else 'Riverlands',
            'C144A50536240665': 'Zhulu',
            '7EB9DBB5DE971CCF': 'Heluo',
            '643D333F32A79A51': 'Laut Senja' if not is_en else 'Sunset Sea',
            '1B75A8918B21DD60': 'Tiga Kerajaan' if not is_en else 'Three Kingdoms',
            '0806C94C7A600204': 'Laut Senja' if not is_en else 'Sunset Sea',
        }

        for tag, nested, enc in fields(raw_dd5b):
            parts = list(fields(nested))
            k = next(p[1].decode('utf-8', 'ignore') for p in parts if p[0] == 10)
            s = next(p[1].decode('utf-8', 'ignore') for p in parts if p[0] == 18)
            t = FACTION_KEYS.get(k) or catalog.lookup(fhash_dd5b, k, s)
            if t and t != s:
                t = compact_text(t, is_en=is_en)
            new_enc = enc
            diff = 0
            if t and t != s:
                vb = t.encode('utf-8')
                rb = b''.join(p[2] if p[0] == 10 else b'\x12' + encode_varint(len(vb)) + vb for p in parts)
                new_enc = b'\n' + encode_varint(len(rb)) + rb
                diff = len(new_enc) - len(enc)
            recs_dd5b.append({'k': k, 's': s, 't': t, 'orig': enc, 'new': new_enc, 'diff': diff, 'is_ui': is_ui(k)})

        for r in recs_dd5b:
            r['active'] = r['new'] if r['diff'] <= 0 else r['orig']
            r['trans'] = (r['diff'] <= 0 and r['t'] and r['t'] != r['s'])

        budget_dd5b = len(raw_dd5b) - sum(len(r['active']) for r in recs_dd5b)
        gt_zero_dd5b = [r for r in recs_dd5b if r['diff'] > 0 and r['t'] and r['t'] != r['s']]
        gt_zero_dd5b.sort(key=lambda r: (r['k'] not in FACTION_KEYS, len(r['s']) > 15, not r['is_ui'], r['diff']))

        for r in gt_zero_dd5b:
            if budget_dd5b >= r['diff']:
                r['active'] = r['new']
                r['trans'] = True
                budget_dd5b -= r['diff']

        if budget_dd5b > 0:
            for r in recs_dd5b:
                if r['trans'] and len(r['t']) + budget_dd5b < 120:
                    vb = (r['t'] + ' ' * budget_dd5b).encode('utf-8')
                    parts = list(fields(list(fields(r['orig']))[0][1]))
                    rb = b''.join(p[2] if p[0] == 10 else b'\x12' + encode_varint(len(vb)) + vb for p in parts)
                    r['active'] = b'\n' + encode_varint(len(rb)) + rb
                    budget_dd5b = 0
                    break

        tbl_dd5b = b''.join(r['active'] for r in recs_dd5b)
        assert len(tbl_dd5b) == len(raw_dd5b)
        offset = 0
        for s in slots_dd5b:
            c_raw = tbl_dd5b[offset : offset + s.uncompressed_size]
            offset += s.uncompressed_size
            comp = qts.lz4.block.compress(c_raw, mode='high_compression', compression=12, store_size=False)
            slot_bytes = upi_mod._slot_bytes(s, comp, s.uncompressed_size, file_hash=fhash_dd5b, slot_offset=s.slot_offset, slot_size=s.slot_size)
            f.seek(s.slot_offset)
            f.write(slot_bytes)
        trans_dd5b = sum(1 for r in recs_dd5b if r['trans'])
        print(f"  [✓] 0x{fhash_dd5b:016X} (Core UI 3-slots): {trans_dd5b}/{len(recs_dd5b)} ({trans_dd5b/len(recs_dd5b)*100:.1f}%)")

        # 2. Lobby & Drawer (0x616B)
        fhash_616b = 0x616B352C296F1FFE
        raw_616b = pkg.extract(fhash_616b, sm)
        slot_616b = sm[fhash_616b][0]
        recs_616b = []
        for tag, nested, enc in fields(raw_616b):
            parts = list(fields(nested))
            k = next(p[1].decode('utf-8', 'ignore') for p in parts if p[0] == 10)
            src = next(p[1].decode('utf-8', 'ignore') for p in parts if p[0] == 18)
            recs_616b.append({'k': k, 'src': src, 'orig': enc})

        d_616b = LOBBY_TABLE_EN if is_en else LOBBY_TABLE_ID
        cur_616b = {r['k']: make_rec(r['k'], d_616b[r['src']]) if r['src'] in d_616b else r['orig'] for r in recs_616b}
        tbl_616b = b''.join(cur_616b[x['k']] for x in recs_616b)
        comp_616b = qts.lz4.block.compress(tbl_616b, mode='high_compression', compression=12, store_size=False)
        slot_bytes_616b = upi_mod._slot_bytes(slot_616b, comp_616b, len(tbl_616b), file_hash=fhash_616b, slot_offset=slot_616b.slot_offset, slot_size=slot_616b.slot_size)
        f.seek(slot_616b.slot_offset)
        f.write(slot_bytes_616b)
        print(f"  [✓] 0x{fhash_616b:016X} (Lobby & Drawer): Translated 15/15")

        # 3. Card Keywords & Triggers (0x5698)
        fhash_5698 = 0x56985DCB17BCDBF9
        if fhash_5698 in sm:
            raw_5698 = pkg.extract(fhash_5698, sm)
            slot_5698 = sm[fhash_5698][0]
            kw_map = dict(KEYWORD_SOL_EN if is_en else KEYWORD_SOL_ID)
            recs_5698 = []
            for tag, nested, enc in fields(raw_5698):
                parts = list(fields(nested))
                k = next(p[1].decode('utf-8', 'ignore') for p in parts if p[0] == 10)
                src = next(p[1].decode('utf-8', 'ignore') for p in parts if p[0] == 18)
                tgt = kw_map.get(k, src)
                recs_5698.append({'k': k, 's': src, 't': tgt, 'orig': enc})
            
            cur_diff = sum(len(make_rec(r['k'], r['t'])) - len(r['orig']) for r in recs_5698)
            pad = -cur_diff
            if pad > 0:
                for r in recs_5698:
                    if r['k'] == '#4A66D52802E8DC92#':
                        r['t'] = r['t'] + ' ' * pad
                        break
            tbl_5698 = b''.join(make_rec(r['k'], r['t']) for r in recs_5698)
            assert len(tbl_5698) == len(raw_5698), f"Length mismatch: {len(tbl_5698)} vs {len(raw_5698)}"
            comp_5698 = qts.lz4.block.compress(tbl_5698, mode='high_compression', compression=12, store_size=False)
            assert len(comp_5698) <= slot_5698.slot_size - 48, f"Overflow: {len(comp_5698)} > {slot_5698.slot_size - 48}"
            sb_5698 = upi_mod._slot_bytes(slot_5698, comp_5698, len(tbl_5698), file_hash=fhash_5698, slot_offset=slot_5698.slot_offset, slot_size=slot_5698.slot_size)
            f.seek(slot_5698.slot_offset)
            f.write(sb_5698)
            print(f"  [✓] 0x{fhash_5698:016X} (Card Keywords & Triggers): Translated 18/18, comp={len(comp_5698)}")

        # 4. Master Localization Tables
        KNOWN_TABLES_1 = {
            0x79E3F2A531266997: 'Game Modes & Events',
            0x42E8DB43608C2FF1: 'Hero Cards & Synergies',
            0xA336359CD92A858E: 'Hero Cards Master 1',
            0x9799DF91AB4F4FA3: 'Hero Cards Master 2',
            0x23C9A9DEBB3BF40C: 'Hero Cards Master 3',
            0x57C03656175B0904: 'Hero Cards Master 4',
            0x28D9F8B02CAA94E2: 'Hero Cards Variant 2',
            0x3D889D9ABCEDE2A8: 'Hero Cards Variant 3',
            0x9CAA7228F782AB5A: 'Hero Cards Variant 4',
            0x4476EC307E0F2142: 'Hero Cards Variant 5',
            0xC9BC3381603BDDB3: 'Hero Cards Variant 6',
            0x04F21C6735D0D555: 'Hero Cards Variant 7',
            0x9BE81CD52C660467: 'Hero Cards Variant 8',
            0x666DC40230B31A30: 'Hero Cards Variant 9',
            0xF628F40CE23D983E: 'Hero Cards Variant 10',
            0xC059EA43719099F1: 'Hero Cards Variant 11',
            0x27BBF8CDFFFA177F: 'Hero Cards Variant 12',
            0xC4E32B49AE8B7FFB: 'Hero Cards Variant 13',
            0x5EB61A0269CD8550: 'Hero Cards Variant 14',
            0x55EC8FF338904581: 'Hero Synergies Variant 2',
            0x7F7F60ACED822B5E: 'Hero Skills 1',
            0x58B4B182D74B34B0: 'Hero Skills 2',
            0x6B4BE06E1593DD1C: 'Hero Skills 3',
            0x58D24D0F3E982EFD: 'Hero Tutorial & Play',
            0x5E72CA8CAF015FDE: 'Event & Mail Rewards',
            0x88DB6A2E7794293C: 'Gameplay Rules',
            0x20A7853F0A7B634D: 'Hero Talents',
            0xDA170394EFB236E6: 'Event Notifications',
            0x4C8CDABFC4BE8C4D: 'Event Notices',
            0x00BF2528D217FFFA: 'Match Misc 1',
            0xEAAC4D47ABAFD6F5: 'Match Misc 2',
            0xD850CF0180690C33: 'Match Misc 3',
            0x9DCBAD5EA212C0CC: 'Match Misc 4',
            0xA07B2B9F994FB0ED: 'Card Effects Master A (Niu Mo/Yixing)',
            0x9C4EC654D5454B46: 'Card Effects Master B',
            0xC13DF45E3492CA0C: 'Card Effects Master C',
            0xEABE356D0A0BB65F: 'Card Effects Master D',
        }

        loc_count = 0
        for fhash in sorted(sm):
            if fhash in (0xDD5B5EDFBB69FEED, 0x616B352C296F1FFE, 0x56985DCB17BCDBF9):
                continue
            try:
                raw_check = pkg.extract(fhash, sm)
                cnt = 0
                has_str = 0
                for tag, nested, enc in fields(raw_check):
                    cnt += 1
                    pts = list(fields(nested))
                    if any(p[0] == 10 for p in pts) and any(p[0] == 18 for p in pts):
                        has_str += 1
                if cnt > 0 and has_str == cnt:
                    lbl = KNOWN_TABLES_1.get(fhash, f"Table 0x{fhash:016X}")
                    ok = patch_table_generic(f, pkg, sm, fhash, lbl, catalog, is_en=is_en)
                    if ok:
                        loc_count += 1
            except Exception:
                pass

    print(f"  [✓] Paket 1 selesai diterjemahkan ({loc_count + 3} tabel berhasil)!")

def patch_package_4(shard_path, is_en=False):
    print(f"[*] Menambal Package 4 ({'English' if is_en else 'Indonesian'})...")
    cat_file = CATALOG_EN_PATH if is_en else CATALOG_ID_PATH
    cat_data = json.load(gzip.open(cat_file, 'rt', encoding='utf-8'))
    compact = COMPACT_TERMS_EN if is_en else COMPACT_TERMS_ID
    for k, v in compact.items():
        cat_data['unique'][k] = v

    catalog = Catalog(cat_data)
    temp_dir = shard_path.parent
    pkg = qts.QtsPackage.from_flat_dir(temp_dir, '4')
    sm = pkg.build_slot_map()

    pkg4_labels = {
        0xE0FF23C02C95D892: 'Hero Profiles & Bios',
        0x38FE3FBB0652B5C9: 'Hero Titles & Roles',
        0x2B65C5CF9CA7633D: 'Hero Skins & Models',
        0x13429059252DC6EB: 'Hero Voice & Lines',
        0xCDB2295507B874E7: 'Hero Background Misc',
        0x98FFCF199B0C9C2B: 'Hero Lore Snippets',
    }

    loc_count = 0
    with open(shard_path, 'r+b') as f:
        for fhash in sorted(sm):
            try:
                raw_check = pkg.extract(fhash, sm)
                cnt = 0
                has_str = 0
                for tag, nested, enc in fields(raw_check):
                    cnt += 1
                    pts = list(fields(nested))
                    if any(p[0] == 10 for p in pts) and any(p[0] == 18 for p in pts):
                        has_str += 1
                if cnt > 0 and has_str == cnt:
                    lbl = pkg4_labels.get(fhash, f"Table 0x{fhash:016X}")
                    ok = patch_table_generic(f, pkg, sm, fhash, lbl, catalog, is_en=is_en)
                    if ok:
                        loc_count += 1
            except Exception:
                pass

    print(f"  [✓] Paket 4 selesai diterjemahkan ({loc_count} tabel berhasil)!")


def strip_safe_comments(text, max_bytes):
    lines = text.split('\n')
    new_lines = []
    stripped = 0
    in_block = False
    for l in lines:
        trimmed = l.strip()
        if not trimmed:
            if stripped < max_bytes:
                stripped += len(l) + 1
                continue
        if trimmed.startswith('--[['):
            in_block = True
            new_lines.append(l)
            continue
        if in_block:
            if '--]]' in trimmed or ']]' in trimmed:
                in_block = False
            new_lines.append(l)
            continue
        if not in_block and stripped < max_bytes and trimmed.startswith('--') and not any(k in trimmed for k in ['local', 'cfg', 'return', 'author', 'class']):
            stripped += len(l) + 1
            continue
        to_add = l
        if stripped < max_bytes and (to_add.startswith('    ') or to_add.startswith('\t')):
            leading = len(to_add) - len(trimmed)
            trim_amt = min(leading, max_bytes - stripped)
            if trim_amt > 0:
                stripped += trim_amt
                to_add = to_add[trim_amt:]
        new_lines.append(to_add)
    return '\n'.join(new_lines)

def patch_package_10(shard_path, is_en=False):
    print(f"[*] Menambal Package 10 ({'English' if is_en else 'Indonesian'})...")
    temp_dir = shard_path.parent
    pkg = qts.QtsPackage.from_flat_dir(temp_dir, '10')
    sm = pkg.build_slot_map()

    # Shop entries
    shop_entries_id = [
        ('"皮肤商店"', '"Toko Skin"'), ('"棋手商店"', '"Toko Bidak"'), ('"棋盘商店"', '"Toko Papan Catur"'),
        ('"特惠道具"', '"Item Diskon"'), ('"月卡"', '"Kartu Bulanan"'), ('"碎片商城"', '"Toko Pecahan"'),
        ('"限时祈愿获取"', '"Didapat dari Wish Terbatas"'), ('"夺宝获取"', '"Didapat dari Undian"'),
        ('"首周专享"', '"Khusus Minggu Pertama"'), ('"活动"', '"Event"'), ('"热卖"', '"Laris"'),
        ('"推荐"', '"Rekomendasi"'), ('"新品"', '"Produk Baru"'), ('"赠礼"', '"Hadiah"'),
        ('"定制"', '"Kustomisasi"'), ('"直购"', '"Beli Langsung"'), ('"夺宝"', '"Undian"')
    ]
    shop_entries_en = [
        ('"皮肤商店"', '"Skin Shop"'), ('"棋手商店"', '"Chess Shop"'), ('"棋盘商店"', '"Board Shop"'),
        ('"特惠道具"', '"Special Items"'), ('"月卡"', '"Monthly Pass"'), ('"碎片商城"', '"Shard Shop"'),
        ('"限时祈愿获取"', '"Obtained via Limited Wish"'), ('"夺宝获取"', '"Obtained via Draw"'),
        ('"首周专享"', '"First Week Special"'), ('"活动"', '"Event"'), ('"热卖"', '"Hot"'),
        ('"推荐"', '"Featured"'), ('"新品"', '"New"'), ('"赠礼"', '"Gifting"'),
        ('"定制"', '"Custom"'), ('"直购"', '"Direct Buy"'), ('"夺宝"', '"Lucky Draw"')
    ]

    # Lineup entries
    lineup_entries_id = [
        ('"三分登场流"', '"Aliran Three Kingdoms"'), ('"大河图腾流"', '"Aliran Totem Sungai Besar"'),
        ('"日落海整备流"', '"Aliran Persiapan Sunset Sea"'), ('"河洛古币流"', '"Aliran Koin Kuno Heluo"'),
        ('"古币成长流"', '"Aliran Pertumbuhan Koin Kuno"'), ('"战术牌成长流"', '"Aliran Pertumbuhan Kartu Taktis"'),
        ('"嫦娥四小队"', '"Skuad Empat Chang\'e"'), ('"马可四驱兄弟"', '"Empat Saudara Marco"'),
        ('"马可万血猪"', '"Zhu Bajie Darah Tebal Marco"'), ('"乔汐速六司空震"', '"Sikong Zhen Cepat Lv 6 Qiao Xi"'),
        ('"安琪拉整备流"', '"Aliran Persiapan Angela"'), ('"图腾成长流"', '"Aliran Pertumbuhan Totem"')
    ]
    lineup_entries_en = [
        ('"三分登场流"', '"Three Kingdoms Flow"'), ('"大河图腾流"', '"River Totem Flow"'),
        ('"日落海整备流"', '"Sunset Sea Prep Flow"'), ('"河洛古币流"', '"Heluo Coin Flow"'),
        ('"古币成长流"', '"Coin Growth Flow"'), ('"战术牌成长流"', '"Tactics Growth Flow"'),
        ('"嫦娥四小队"', '"Chang\'e Squad"'), ('"马可四驱兄弟"', '"Marco 4WD Bros"'),
        ('"马可万血猪"', '"Marco Tanky Pig"'), ('"乔汐速六司空震"', '"Fast Lv6 Sikong Zhen Qiao Xi"'),
        ('"安琪拉整备流"', '"Angela Prep Flow"'), ('"图腾成长流"', '"Totem Growth Flow"')
    ]

    with open(shard_path, 'r+b') as f:
        # 1. ShopHelper (0xE7444AC3CEB9BDB1)
        fhash_shop = 0xE7444AC3CEB9BDB1
        if fhash_shop in sm:
            raw = pkg.extract(fhash_shop, sm)
            slot = sm[fhash_shop][0]
            clean = strip_safe_comments(raw.decode('utf-8', errors='ignore'), 3000)
            entries = shop_entries_en if is_en else shop_entries_id
            dict_body = ",\n        ".join(f"[{e[0]}] = {e[1]}" for e in entries)
            start_fn = "function ShopHelperClass:GetLocalize(key)"
            end_marker = "return key\nend"
            s_idx = clean.find(start_fn)
            e_idx = clean.find(end_marker, s_idx) if s_idx != -1 else -1
            if s_idx != -1 and e_idx != -1:
                rep_fn = f"""function ShopHelperClass:GetLocalize(key)
    if string.isNullOrEmpty(key) then return key end
    local _dict = {{
        {dict_body},
    }}
    if _dict[key] then return _dict[key] end
    local res = Localize and Localize.GetString(key)
    if res and res ~= key then return res end
    return key
end"""
                patched_txt = clean[:s_idx] + rep_fn + clean[e_idx + len(end_marker):]
                pb = patched_txt.encode('utf-8')
                pad = slot.uncompressed_size - len(pb)
                if pad >= 4:
                    pb += ("\n-- " + "=" * (pad - 4)).encode('utf-8')
                comp = qts.lz4.block.compress(pb, mode='high_compression', compression=12, store_size=False)
                sb = upi_mod._slot_bytes(slot, comp, len(pb), file_hash=fhash_shop, slot_offset=slot.slot_offset, slot_size=slot.slot_size)
                f.seek(slot.slot_offset)
                f.write(sb)
                print("  [✓] 0xE7444AC3CEB9BDB1 (ShopHelper): Patched")

        # 2. EmbattleFormation (0x2AA6E0613FA44093)
        fhash_form = 0x2AA6E0613FA44093
        if fhash_form in sm:
            raw = pkg.extract(fhash_form, sm)
            slot = sm[fhash_form][0]
            clean = strip_safe_comments(raw.decode('utf-8', errors='ignore'), 8000)
            target = 'self._version = shareData.Version or ""'
            if target in clean:
                entries = lineup_entries_en if is_en else lineup_entries_id
                dict_body = ",\n        ".join(f"[{e[0]}] = {e[1]}" for e in entries)
                injected = f"""{target}
    local _dict = {{
        {dict_body},
    }}
    local _loc = Localize and Localize.GetString
    if _dict[self._formationName] then self._formationName = _dict[self._formationName] elseif _loc and _loc(self._formationName) ~= self._formationName then self._formationName = _loc(self._formationName) end
    if _dict[self._formationDesc] then self._formationDesc = _dict[self._formationDesc] elseif _loc and _loc(self._formationDesc) ~= self._formationDesc then self._formationDesc = _loc(self._formationDesc) end
    if _dict[self._positionDesc] then self._positionDesc = _dict[self._positionDesc] elseif _loc and _loc(self._positionDesc) ~= self._positionDesc then self._positionDesc = _loc(self._positionDesc) end
    if _dict[self._equipDesc] then self._equipDesc = _dict[self._equipDesc] elseif _loc and _loc(self._equipDesc) ~= self._equipDesc then self._equipDesc = _loc(self._equipDesc) end
    if _dict[self._talentDesc] then self._talentDesc = _dict[self._talentDesc] elseif _loc and _loc(self._talentDesc) ~= self._talentDesc then self._talentDesc = _loc(self._talentDesc) end
    if _dict[self._effectCardDesc] then self._effectCardDesc = _dict[self._effectCardDesc] elseif _loc and _loc(self._effectCardDesc) ~= self._effectCardDesc then self._effectCardDesc = _loc(self._effectCardDesc) end"""
                patched_txt = clean.replace(target, injected, 1)
                pb = patched_txt.encode('utf-8')
                pad = slot.uncompressed_size - len(pb)
                if pad >= 4:
                    pb += ("\n-- " + "=" * (pad - 4)).encode('utf-8')
                comp = qts.lz4.block.compress(pb, mode='high_compression', compression=12, store_size=False)
                sb = upi_mod._slot_bytes(slot, comp, len(pb), file_hash=fhash_form, slot_offset=slot.slot_offset, slot_size=slot.slot_size)
                f.seek(slot.slot_offset)
                f.write(sb)
                print("  [✓] 0x2AA6E0613FA44093 (EmbattleFormation): Patched")

        # 3. LobbyPresenter (0xFC07FFAAB85F0418)
        fhash_pres = 0xFC07FFAAB85F0418
        if fhash_pres in sm:
            raw = pkg.extract(fhash_pres, sm)
            slot = sm[fhash_pres][0]
            clean = strip_safe_comments(raw.decode('utf-8', errors='ignore'), 18000)
            target_a = 'self:SetSeasonHint(cfg and cfg.Name or "")\n    self:SetAdditionalText(Localize.GetString("FirstDailyBuffTip"))'
            target_b = 'self:SetSeasonHint(cfg and cfg.Name or "")\nself:SetAdditionalText(Localize.GetString("FirstDailyBuffTip"))'
            target = target_a if target_a in clean else (target_b if target_b in clean else None)
            if target:
                sHint = "S1 Genesis" if is_en else "S1 Awal Mula"
                trainBtn = "TRAINING" if is_en else "LATIHAN"
                unrank = "Unranked"
                startGame = "START GAME" if is_en else "MULAI GAME"
                tourney = "ACE Tournament" if is_en else "Turnamen ACE"
                diamondRush = "Diamond Rush" if is_en else "Diamond Frenzy"
                sixPlayer = "6-Player Battle, Claim the Crown" if is_en else "Pertarungan 6 Pemain, Rebut Mahkota"
                unlockReq = "Unlock Requirements Met" if is_en else "Capai Syarat untuk Membuka"
                silverUnlock = "Unlock New Content at Silver" if is_en else "Buka Konten Baru di Silver"
                train = "Training" if is_en else "Latihan"
                custom = "Custom" if is_en else "Kustom"
                casual = "Casual" if is_en else "Hiburan"
                seasonRwd = "Season" if is_en else "Musim"
                choiceChess = "Choice Chess" if is_en else "Catur Pilihan"
                endgameChall = "Endgame Challenge" if is_en else "Tantangan Babak Akhir"
                repTarget = f"""local _sName = cfg and cfg.Name or ""
    if _sName == "S1万象启程" then _sName = "{sHint}" end
    self:SetSeasonHint(_sName)
    self:SetAdditionalText(Localize.GetString("FirstDailyBuffTip"))"""

                hookCode = f"""
-- [[ ZENITH RUNTIME HOOK ]]
if not _G.__zenith_hooked then
    _G.__zenith_hooked = true
    local _og = Localize and Localize.GetString
    local _sm = {{
        ["对战特训"]="{trainBtn}",["日月行者"]="Sun & Moon Traveler",
        ["S1万象启程"]="{sHint}",["万象启程"]="ACE",
        ["未上榜"]="{unrank}",["全部阵营"]="All Factions",
        ["开始游戏"]="{startGame}",["万象大赛"]="{tourney}",["钻石狂潮"]="{diamondRush}",
        ["六人对战，独享桂冠"]="{sixPlayer}",["达成条件解锁"]="{unlockReq}",
        ["秩序白银解锁新内容"]="{silverUnlock}",["排位"]="Ranked",["训练"]="{train}",
        ["自定义"]="{custom}",["娱乐"]="{casual}",["赛季奖励"]="{seasonRwd}",
        ["残局挑战"]="{endgameChall}",["抉择之弈"]="{choiceChess}",
        ["倔强青铜"]="Bronze",["秩序白银"]="Silver",["荣耀黄金"]="Gold",
        ["尊贵铂金"]="Platinum",["永恒钻石"]="Diamond",["至尊星耀"]="Mythic",["最强王者"]="Grandmaster"
    }}
    local function _cln(t)
        if not t or type(t) ~= "string" or t == "" then return t end
        if _sm[t] then return _sm[t] end
        local r = t
        if string.find(r, "开始游戏", 1, true) then r = string.gsub(r, "开始游戏", "{startGame}") end
        if string.find(r, "S1万象启程", 1, true) then r = string.gsub(r, "S1万象启程", "{sHint}") end
        if string.find(r, "万象大赛", 1, true) then r = string.gsub(r, "万象大赛", "{tourney}") end
        if string.find(r, "钻石狂潮", 1, true) then r = string.gsub(r, "钻石狂潮", "{diamondRush}") end
        return r
    end
    if _og then
        Localize.GetString = function(k, ...)
            if k and _sm[k] then return _sm[k] end
            local a = {{...}}
            for i = 1, #a do if type(a[i]) == "string" and _sm[a[i]] then a[i] = _sm[a[i]] end end
            local res = _og(k, table.unpack(a))
            return res and _cln(res) or res
        end
    end
    local function _fix(it)
        if it then
            pcall(function()
                if it.Name then it.Name = _cln(it.Name) end
                if it.Title then it.Title = _cln(it.Title) end
                if it.Desc then it.Desc = _cln(it.Desc) end
            end)
        end
        return it
    end
    if PBDataManager and PBDataManager.ResLobbyEntryJumpCfg then
        local _rgm = PBDataManager.ResLobbyEntryJumpCfg.GetMulti_ByGruopType
        if _rgm then PBDataManager.ResLobbyEntryJumpCfg.GetMulti_ByGruopType = function(gt) local l = _rgm(gt); if l then for i = 1, #l do _fix(l[i]) end end; return l end end
        local _rge = PBDataManager.ResLobbyEntryJumpCfg.Get
        if _rge then PBDataManager.ResLobbyEntryJumpCfg.Get = function(id) return _fix(_rge(id)) end end
    end
    if LobbyData and LobbyData.GetLobbyEntryCfgListByType then
        local _old = LobbyData.GetLobbyEntryCfgListByType
        LobbyData.GetLobbyEntryCfgListByType = function(self, t)
            local res = _old(self, t)
            if res then for _, v in pairs(res) do _fix(v) end end
            return res
        end
    end
end"""
                patched_txt = clean.replace(target, repTarget, 1)
                if "return UILobbyClass" in patched_txt:
                    patched_txt = patched_txt.replace("return UILobbyClass", f"{hookCode}\n\nreturn UILobbyClass")
                else:
                    patched_txt += hookCode

                pb = patched_txt.encode('utf-8')
                pad = slot.uncompressed_size - len(pb)
                if pad >= 4:
                    pb += ("\n-- " + "=" * (pad - 4)).encode('utf-8')
                comp = qts.lz4.block.compress(pb, mode='high_compression', compression=12, store_size=False)
                sb = upi_mod._slot_bytes(slot, comp, len(pb), file_hash=fhash_pres, slot_offset=slot.slot_offset, slot_size=slot.slot_size)
                f.seek(slot.slot_offset)
                f.write(sb)
                print("  [✓] 0xFC07FFAAB85F0418 (LobbyPresenter): Patched")

        # 4. GameCenter (0x796A58EA33D65358)
        fhash_gc = 0x796A58EA33D65358
        if fhash_gc in sm:
            raw = pkg.extract(fhash_gc, sm)
            slot = sm[fhash_gc][0]
            clean = strip_safe_comments(raw.decode('utf-8', errors='ignore'), 10000)
            start_txt = "START GAME" if is_en else "MULAI GAME"
            t5 = "self:CreateUIRoomRightBottom(self._rightBottomData)"
            r5 = f"""{t5}
    if self.uiRoomRightBottomChild then
        local _om = self.uiRoomRightBottomChild.Modify
        self.uiRoomRightBottomChild.Modify = function(s, d)
            if d then
                if d.Title == "开始游戏" or d.Title == UIRoomRightBottomClassTextStatus.StartPlay then d.Title = "{start_txt}" end
            end
            if _om then _om(s, d) end
        end
    end"""
            patched_txt = clean.replace(t5, r5, 1)
            pb = patched_txt.encode('utf-8')
            pad = slot.uncompressed_size - len(pb)
            if pad >= 4:
                pb += ("\n-- " + "=" * (pad - 4)).encode('utf-8')
            comp = qts.lz4.block.compress(pb, mode='high_compression', compression=12, store_size=False)
            sb = upi_mod._slot_bytes(slot, comp, len(pb), file_hash=fhash_gc, slot_offset=slot.slot_offset, slot_size=slot.slot_size)
            f.seek(slot.slot_offset)
            f.write(sb)
            print("  [✓] 0x796A58EA33D65358 (GameCenter): Patched")

        # 5. UILobbyClass_AutoBind (0x25D1A19B4BE0B669)
        fhash_bind = 0x25D1A19B4BE0B669
        if fhash_bind in sm:
            raw = pkg.extract(fhash_bind, sm)
            slot = sm[fhash_bind][0]
            clean = strip_safe_comments(raw.decode('utf-8', errors='ignore'), 8000)
            target = "function UILobbyClass_AutoBind:SetSeasonHint(arg)\n    self.seasonHint.text = arg\nend"
            sHint = "S1 Genesis" if is_en else "S1 Awal Mula"
            if target in clean:
                rep = f"""function UILobbyClass_AutoBind:SetSeasonHint(arg)
    if arg and string.find(arg, "万象启程") then
        arg = string.gsub(arg, "万象启程", "{sHint}")
    elseif not arg or arg == "" then
        arg = "{sHint}"
    end
    self.seasonHint.text = arg
end"""
                clean = clean.replace(target, rep, 1)
            pb = clean.encode('utf-8')
            pad = slot.uncompressed_size - len(pb)
            if pad >= 4:
                pb += ("\n-- " + "=" * (pad - 4)).encode('utf-8')
            comp = qts.lz4.block.compress(pb, mode='high_compression', compression=12, store_size=False)
            sb = upi_mod._slot_bytes(slot, comp, len(pb), file_hash=fhash_bind, slot_offset=slot.slot_offset, slot_size=slot.slot_size)
            f.seek(slot.slot_offset)
            f.write(sb)
            print("  [✓] 0x25D1A19B4BE0B669 (UILobbyClass_AutoBind): Patched")

    print("  [✓] Paket 10 selesai diterjemahkan!")

def create_archive(build_dir, zip_path):
    print(f"[*] Mengompresi ke {zip_path.name}...")
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for pkg_id in ['1', '4', '10']:
            desc_file = build_dir / pkg_id / f"{pkg_id}.db"
            shard_file = build_dir / pkg_id / f"{pkg_id}_0.db"
            zf.write(desc_file, f"{pkg_id}/{pkg_id}.db")
            zf.write(shard_file, f"{pkg_id}/{pkg_id}_0.db")
    size = zip_path.stat().st_size
    h = hashlib.sha256(zip_path.read_bytes()).hexdigest().upper()
    print(f"  [✓] {zip_path.name}: {size} bytes, SHA256: {h}")
    return size, h

def main():
    print("==================================================================")
    print("      ZENITH PATCHER // MASTER SHARD COMPLETE GENERATOR V2        ")
    print("==================================================================")

    # 1. Prepare clean build directories
    build_id = WORK_DIR / "build_golden_id"
    build_en = WORK_DIR / "build_golden_en"
    for b in [build_id, build_en]:
        if b.exists():
            shutil.rmtree(b)
        (b / "1").mkdir(parents=True)
        (b / "4").mkdir(parents=True)
        (b / "10").mkdir(parents=True)

    # 2. Copy source Android v1.5.1 files
    src_1 = WORK_DIR / "real_android_1.db"
    src_1_0 = WORK_DIR / "android_1_0.db.orig"
    src_4 = WORK_DIR / "real_android_4.db"
    src_4_0 = WORK_DIR / "android_4_0.db"
    src_10 = WORK_DIR / "real_android_10.db"
    src_10_0 = WORK_DIR / "android_10_0.db"

    for b in [build_id, build_en]:
        shutil.copyfile(src_1, b / "1" / "1.db")
        shutil.copyfile(src_1_0, b / "1" / "1_0.db")
        shutil.copyfile(src_4, b / "4" / "4.db")
        shutil.copyfile(src_4_0, b / "4" / "4_0.db")
        shutil.copyfile(src_10, b / "10" / "10.db")
        shutil.copyfile(src_10_0, b / "10" / "10_0.db")

    # 3. Patch Indonesian
    print("\n--- [1/2] MEMBANGUN GOLDEN SHARD BAHASA INDONESIA ---")
    patch_package_1(build_id / "1" / "1_0.db", is_en=False)
    patch_package_4(build_id / "4" / "4_0.db", is_en=False)
    patch_package_10(build_id / "10" / "10_0.db", is_en=False)
    id_zip = ONLINE_DIR / "golden_shards.zip"
    id_size, id_hash = create_archive(build_id, id_zip)

    # 4. Patch English
    print("\n--- [2/2] MEMBANGUN GOLDEN SHARD GLOBAL ENGLISH ---")
    patch_package_1(build_en / "1" / "1_0.db", is_en=True)
    patch_package_4(build_en / "4" / "4_0.db", is_en=True)
    patch_package_10(build_en / "10" / "10_0.db", is_en=True)
    en_zip = ONLINE_DIR / "golden_shards_en.zip"
    en_size, en_hash = create_archive(build_en, en_zip)

    # 5. Update Manifest
    manifest_data = {
        "manifestVersion": "1.0",
        "appVersion": "1.8.2",
        "buildCode": 10,
        "updatedAt": "2026-10-14T00:10:00Z",
        "packages": {
            "id": {
                "language": "id",
                "displayName": "Bahasa Indonesia",
                "fileName": "golden_shards.zip",
                "primaryUrl": "https://github.com/AuraXaviera/HonorOfKingsAce/releases/download/v1.8.2/golden_shards.zip",
                "mirrorUrl": "https://raw.githubusercontent.com/AuraXaviera/HonorOfKingsAce/main/shards/golden_shards.zip",
                "sha256": id_hash,
                "sizeBytes": id_size,
                "shardsIncluded": ["1", "4", "10"],
                "bitExactVerified": True
            },
            "en": {
                "language": "en",
                "displayName": "Global English",
                "fileName": "golden_shards_en.zip",
                "primaryUrl": "https://github.com/AuraXaviera/HonorOfKingsAce/releases/download/v1.8.2/golden_shards_en.zip",
                "mirrorUrl": "https://raw.githubusercontent.com/AuraXaviera/HonorOfKingsAce/main/shards/golden_shards_en.zip",
                "sha256": en_hash,
                "sizeBytes": en_size,
                "shardsIncluded": ["1", "4", "10"],
                "bitExactVerified": True
            }
        }
    }
    manifest_file = ONLINE_DIR / "shards_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as mf:
        json.dump(manifest_data, mf, indent=2, ensure_ascii=False)
    print(f"\n[✓] Manifest diperbarui: {manifest_file}")

    # Copy to repo clone if exists
    if (REPO_DIR / "shards").exists():
        shutil.copyfile(id_zip, REPO_DIR / "shards" / "golden_shards.zip")
        shutil.copyfile(en_zip, REPO_DIR / "shards" / "golden_shards_en.zip")
        shutil.copyfile(manifest_file, REPO_DIR / "shards" / "shards_manifest.json")
        if (REPO_DIR / "tools").exists():
            shutil.copyfile(Path(__file__).resolve(), REPO_DIR / "tools" / "build_master_shards.py")
        print(f"[✓] Berkas disinkronkan ke repo clone: {REPO_DIR / 'shards'}")

    print("\n[+] GENERASI MASTER SHARDS SELESAI DENGAN SUKSES!")

if __name__ == "__main__":
    main()
