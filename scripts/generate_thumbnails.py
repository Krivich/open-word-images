import os
from PIL import Image

SIZES = [128, 256, 512]

for root, dirs, files in os.walk('styles'):
    for f in sorted(files):
        # Skip non-PNG files and existing thumbnails
        if not f.endswith('.png'):
            continue
        bn = f[:-4]
        
        # Skip if this is already a thumbnail (ends with _128, _256, _512)
        if any(bn.endswith(f'_{size}') for size in SIZES):
            continue
            
        # Process only _latest.png files (including symlinks)
        if not bn.endswith('_latest'):
            continue
            
        img_path = os.path.join(root, f)
        
        # Skip if all thumbnails already exist
        all_exist = all(os.path.exists(os.path.join(root, f'{bn}_{size}.png')) for size in SIZES)
        if all_exist:
            continue
        
        try:
            # Follow symlinks to get the real image
            real_path = os.path.realpath(img_path)
            img = Image.open(real_path).convert('RGBA')
            
            for size in SIZES:
                # High-quality resize
                resized = img.resize((size, size), Image.LANCZOS)
                out_path = os.path.join(root, f'{bn}_{size}.png')
                resized.save(out_path, 'PNG', optimize=True)
                
        except Exception as e:
            print(f'Warning: Error processing {f}: {e}')

print('Thumbnails generated successfully')
