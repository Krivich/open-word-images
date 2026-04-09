import json, os, re, shutil, glob
from PIL import Image

manifest = []
SIZES = [128, 256, 512]

print("Step 1: Searching for new unversioned files...")
new_files = []

# Step 1: Find and auto-version NEW files
for root, dirs, files in os.walk('styles'):
    for f in sorted(files):
        if not f.endswith('.png'):
            continue
        
        # Skip thumbnails and symlinks
        if os.path.islink(os.path.join(root, f)):
            continue
        
        # Skip files that look like thumbnails
        if any(d in f for d in ['_latest_128', '_latest_256', '_latest_512']):
            continue
            
        bn = f[:-4]
        
        # If it's already versioned, skip
        if re.match(r'.+_v\d+$', bn):
            continue
            
        # If it's _latest.png, skip (we handle it later)
        if bn.endswith('_latest'):
            continue
            
        # It's a new file!
        new_files.append(os.path.join(root, f))

if new_files:
    print(f"Found {len(new_files)} new files to process.")
else:
    print("No new files found.")

for file_path in new_files:
    root = os.path.dirname(file_path)
    f = os.path.basename(file_path)
    bn = f[:-4]
    word = bn
    
    # Find max version
    existing = glob.glob(os.path.join(root, f'{word}_v*.png'))
    max_ver = 0
    for ep in existing:
        em = re.match(rf'{re.escape(word)}_v(\d+)\.png$', os.path.basename(ep))
        if em:
            max_ver = max(max_ver, int(em.group(1)))
    
    new_ver = max_ver + 1
    new_name = f'{word}_v{new_ver}.png'
    new_path = os.path.join(root, new_name)
    
    # Rename
    os.rename(file_path, new_path)
    print(f'  Auto-versioned: {f} -> {new_name}')
    
    # Update latest symlink and thumbnails if this is the new latest
    # Check if this version is >= existing latest target
    link_path = os.path.join(root, f'{word}_latest.png')
    is_new_latest = True
    if os.path.islink(link_path):
        target = os.readlink(link_path)
        # Extract version from target filename
        tm = re.match(rf'{re.escape(word)}_v(\d+)\.png$', target)
        if tm:
            if int(tm.group(1)) >= new_ver:
                is_new_latest = False

    if is_new_latest:
        print(f'  Updating latest for {word}...')
        
        # Remove old symlink
        if os.path.exists(link_path) or os.path.islink(link_path):
            os.remove(link_path)
            
        # Remove old thumbnails
        for size in SIZES:
            thumb = os.path.join(root, f'{word}_latest_{size}.png')
            if os.path.exists(thumb):
                os.remove(thumb)
        
        # Create new symlink
        try:
            os.symlink(new_name, link_path)
        except OSError:
            shutil.copy2(new_path, link_path)
            
        # Generate new thumbnails
        try:
            img = Image.open(new_path).convert('RGBA')
            for size in SIZES:
                resized = img.resize((size, size), Image.LANCZOS)
                out_path = os.path.join(root, f'{word}_latest_{size}.png')
                resized.save(out_path, 'PNG', optimize=True)
        except Exception as e:
            print(f'  Warning: Error generating thumbnails: {e}')

# Step 2: Build manifest
print("\nStep 2: Building manifest...")
for root, dirs, files in os.walk('styles'):
    for f in sorted(files):
        if not f.endswith('.png'):
            continue
        # We include versioned files and latest symlinks in manifest
        # We DO NOT include thumbnails in manifest (usually)
        # Or maybe we do? Let's stick to current behavior: include _latest and _vN
        # But exclude thumbnails from manifest to keep it clean? 
        # Actually index.html expects them. Let's include everything that isn't a thumbnail
        
        # Better filter: if it's a thumbnail (_128.png etc), maybe we don't need it in manifest?
        # Let's keep it simple: include everything PNG that isn't a thumbnail
        if any(skip in f for skip in ['_latest_128', '_latest_256', '_latest_512']):
            continue

        bn = f[:-4]
        # Identify if it's versioned or latest
        m = re.match(r'(.+?)_v(\d+)$', bn)
        if m:
            word, ver = m.group(1), int(m.group(2))
            p = os.path.join(root, f).replace('\\', '/')
            manifest.append({'word': word, 'version': 'v' + str(ver), 'path': p, 'url': p})
        elif bn.endswith('_latest'):
            word = bn[:-7]
            p = os.path.join(root, f).replace('\\', '/')
            manifest.append({'word': word, 'version': 'latest', 'path': p, 'url': p})

manifest.sort(key=lambda x: (x['word'], 0 if x['version'] == 'latest' else int(x['version'][1:])))

print(f"\nManifest entries: {len(manifest)}")
with open('manifest.json', 'w', encoding='utf-8') as out:
    json.dump(manifest, out, indent=2, ensure_ascii=False)
print('Done!')