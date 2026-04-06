import json, os, re

manifest = []
latest = {}

for root, dirs, files in os.walk('styles'):
    for fname in sorted(files):
        if not fname.endswith('.png'):
            continue
        img = os.path.join(root, fname)
        if os.path.islink(img):
            continue
        basename = fname[:-4]
        match = re.match(r'(.+?)_v(\d+)$', basename)
        if not match:
            continue
        word = match.group(1)
        ver_num = int(match.group(2))
        manifest.append({'word': word, 'version': 'v' + str(ver_num), 'path': img, 'url': img})
        if word not in latest or ver_num > latest[word][0]:
            latest[word] = (ver_num, img)

for word, (ver_num, img_path) in latest.items():
    manifest.append({'word': word, 'version': 'latest', 'path': img_path, 'url': img_path})

with open('manifest.json', 'w') as f:
    json.dump(manifest, f, indent=2)
print('Done:', len(manifest), 'entries,', len(latest), 'latest')
