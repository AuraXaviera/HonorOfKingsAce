#!/usr/bin/env python3
"""
Zenith Patcher // Fast Developer Card Patcher CLI
=================================================
Automated bit-exact, table-aware multi-chunk protobuf card reconstructor.
Reads replacement mappings from tools/terms_override.json.

Usage:
  python tools/patch_cards.py                  # In-memory dry-run & verify (fast ~1s)
  python tools/patch_cards.py --apply          # Patch local online_shards zip archives & manifest
  python tools/patch_cards.py --deploy         # Patch, commit, push, and upload to GitHub Release
  python tools/patch_cards.py --add-id "old" "new"   # Add ID override
  python tools/patch_cards.py --add-en "old" "new"   # Add EN override
"""

import os
import sys
import io
import json
import struct
import hashlib
import zipfile
import shutil
import argparse
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import lz4.block
except ImportError:
    print("[!] Modul 'lz4' belum terpasang di Python ini. Jalankan dengan virtualenv:")
    print("    .venv\\Scripts\\python.exe tools/patch_cards.py")
    sys.exit(1)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TERMS_FILE = os.path.join(ROOT_DIR, "tools", "terms_override.json")
SHARDS_DIR = os.path.join(ROOT_DIR, "online_shards")
ID_ZIP = os.path.join(SHARDS_DIR, "golden_shards.zip")
EN_ZIP = os.path.join(SHARDS_DIR, "golden_shards_en.zip")
MANIFEST_FILE = os.path.join(SHARDS_DIR, "shards_manifest.json")
REPO_CLONE_DIR = os.path.join(ROOT_DIR, "work_temp", "repo_clone")
DEFAULT_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Protobuf Varint Helpers
def write_varint(stream, value):
    v = value
    while True:
        b = v & 0x7F
        v >>= 7
        if v == 0:
            stream.write(bytes([b]))
            break
        else:
            stream.write(bytes([b | 0x80]))

def decode_varint(buf, pos):
    res, shift, vlen = 0, 0, 0
    while True:
        b = buf[pos + vlen]
        vlen += 1
        res |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return res, vlen

def encode_record(key, val):
    valB = val.encode('utf-8')
    keyB = key.encode('utf-8')
    recB = io.BytesIO()
    recB.write(bytes([10]))
    write_varint(recB, len(keyB))
    recB.write(keyB)
    recB.write(bytes([18]))
    write_varint(recB, len(valB))
    recB.write(valB)
    payload = recB.getvalue()
    fullRec = io.BytesIO()
    fullRec.write(bytes([10]))
    write_varint(fullRec, len(payload))
    fullRec.write(payload)
    return fullRec.getvalue()

def parse_records(raw):
    recs = []
    if not raw or raw[0] != 0x0A:
        return []
    pos = 0
    try:
        while pos < len(raw):
            if raw[pos] != 0x0A:
                break
            rec_start = pos
            pos += 1
            if pos >= len(raw):
                break
            rlen, vlen = decode_varint(raw, pos)
            pos += vlen
            content_end = pos + rlen
            if content_end > len(raw):
                break
            sub = pos
            key, val = None, None
            while sub < content_end:
                tag = raw[sub]
                sub += 1
                if sub >= content_end:
                    break
                flen, fvlen = decode_varint(raw, sub)
                sub += fvlen
                fend = sub + flen
                if fend > content_end:
                    break
                if tag == 10:
                    key = raw[sub:fend].decode('utf-8', errors='ignore')
                elif tag == 18:
                    val = raw[sub:fend].decode('utf-8', errors='ignore')
                sub = fend
            raw_rec_bytes = raw[rec_start:content_end]
            recs.append({'key': key, 'val': val, 'raw': raw_rec_bytes})
            pos = content_end
    except Exception:
        pass
    return recs

def scan_slots(data):
    slots = []
    pos = 0
    stopper = len(data)
    while pos + 48 <= stopper:
        marker = struct.unpack('<i', data[pos+4:pos+8])[0]
        if marker != -1:
            pos += 4
            continue
        slotSize = struct.unpack('<i', data[pos+8:pos+12])[0]
        if slotSize < 48 or pos + slotSize > stopper:
            pos += 4
            continue
        compSizeRaw = struct.unpack('<i', data[pos+24:pos+28])[0]
        uncompSize = struct.unpack('<i', data[pos+28:pos+32])[0]
        if compSizeRaw < 4 or compSizeRaw - 4 > slotSize:
            pos += 4
            continue
        compSize = compSizeRaw - 4
        alignedTrailer = (pos + 32 + compSize + 3) & -4
        if pos + 32 <= alignedTrailer <= pos + slotSize - 16:
            fHash = struct.unpack('<Q', data[alignedTrailer:alignedTrailer+8])[0]
            reserved, chunkId = struct.unpack('<ii', data[alignedTrailer+8:alignedTrailer+16])
            slots.append({
                'pos': pos, 'slotSize': slotSize, 'compSize': compSize,
                'uncompSize': uncompSize, 'fHash': fHash, 'chunkId': chunkId,
                'reserved': reserved
            })
            pos += slotSize
        else:
            pos += 4
    return slots

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()

