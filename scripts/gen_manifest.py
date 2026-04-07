import json, os, re, shutil

manifest = []
latest = {}

for root, dirs, files in os.walk('styles'):
    for f in sorted(files):
        if not f.endswith('.png') or os.path.islink(os.path.join(root, f)):
            continue
        bn = f[:-4]
        m = re.match(r'(.+?)_v(\d+)$', bn)
        if not m:
            continue
        word, ver = m.group(1), int(m.group(2))
        p = os.path.join(root, f)
        manifest.append({'word': word, 'version': 'v' + str(ver), 'path': p, 'url': p})
        if word not in latest or ver > latest[word][0]:
            latest[word] = (ver, p)

for word, (ver, p) in latest.items():
    # Create symlink on Linux/macOS, hardlink on Windows
    link_path = p.replace('_v' + str(ver) + '.png', '_latest.png')
    if os.path.exists(link_path) or os.path.islink(link_path):
        os.remove(link_path)
    try:
        os.symlink(os.path.basename(p), link_path)  # Works on Linux
    except OSError:
        shutil.copy2(p, link_path)  # Fallback for Windows
    manifest.append({'word': word, 'version': 'latest', 'path': link_path, 'url': link_path})

manifest.sort(key=lambda x: (x['word'], 0 if x['version'] == 'latest' else int(x['version'][1:])))
with open('manifest.json', 'w') as out:
    json.dump(manifest, out, indent=2)
print('Done:', len(manifest), 'entries')
