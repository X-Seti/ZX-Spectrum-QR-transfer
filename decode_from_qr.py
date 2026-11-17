#!/usr/bin/env python3
"""Rebuild a binary file from QR images, or collect QR codes from a webcam."""
# X-Seti - November 17 2025

import argparse, base64, hashlib, pathlib, re, sys
import cv2

PREFIX = "ZXSQR1|"

def parse_payload(text):
    if not text.startswith(PREFIX): return None
    fields = text.split("|", 5)
    if len(fields) != 6: return None
    _, index, total, digest, encoded_name, encoded_data = fields
    try:
        index, total = int(index), int(total)
        name = base64.urlsafe_b64decode(encoded_name + "="*((4-len(encoded_name)%4)%4)).decode()
        chunk = base64.b64decode(encoded_data, validate=True)
        if not (1 <= index <= total): return None
        return index, total, digest, name, chunk
    except Exception:
        return None

def decode_image(path, detector):
    image = cv2.imread(str(path))
    if image is None: return []
    # Multi-decode can find more than one code in an image.
    try:
        ok, texts, points, straight = detector.detectAndDecodeMulti(image)
        if ok:
            return [t for t in texts if t]
    except Exception:
        pass
    text, points, straight = detector.detectAndDecode(image)
    return [text] if text else []

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("images", nargs="*", help="QR image files (or use --webcam)")
    ap.add_argument("-o", "--output", type=pathlib.Path, default=pathlib.Path("recovered.tap"))
    ap.add_argument("--webcam", action="store_true", help="scan codes live; press Q to stop")
    ap.add_argument("--camera", type=int, default=0)
    args = ap.parse_args()
    detector = cv2.QRCodeDetector()
    found = {}

    def accept(text):
        item = parse_payload(text)
        if not item: return
        idx, total, digest, name, chunk = item
        if idx in found and found[idx][4] != chunk:
            print(f"Conflicting data for QR {idx}; keeping first copy.")
            return
        found[idx] = item
        print(f"Received QR {idx}/{total} ({len(chunk)} bytes)")

    if args.webcam:
        cap = cv2.VideoCapture(args.camera)
        if not cap.isOpened(): raise SystemExit("Could not open webcam.")
        print("Show each QR code to the camera. Press Q to finish.")
        while True:
            ok, frame = cap.read()
            if not ok: break
            for t in decode_frame(frame, detector): accept(t)
            cv2.imshow("ZX Spectrum QR reader — press Q to finish", frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")): break
        cap.release(); cv2.destroyAllWindows()
    else:
        if not args.images: ap.error("Supply QR image paths, a directory, or --webcam")
        paths = []
        for item in args.images:
            p = pathlib.Path(item)
            paths.extend(sorted(p.glob("*.png")) if p.is_dir() else [p])
        for p in paths:
            for t in decode_image(p, detector): accept(t)

    if not found: raise SystemExit("No valid ZX Spectrum QR codes were decoded.")
    totals = {v[1] for v in found.values()}
    digests = {v[2] for v in found.values()}
    names = {v[3] for v in found.values()}
    if len(totals) != 1 or len(digests) != 1 or len(names) != 1:
        raise SystemExit("The scanned codes belong to different files or sets.")
    total = totals.pop()
    missing = sorted(set(range(1, total+1)) - set(found))
    if missing:
        raise SystemExit(f"Incomplete set: received {len(found)}/{total}; missing: {missing}")
    ordered = b"".join(found[i][5] for i in range(1, total+1))
    expected = digests.pop()
    actual = hashlib.sha256(ordered).hexdigest()
    if actual != expected:
        raise SystemExit(f"Checksum FAILED: expected {expected}, got {actual}")
    suggested = names.pop()
    if args.output == pathlib.Path("recovered.tap") and suggested:
        args.output = pathlib.Path(suggested)
    args.output.write_bytes(ordered)
    print(f"SUCCESS: rebuilt {args.output} ({len(ordered)} bytes)")
    print(f"SHA-256 verified: {actual}")

def decode_frame(frame, detector):
    try:
        ok, texts, points, straight = detector.detectAndDecodeMulti(frame)
        if ok: return [t for t in texts if t]
    except Exception: pass
    text, points, straight = detector.detectAndDecode(frame)
    return [text] if text else []

if __name__ == "__main__": main()
