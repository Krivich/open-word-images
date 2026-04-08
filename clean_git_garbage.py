import os, subprocess

# Ищем все файлы, в имени которых "latest" встречается более 1 раза или есть паттерн "_latest_NNN_"
bad_files = []
for root, dirs, files in os.walk('styles'):
    for f in files:
        if f.endswith('.png'):
            if f.count('latest') > 1 or (f.count('_latest_') > 1 and any(s in f for s in ['_128', '_256', '_512'])):
                bad_files.append(os.path.join(root, f))

if bad_files:
    print(f'Found {len(bad_files)} garbage files to remove.')
    for f in bad_files:
        print(f'Removing: {f}')
        # Удаляем из Git индекса и с диска
        subprocess.run(['git', 'rm', '-f', f], check=True)
    print('Done! Commit and push these changes.')
else:
    print('No garbage files found locally.')
