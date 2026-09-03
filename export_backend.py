from pathlib import Path

ROOT = Path.cwd()
BACKEND = ROOT / "backend"
OUTPUT = ROOT / "backendtxts"

FILES_PER_TXT = 2

if not BACKEND.exists():
    print("ERROR: backend folder not found:")
    print(BACKEND)
    input("Press Enter to exit...")
    raise SystemExit

OUTPUT.mkdir(exist_ok=True)

# Files/directories to ignore
IGNORE_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".git",
    ".venv",
    "venv",
    "env",
}

# Useful backend text/source files
EXTENSIONS = {
    ".py",
    ".ini",
    ".md",
    ".txt",
    ".example",
    ".yml",
    ".yaml",
}

# Collect backend files
files = []

for path in BACKEND.rglob("*"):
    if not path.is_file():
        continue

    if any(part in IGNORE_DIRS for part in path.parts):
        continue

    if path.suffix.lower() in EXTENSIONS:
        files.append(path)

# Also include project-level backend-related files
for name in [
    "docker-compose.yml",
    "README.md",
    "TECHNICAL_CHALLENGES_AND_SOLUTIONS.md",
]:
    path = ROOT / name
    if path.exists():
        files.append(path)

# Remove duplicates and sort
files = sorted(set(files), key=lambda p: str(p).lower())

print()
print("=" * 80)
print("WorthIt Backend Exporter")
print("=" * 80)
print()
print("Project:")
print(ROOT)
print()
print("Backend:")
print(BACKEND)
print()
print("Output:")
print(OUTPUT)
print()
print(f"Found {len(files)} files.")
print()

# Create TXT files, 2 source files per TXT
for i in range(0, len(files), FILES_PER_TXT):

    batch = files[i:i + FILES_PER_TXT]

    txt_number = (i // FILES_PER_TXT) + 1
    output_file = OUTPUT / f"{txt_number:03d}_backend.txt"

    with output_file.open("w", encoding="utf-8") as out:

        for file_path in batch:

            try:
                relative = file_path.relative_to(ROOT)
            except ValueError:
                relative = file_path

            out.write("\n")
            out.write("=" * 100)
            out.write("\n")
            out.write(f"FILE: {relative}\n")
            out.write(f"FULL PATH: {file_path.resolve()}\n")
            out.write("=" * 100)
            out.write("\n\n")

            try:
                content = file_path.read_text(
                    encoding="utf-8",
                    errors="replace"
                )
                out.write(content)
            except Exception as e:
                out.write(f"\n[ERROR READING FILE: {e}]\n")

            out.write("\n\n")

    print(f"Created: {output_file.name}")

print()
print("=" * 80)
print("DONE")
print("=" * 80)
print()
print(f"Created folder:")
print(OUTPUT)
print()
print(f"Created {((len(files) + 1) // 2)} TXT files.")
print()
input("Press Enter to close...")
