import os
from PIL import Image

SIZES = [128, 256, 512]

for root, dirs, files in os.walk('styles'):
    for f in sorted(files):
        if not f.endswith('.png') or '_latest_' in f or os.path.islink(os.path.join(root, f)):
            continue
        bn = f[:-4]
        
        # Process only _latest.png files
        if not bn.endswith('_latest'):
            continue
            
        img_path = os.path.join(root, f)
        try:
            img = Image.open(img_path).convert('RGBA')
            
            for size in SIZES:
                # High-quality resize
                resized = img.resize((size, size), Image.LANCZOS)
                out_path = os.path.join(root, f'{bn}_{size}.png')
                resized.save(out_path, 'PNG', optimize=True)
                
        except Exception as e:
            print(f'Warning: Error processing {f}: {e}')

print('Thumbnails generated successfully')
