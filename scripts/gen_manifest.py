import json, glob, os, re

manifest = []
latest = {}

for img in sorted(glob.glob('styles/**/*.png', recursive=True)):
    if os.path.islink(img):
        continue
    basename = os.path.splitext(os.path.basename(img))[0]
    match = re.match(r'(.+?)_v(\d+)$', basename)
    if not match:
        continue
    word = match.group(1)
    ver_num = int(match.group(2))
    manifest.append({'word': word, 'version': 'v' + str(ver_num), 'path': img, 'url': img})
    if word not in latest or ver_num > latest[word][0]:
        latest[word] = (ver_num, img)

for word, (ver_num, img_path) in latest.items():
    link_path = os.path.join(os.path.dirname(img_path), word + '_latest.png')
    target = word + '_v' + str(ver_num) + '.png'
    if os.path.islink(link_path) or os.path.exists(link_path):
        os.remove(link_path)
    os.symlink(target, link_path)
    manifest.append({'word': word, 'version': 'latest', 'path': link_path, 'url': link_path})

with open('manifest.json', 'w') as f:
    json.dump(manifest, f, indent=2)
print('Done:', len(manifest), 'entries,', len(latest), 'symlinks')
