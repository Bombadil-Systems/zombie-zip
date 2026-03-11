# Zombie ZIP

ZIP format confusion technique that evades 98% of antivirus engines.

**CVE-2026-0866** | [VU#976247](https://kb.cert.org/vuls/id/976247) | Published March 10, 2026

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

|File               |Technique |VirusTotal                                                                                                  |
|-------------------|----------|------------------------------------------------------------------------------------------------------------|
|baseline.zip       |Valid ZIP |55/67                                                                                                       |
|method_mismatch.zip|Zombie ZIP|[1/66](https://www.virustotal.com/gui/file/7316a4c3cd1cf183925ab4b7e77dbf52b38180ee1faf0156d7ea410f42cb5e76)|

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

## Files

zombie_zip.py - Generator script  
method_mismatch.zip - Pre-generated PoC with EICAR  
baseline.zip - Valid ZIP for comparison  
loader_poc.py - Demonstrates programmatic payload recovery  

## How It Works

AV engines trust the ZIP Method field. When Method=0 (STORED), they scan the data as raw uncompressed bytes. But the data is actually DEFLATE compressed — so the scanner sees compressed noise and finds no signatures.

The CRC is set to the uncompressed payload’s checksum, creating an additional mismatch that causes standard extraction tools (7-Zip, unzip, WinRAR) to report errors or extract corrupted output.

However, a purpose-built loader that ignores the declared method and decompresses as DEFLATE recovers the payload perfectly. This is demonstrated by loader_poc.py — six lines of standard zlib.

The vulnerability is scanner evasion: security controls assert “no malware present” while malware is present and trivially recoverable by attacker tooling.

## Attack Vector

This is not an end-user extraction vulnerability. It is a staged delivery / smuggling technique:

1. Malicious payload packaged in a Zombie ZIP
1. ZIP transits security boundaries (email gateways, network scanners, endpoint AV)
1. Scanners read Method=0, scan compressed noise, report “clean”
1. A loader or dropper decompresses the payload programmatically
1. Payload materializes and executes

This is consistent with established malware delivery patterns (ISO smuggling, HTML smuggling, CAB abuse) where attackers use custom loaders rather than consumer extraction tools.

## Affected

- 50/51 AV engines on VirusTotal
- Microsoft Defender, Avast, Bitdefender, ESET, Kaspersky, McAfee, Sophos, TrendMicro, etc.
- Only Kingsoft detected it

## Prior Art

- **VU#968818** (CERT/CC, 2004): Malformed ZIP archives evading AV
- **CVE-2004-0935**: ESET Anti-Virus bypass via malformed ZIP headers
- This technique demonstrates a new primitive (method field desynchronization) within the same vulnerability class

## Author

Chris Aziz - Bombadil Systems

## License

MIT - For authorized security research only.