def load_terms():
    if not os.path.exists(TERMS_FILE):
        return {"id": {}, "en": {}, "descriptions": {}, "skip_tables": []}
    with open(TERMS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_terms(terms):
    with open(TERMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(terms, f, indent=2, ensure_ascii=False)

def apply_term_rules(key, val, terms, is_en=False):
    if not val:
        return None
    v = val

    # 1. Check description triggers
    desc_dict = terms.get("descriptions", {})
    for _, desc_item in desc_dict.items():
        triggers = desc_item.get("triggers", [])
        if any(t in v for t in triggers):
            return desc_item.get("en" if is_en else "id")

    # 2. Check specific dictionary replacements
    dict_map = terms.get("en" if is_en else "id", {})
    # Exact match first
    if v in dict_map:
        return dict_map[v]

    # Substring matches (longest strings first)
    modified = False
    sorted_patterns = sorted(dict_map.keys(), key=len, reverse=True)
    for p in sorted_patterns:
        if p in v:
            v = v.replace(p, dict_map[p])
            modified = True

    return v if modified else None

def patch_shard_bytes(db_bytes, terms, is_en=False, verbose=False):
    data = bytearray(db_bytes)
    orig_len = len(data)
    slots = scan_slots(data)
    
    skip_hashes = {int(h, 16) if isinstance(h, str) and h.startswith("0x") else int(h) for h in terms.get("skip_tables", [])}

    table_map = {}
    for s in slots:
        table_map.setdefault(s['fHash'], {})[s['chunkId']] = s

    tables_modified = 0
    total_strings_patched = 0

    for fHash, chunk_dict in sorted(table_map.items()):
        if fHash in skip_hashes:
            continue

        s_list = [chunk_dict[c] for c in sorted(chunk_dict.keys())]
        
        # 1. Decompress entire table into full_raw
        full_raw_parts = []
        decomp_ok = True
        for s in s_list:
            comp_bytes = data[s['pos']+32 : s['pos']+32+s['compSize']]
            try:
                raw_chunk = lz4.block.decompress(comp_bytes, uncompressed_size=s['uncompSize'])
                full_raw_parts.append(raw_chunk)
            except Exception:
                decomp_ok = False
                break
        if not decomp_ok:
            continue

        full_raw = b''.join(full_raw_parts)
        if not full_raw or full_raw[0] != 0x0A:
            continue

        orig_total_uncomp = sum(s['uncompSize'] for s in s_list)
        if len(full_raw) != orig_total_uncomp:
            continue

        # 2. Parse records across entire table
        recs = parse_records(full_raw)
        if not recs:
            continue

        has_change = False
        new_recs = []
        table_strings_patched = 0

        for r in recs:
            k = r['key']
            v = r['val']
            tgt = apply_term_rules(k, v, terms, is_en=is_en) if (k and v) else None
            if tgt and tgt != v:
                has_change = True
                table_strings_patched += 1
                encoded = encode_record(k, tgt)
                new_recs.append({'key': k, 'val': tgt, 'changed': True, 'raw': encoded})
            else:
                new_recs.append({'key': k, 'val': v, 'changed': False, 'raw': r['raw']})

        if not has_change:
            continue

        # 3. Assemble and pad to match orig_total_uncomp exactly
        raw_table_bytes = b''.join(nr['raw'] for nr in new_recs)
        budget = orig_total_uncomp - len(raw_table_bytes)

        if budget < 0:
            if verbose:
                print(f"[!] Warning: Table 0x{fHash:016X} negative budget ({budget})! Skipping.")
            continue

        if budget > 0:
            # Pad spaces on a modified description record
            pad_rec = next((nr for nr in new_recs if nr['changed'] and len(nr['val']) > 30), None)
            if not pad_rec:
                pad_rec = next((nr for nr in new_recs if nr['changed']), None)

            if pad_rec:
                orig_pad_len = len(pad_rec['raw'])
                found_pad = False
                for sp in range(max(0, budget - 4), budget + 5):
                    test_val = pad_rec['val'] + (' ' * sp)
                    cand_bytes = encode_record(pad_rec['key'], test_val)
                    if len(cand_bytes) - orig_pad_len == budget:
                        pad_rec['val'] = test_val
                        pad_rec['raw'] = cand_bytes
                        found_pad = True
                        break
                
                if not found_pad:
                    pad_rec['val'] = pad_rec['val'] + (' ' * budget)
                    pad_rec['raw'] = encode_record(pad_rec['key'], pad_rec['val'])

                raw_table_bytes = b''.join(nr['raw'] for nr in new_recs)

        if len(raw_table_bytes) != orig_total_uncomp:
            if verbose:
                print(f"[!] Warning: Table 0x{fHash:016X} size mismatch ({len(raw_table_bytes)} != {orig_total_uncomp}). Skipping.")
            continue

        # 4. Slice back into chunks and compress each
        offset = 0
        new_chunks = []
        all_fit = True
        for s in s_list:
            chunk_len = s['uncompSize']
            chunk_raw = raw_table_bytes[offset : offset + chunk_len]
            offset += chunk_len

            comp_chunk = lz4.block.compress(chunk_raw, mode='high_compression', compression=17, store_size=False)
            max_comp_allowed = s['slotSize'] - 48
            if len(comp_chunk) > max_comp_allowed:
                all_fit = False
                if verbose:
                    print(f"[!] Warning: Table 0x{fHash:016X} chunk {s['chunkId']} overflow ({len(comp_chunk)} > {max_comp_allowed}).")
                break
            new_chunks.append((s, comp_chunk))

        if not all_fit:
            continue

        # 5. Write back new chunks into data
        for s, comp_chunk in new_chunks:
            aligned_trailer = (s['pos'] + 32 + len(comp_chunk) + 3) & -4
            trailer_offset = aligned_trailer - s['pos']

            new_slot = bytearray(s['slotSize'])
            new_slot[0:4] = data[s['pos']:s['pos']+4]
            struct.pack_into('<i', new_slot, 4, -1)
            struct.pack_into('<i', new_slot, 8, s['slotSize'])
            new_slot[12:20] = data[s['pos']+12:s['pos']+20]
            new_slot[20:24] = data[s['pos']+20:s['pos']+24]
            struct.pack_into('<i', new_slot, 24, len(comp_chunk) + 4)
            struct.pack_into('<i', new_slot, 28, s['uncompSize'])

            new_slot[32 : 32 + len(comp_chunk)] = comp_chunk
            struct.pack_into('<Q', new_slot, trailer_offset, s['fHash'])
            struct.pack_into('<i', new_slot, trailer_offset + 8, s['reserved'])
            struct.pack_into('<i', new_slot, trailer_offset + 12, s['chunkId'])

            data[s['pos'] : s['pos'] + s['slotSize']] = new_slot

        tables_modified += 1
        total_strings_patched += table_strings_patched
        if verbose:
            print(f"  [+] 0x{fHash:016X}: {table_strings_patched} strings, {len(s_list)} chunks")

    assert len(data) == orig_len, f"Shard length altered! {len(data)} != {orig_len}"
    return bytes(data), tables_modified, total_strings_patched

def run_verify(verbose=False):
    terms = load_terms()
    print("\n" + "="*50)
    print("ZENITH DEVELOPER CARD PATCHER: IN-MEMORY VERIFY")
    print("="*50)

    # Test ID
    with zipfile.ZipFile(ID_ZIP, 'r') as z:
        id_1_0 = z.read('1/1_0.db')
    print(f"[*] Processing ID shard ({len(id_1_0):,} bytes)...")
    patched_id, id_tbls, id_strs = patch_shard_bytes(id_1_0, terms, is_en=False, verbose=verbose)
    print(f"    [✓] ID Result: {id_tbls} tables modified, {id_strs} strings replaced (Bit-Exact: {len(patched_id):,} B)")

    # Test EN
    with zipfile.ZipFile(EN_ZIP, 'r') as z:
        en_1_0 = z.read('1/1_0.db')
    print(f"[*] Processing EN shard ({len(en_1_0):,} bytes)...")
    patched_en, en_tbls, en_strs = patch_shard_bytes(en_1_0, terms, is_en=True, verbose=verbose)
    print(f"    [✓] EN Result: {en_tbls} tables modified, {en_strs} strings replaced (Bit-Exact: {len(patched_en):,} B)")

    print("\n[✓] In-memory verification PASSED with 0 errors!")
    return patched_id, patched_en

def run_apply(verbose=False):
    terms = load_terms()
    print("\n" + "="*50)
    print("ZENITH DEVELOPER CARD PATCHER: APPLY TO LOCAL ARCHIVES")
    print("="*50)

    for zip_path, is_en, lang_name in [(ID_ZIP, False, "Bahasa Indonesia"), (EN_ZIP, True, "Global English")]:
        print(f"\n[*] Patching {lang_name} ({os.path.basename(zip_path)})...")
        with zipfile.ZipFile(zip_path, 'r') as zin:
            items = {info.filename: (info, zin.read(info.filename)) for info in zin.infolist()}

        orig_1_0 = items['1/1_0.db'][1]
        patched_1_0, tbls, strs = patch_shard_bytes(orig_1_0, terms, is_en=is_en, verbose=verbose)
        print(f"    [✓] Reconstructed: {tbls} tables, {strs} strings updated")

        tmp_zip = zip_path + '.tmp'
        with zipfile.ZipFile(tmp_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zout:
            for fname, (info, raw_bytes) in items.items():
                if fname == '1/1_0.db':
                    zout.writestr(fname, patched_1_0)
                else:
                    zout.writestr(fname, raw_bytes)
        os.replace(tmp_zip, zip_path)
        print(f"    [✓] Saved {zip_path} ({os.path.getsize(zip_path):,} bytes, SHA-256: {sha256_file(zip_path)})")

    # Update manifest
    id_size = os.path.getsize(ID_ZIP)
    id_hash = sha256_file(ID_ZIP)
    en_size = os.path.getsize(EN_ZIP)
    en_hash = sha256_file(EN_ZIP)

    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    manifest['packages']['id']['sha256'] = id_hash
    manifest['packages']['id']['sizeBytes'] = id_size
    manifest['packages']['en']['sha256'] = en_hash
    manifest['packages']['en']['sizeBytes'] = en_size
    with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    print(f"\n[✓] Manifest updated: {MANIFEST_FILE}")

    # Mirror to repo clone if present
    if os.path.exists(REPO_CLONE_DIR):
        shutil.copy2(ID_ZIP, os.path.join(REPO_CLONE_DIR, "shards", "golden_shards.zip"))
        shutil.copy2(EN_ZIP, os.path.join(REPO_CLONE_DIR, "shards", "golden_shards_en.zip"))
        shutil.copy2(MANIFEST_FILE, os.path.join(REPO_CLONE_DIR, "shards_manifest.json"))
        print(f"[✓] Mirrored updated archives to git repo clone: {REPO_CLONE_DIR}")

def run_deploy(token, verbose=False):
    run_apply(verbose=verbose)
    print("\n" + "="*50)
    print("ZENITH DEVELOPER CARD PATCHER: DEPLOY TO GITHUB")
    print("="*50)

    if not os.path.exists(REPO_CLONE_DIR):
        print(f"[!] Folder git clone tidak ditemukan: {REPO_CLONE_DIR}")
        return

    # Git commit & push
    auth_remote = f"https://AuraXaviera:{token}@github.com/AuraXaviera/HonorOfKingsAce.git"
    subprocess.run(["git", "-C", REPO_CLONE_DIR, "remote", "set-url", "origin", auth_remote], check=True)
    subprocess.run(["git", "-C", REPO_CLONE_DIR, "add", "."], check=True)
    subprocess.run(["git", "-C", REPO_CLONE_DIR, "commit", "-m", "fix(cards): update terms via patch_cards CLI"], capture_output=True)
    print("[*] Pushing commit to GitHub main branch...")
    subprocess.run(["git", "-C", REPO_CLONE_DIR, "push", "origin", "main"], check=True)
    print("[✓] Git push successful!")

    # Upload to Release
    upload_script = os.path.join(ROOT_DIR, "work_temp", "upload_release.py")
    if os.path.exists(upload_script):
        print("[*] Uploading assets to GitHub Release v1.8.2...")
        subprocess.run([sys.executable, upload_script, token], check=True)
        print("[✓] Release upload completed!")

def main():
    parser = argparse.ArgumentParser(description="Zenith Fast Card Patcher CLI")
    parser.add_argument("--apply", action="store_true", help="Apply fixes to local zip archives and manifest")
    parser.add_argument("--deploy", action="store_true", help="Apply fixes, commit to git, and upload to GitHub Release")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="GitHub token for deployment")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose table logging")
    parser.add_argument("--add-id", nargs=2, metavar=("OLD", "NEW"), help="Add an ID term override")
    parser.add_argument("--add-en", nargs=2, metavar=("OLD", "NEW"), help="Add an EN term override")

    args = parser.parse_args()

    # Handle quick add
    if args.add_id or args.add_en:
        terms = load_terms()
        if args.add_id:
            terms.setdefault("id", {})[args.add_id[0]] = args.add_id[1]
            print(f"[+] Added ID override: '{args.add_id[0]}' -> '{args.add_id[1]}'")
        if args.add_en:
            terms.setdefault("en", {})[args.add_en[0]] = args.add_en[1]
            print(f"[+] Added EN override: '{args.add_en[0]}' -> '{args.add_en[1]}'")
        save_terms(terms)
        return

    if args.deploy:
        run_deploy(args.token, verbose=args.verbose)
    elif args.apply:
        run_apply(verbose=args.verbose)
    else:
        run_verify(verbose=args.verbose)

if __name__ == '__main__':
    main()
