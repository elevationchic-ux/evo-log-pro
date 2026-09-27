"""Fix double-encoded UTF-8 files across the frontend.

Detects: bytes starting with 0xC3 0x83 (which is UTF-8 for 'Ã',
the mojibake signature of UTF-8 bytes re-encoded as UTF-8).
Repairs: decode(utf-8) -> encode(latin-1) -> decode(utf-8) to undo one round.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "evo-log-frontend" / "src"

def is_double_encoded(path: pathlib.Path) -> bool:
    raw = path.read_bytes()
    if len(raw) < 50:
        return False
    # Look for 0xC3 0x83 (Ã in double-encoded) in first 5000 bytes
    window = raw[:5000]
    for i in range(len(window) - 1):
        if window[i] == 0xC3 and window[i + 1] == 0x83:
            return True
    return False


def fix_file(path: pathlib.Path) -> bool:
    raw = path.read_bytes()
    try:
        # First decode gives us the mojibake (e.g., "Ã©" for "é")
        text = raw.decode("utf-8")
        # Re-encode recovers original UTF-8 bytes, then decode properly
        # Try latin-1 first (covers U+0000 to U+00FF), then cp1252 (adds 0x80-0x9F)
        try:
            fixed = text.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            fixed = text.encode("cp1252").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return False
    # Normalize line endings to LF (frontend standard)
    fixed = fixed.replace("\r\n", "\n")
    path.write_bytes(fixed.encode("utf-8"))
    return True


def main():
    fixed = 0
    checked = 0
    for ext in ("*.tsx", "*.ts", "*.css", "*.json"):
        for f in sorted(ROOT.rglob(ext)):
            if "node_modules" in str(f):
                continue
            checked += 1
            if is_double_encoded(f):
                if fix_file(f):
                    rel = f.relative_to(ROOT.parent)
                    print(f"FIXED   {rel}")
                    fixed += 1
                else:
                    rel = f.relative_to(ROOT.parent)
                    print(f"STUCK   {rel} (could not repair cleanly)")
    print(f"\n{fixed} files repaired out of {checked} checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
