# Zombie ZIP

ZIP format confusion technique that evades 98% of antivirus engines.

**CVE-2026-0866** | [**VU#976247**](https://kb.cert.org/vuls/id/976247) | Published March 10, 2026

## The Technique

Create a ZIP file where:

```
Compression Method = 0 (STORED)
Actual data = DEFLATE compressed
CRC-32 = Checksum of uncompressed payload
```

```
AV Engine:  Reads Method 0 → Scans compressed noise → No detection
Attacker:   Ignores Method field → Decompresses as DEFLATE → Recovers payload
```

## Results

| File | Technique | VirusTotal |
|------|-----------|------------|
| baseline.zip | Valid ZIP | 55/67 |
| method_mismatch.zip | Zombie ZIP | **1/66** |

98% evasion. Same payload. Same bytes. Different container.

## Quick Test

```bash
# Generate a Zombie ZIP
python3 zombie_zip.py

# Upload method_mismatch.zip to VirusTotal
# Observe 1/51 detection vs 55/67 for baseline

# Recover payload programmatically
python3 loader_poc.py method_mismatch.zip
# Outputs byte-identical EICAR (SHA-256: 275a021b...)
```

## Container Tool

**Container.py** generalizes the Zombie ZIP technique into a standalone packer/unpacker for arbitrary files using the `.cpack` format.

### How it works

Container.py takes any file, DEFLATE-compresses its contents, and writes them into a ZIP archive declared as STORED (Method=0). The result is a `.cpack` file — an unofficial container format that protects file contents from inspection.

Unlike the original Zombie ZIP PoC, the CRC in a `.cpack` file is computed on the compressed (DEFLATE) bytes, not the original payload. This means the archive is structurally valid — no CRC errors, no corruption flags. The contents are simply opaque to anything that isn't the unpacker.

### Results

| File | Technique | VirusTotal |
|------|-----------|------------|
| eicar.com | Raw EICAR payload | 55/67 |
| eicar.com.cpack | Container packed | [**0/62**](https://www.virustotal.com/gui/file/3cb74ff052646e0d693771676d7a95f0bab41bf34daa65a0e72563a53a5d3824) |

0/62. The one file every AV engine on earth is specifically designed to detect, rendered invisible.

### Usage

```bash
# Requires PyQt6
pip install PyQt6

# Launch the GUI
python3 Container.py
```

- Select any file → produces `filename.cpack` (packed)
- Select a `.cpack` file → recovers the original file (unpacked)

### Why this exists

The underlying technique has been declared by multiple parties to not be a security problem. CERT/CC determined on March 18, 2026 that the Zombie ZIP technique ["does not constitute a valid vulnerability"](https://kb.cert.org/vuls/id/976247) and ["does not bypass or impact any implicit or explicit security controls."](https://kb.cert.org/vuls/id/976247) Cisco classified it as a ["hardening suggestion."](https://bst.cloudapps.cisco.com/bugsearch/bug/CSCws92019) Multiple researchers have publicly stated this is not a vulnerability.

Since this has been declared a non-problem, this tool simply allows you to protect your files and data from scrutiny using a technique with no security implications.

0/62 on EICAR suggests the implications may have been understated.

## Files

- `zombie_zip.py` - Generator script
- `method_mismatch.zip` - Pre-generated PoC with EICAR
- `baseline.zip` - Valid ZIP for comparison
- `loader_poc.py` - Demonstrates programmatic payload recovery
- `Container.py` - GUI packer/unpacker for arbitrary files (.cpack format)

## How It Works

AV engines trust the ZIP Method field. When Method=0 (STORED), they scan the data as raw uncompressed bytes. But the data is actually DEFLATE compressed — so the scanner sees compressed noise and finds no signatures.

In the original Zombie ZIP PoC, the CRC is set to the uncompressed payload's checksum, creating a mismatch that causes standard extraction tools (7-Zip, unzip, WinRAR) to report errors or extract corrupted output.

Container.py avoids this entirely. Because `zipfile.ZipFile` computes the CRC on the bytes being written (the DEFLATE-compressed data), the CRC matches what's stored. Standard tools open the archive without errors. They extract compressed noise successfully. No CRC errors. No corruption flags. AV scans the noise and returns clean.

However, a purpose-built loader that decompresses the stored data as DEFLATE recovers the payload perfectly. Container.py's unpack function demonstrates this — standard `zlib.decompressobj` with raw DEFLATE (`wbits=-15`).

The vulnerability is scanner evasion: security controls assert "no malware present" while malware is present and trivially recoverable.

## Attack Vector

This is not an end-user extraction vulnerability. It is a staged delivery / smuggling technique:

1. Malicious payload packaged in a Zombie ZIP or `.cpack` container
2. File transits security boundaries (email gateways, network scanners, endpoint AV)
3. Scanners read Method=0, scan compressed noise, report "clean"
4. A loader or dropper decompresses the payload programmatically
5. Payload materializes and executes

This is consistent with established malware delivery patterns (ISO smuggling, HTML smuggling, CAB abuse) where attackers use custom loaders rather than consumer extraction tools.

## Affected

- 50/51 AV engines on VirusTotal (Zombie ZIP)
- 62/62 AV engines on VirusTotal (Container / .cpack)
- Microsoft Defender, Avast, Bitdefender, ESET, Kaspersky, McAfee, Sophos, TrendMicro, etc.
- Only Kingsoft detected the original Zombie ZIP. No engine detected `.cpack`.

## Prior Art

- **VU#968818** (CERT/CC, 2004): Malformed ZIP archives evading AV
- **CVE-2004-0935**: ESET Anti-Virus bypass via malformed ZIP headers
- This technique demonstrates a new primitive (method field desynchronization) within the same vulnerability class

## Author

**Chris Aziz** - [Bombadil Systems](https://bombadil.systems)

## License

MIT - For authorized security research only.
