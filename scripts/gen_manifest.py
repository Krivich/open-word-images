import json, os, re, shutil, glob

manifest = []
latest = {}

# Step 1: Auto-version unversioned files
for root, dirs, files in os.walk('styles'):
    for f in sorted(files):
        if not f.endswith('.png') or os.path.islink(os.path.join(root, f)):
            continue
        bn = f[:-4]
        m = re.match(r'(.+?)_v(\d+)$', bn)
        if not m:
            # Unversioned file — find max version and rename
            word = bn
            existing = glob.glob(os.path.join(root, f'{word}_v*.png'))
            max_ver = 0
            for ep in existing:
                em = re.match(rf'{re.escape(word)}_v(\d+)\.png$', os.path.basename(ep))
                if em:
                    max_ver = max(max_ver, int(em.group(1)))
            new_ver = max_ver + 1
            old = os.path.join(root, f)
            new = os.path.join(root, f'{word}_v{new_ver}.png')
            os.rename(old, new)
            print(f'Auto-versioned: {f} -> {word}_v{new_ver}.png')

# Step 2: Build manifest
for root, dirs, files in os.walk('styles'):
    for f in sorted(files):
        if not f.endswith('.png') or os.path.islink(os.path.join(root, f)):
            continue
        bn = f[:-4]
        m = re.match(r'(.+?)_v(\d+)$', bn)
        if not m:
            continue
        word, ver = m.group(1), int(m.group(2))
        p = os.path.join(root, f).replace('\\', '/')
        manifest.append({'word': word, 'version': 'v' + str(ver), 'path': p, 'url': p})
        if word not in latest or ver > latest[word][0]:
            latest[word] = (ver, p)

# Step 3: Create symlinks (works on Linux)
for word, (ver, p) in latest.items():
    link_path = p.replace('_v' + str(ver) + '.png', '_latest.png')
    
    # Remove existing symlink and old thumbnails
    if os.path.exists(link_path) or os.path.islink(link_path):
        os.remove(link_path)
    for size in [128, 256, 512]:
        thumb = link_path.replace('_latest.png', f'_latest_{size}.png')
        if os.path.exists(thumb):
            os.remove(thumb)
    
    try:
        os.symlink(os.path.basename(p), link_path)  # Linux symlink
        print(f'Updated symlink: {word}')
    except OSError:
        shutil.copy2(p, link_path)  # Windows fallback
    manifest.append({'word': word, 'version': 'latest', 'path': link_path, 'url': link_path})

manifest.sort(key=lambda x: (x['word'], 0 if x['version'] == 'latest' else int(x['version'][1:])))
with open('manifest.json', 'w') as out:
    json.dump(manifest, out, indent=2)
print('Done:', len(manifest), 'entries')
