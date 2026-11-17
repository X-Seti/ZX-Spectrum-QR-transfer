#!/usr/bin/env python3
"""Split a ZX Spectrum TAP/TZX or any binary file into numbered QR codes."""
# X-Seti - November 17 2025

import argparse, base64, hashlib, math, pathlib
import qrcode
from qrcode.constants import ERROR_CORRECT_M

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=pathlib.Path)
    ap.add_argument("-o", "--output", type=pathlib.Path, default=pathlib.Path("qr_output"))
    ap.add_argument("--chunk-size", type=int, default=1100)
    args = ap.parse_args()
    raw = args.input.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    name = base64.urlsafe_b64encode(args.input.name.encode()).decode().rstrip("=")
    parts = [raw[i:i+args.chunk_size] for i in range(0, len(raw), args.chunk_size)]
    args.output.mkdir(parents=True, exist_ok=True)
    for n, part in enumerate(parts, 1):
        body = base64.b64encode(part).decode()
        text = f"ZXSQR1|{n}|{len(parts)}|{digest}|{name}|{body}"
        qr = qrcode.QRCode(error_correction=ERROR_CORRECT_M, box_size=8, border=4)
        qr.add_data(text); qr.make(fit=True)
        qr.make_image(fill_color="black", back_color="white").save(args.output / f"qr_{n:04d}_of_{len(parts):04d}.png")
    print(f"Created {len(parts)} QR images in {args.output}")
    print(f"Original: {len(raw)} bytes; SHA-256: {digest}")
if __name__ == "__main__": main()
