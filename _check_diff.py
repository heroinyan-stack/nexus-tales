import json, subprocess, os

# Read current
with open('data/novels.json') as f:
    curr = json.load(f)

# Read previous from git
r = subprocess.run(['git', 'show', 'HEAD:data/novels.json'], capture_output=True)
prev = json.loads(r.stdout.decode('utf-8'))

prev_ids = {n['id'] for n in prev}
curr_ids = {n['id'] for n in curr}
new_ids = curr_ids - prev_ids

print(f'Previous novels: {len(prev)}')
print(f'Current novels:  {len(curr)}')
print(f'New novels:      {len(new_ids)}')
print()

for n in curr:
    if n['id'] in new_ids:
        title = n.get('title_en') or n.get('title_zh', '???')
        chapters = n.get('total_chapters', 0)
        print(f"  [{n['id']:4d}] {title} | {chapters} chapters")

print()
print(f"Total chapters (all novels): {sum(n.get('total_chapters', 0) for n in curr):,}")
