import pathlib, shutil
sdk = pathlib.Path(shutil.which('flutter')).resolve().parents[1]
p = sdk / 'packages/flutter_tools/lib/src/isolated/native_assets/macos/native_assets.dart'
text = p.read_text()
old = 'const targetMacOSVersion = 13;'
new = 'const targetMacOSVersion = 11;'
assert old in text or new in text, 'Unexpected Flutter native-assets target implementation'
if old in text:
    p.write_text(text.replace(old, new))
    for name in ('flutter_tools.snapshot', 'flutter_tools.stamp'):
        cached = sdk / 'bin/cache' / name
        if cached.exists():
            cached.unlink()
print('Flutter native-assets compilation target is macOS 11 (upstream hard-codes 13).')
print('This rebuilds C sources with the correct deployment target; no Mach-O metadata rewriting.')
