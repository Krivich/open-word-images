import json, os, re

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
    manifest.append({'word': word, 'version': 'latest', 'path': p, 'url': p})
manifest.sort(key=lambda x: (x['word'], 0 if x['version'] == 'latest' else int(x['version'][1:])))
with open('manifest.json', 'w') as out:
    json.dump(manifest, out, indent=2)
print('Done:', len(manifest))
