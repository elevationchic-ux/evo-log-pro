from pathlib import Path
import re

p = Path("evo-log-frontend/src/config/navigationRegistry.ts")
txt = p.read_text(encoding="utf-8")

# Try progressively
print("test 1: simple } then {")
pat1 = re.compile(r'\}\s+\{')
print(f"  count: {len(pat1.findall(txt))}")

print("test 2: }\\n          {")
pat2 = re.compile(r'\}\n\s+\{')
print(f"  count: {len(pat2.findall(txt))}")

print("test 3: full")
pat3 = re.compile(r'(\})(?!,)([\s]+)(\{)')
print(f"  count: {len(pat3.findall(txt))}")

print("test 4: with expansion lookahead")
pat4 = re.compile(r'(\})(?!,)([\s]+)(\{[\s\S]{0,300}?badge: "Expansion")')
print(f"  count: {len(pat4.findall(txt))}")

print("test 5: no backreferences")
pat5 = re.compile(r'\}(?!,)[\s]+\{[\s\S]{0,300}?badge: "Expansion')
print(f"  count: {len(pat5.findall(txt))}")
