import os, re

# Create symlinks for latest versions
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
        if word not in latest or ver > latest[word][0]:
            latest[word] = (ver, p)

for word, (ver, p) in latest.items():
    link = p.replace('_v' + str(ver) + '.png', '_latest.png')
    if os.path.islink(link) or os.path.exists(link):
        os.remove(link)
    os.symlink(os.path.basename(p), link)

print('Created', len(latest), 'symlinks')
