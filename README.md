# ZX Spectrum QR transfer - Short Circuit (1987)
# X-Seti - November 17 2025 - This little project is WIP, just a bit of fun. 

This package converts the supplied TAP file into a set of numbered QR codes and
reconstructs the original TAP file from those codes.


## Supplied game file
- File: `Short Circuit (1987)(Erbe Software)(128k)[re-release].tap`
- Size: 91,033 bytes
- QR chunk size: 1,100 bytes
- QR codes: 83
- SHA-256: `9e71e4099210c253de1e36be6b60ab8fc2644230d20475ca624456610abba71b`


## Install (Linux / Garuda / Ubuntu / Debian)
Python 3 is required. From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Rebuild from the included QR PNGs
```bash
python decode_from_qr.py qr_codes/ -o Short_Circuit_recovered.tap
```

## Scan printed codes with a webcam
```bash
python decode_from_qr.py --webcam -o Short_Circuit_recovered.tap
```
Show each QR code to the camera in turn. The reader remembers each numbered
chunk; press Q when finished. It reports any missing chunks and verifies the
complete file with SHA-256 before writing it.


## Convert another TAP/TZX/binary into QR codes
```bash
python encode_to_qr.py "my_game.tap" -o my_game_qr
```
Then rebuild it with:
```bash
python decode_from_qr.py my_game_qr/ -o recovered.tap
```

## Using the recovered game
The recovered file is a normal `.tap` file. Open it in your ZX Spectrum
emulator (for example Fuse) exactly as you would the original.


## Notes
- The PDF contains four large QR codes per A4 page.
- The individual PNGs are the best source for screen scanning or reprinting.
- Keep all codes from the same set together. Each code includes a set checksum
  and its sequence number.
- QR error correction is set to Medium. If a printed/scanned code is unreliable,
  display its PNG larger or reprint it.
- The decoder needs OpenCV; webcam support depends on your system's camera
  permissions and OpenCV video backend.
