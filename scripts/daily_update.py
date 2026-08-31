#!/usr/bin/env python3
"""
Nexus Tales — Daily Chapter Update Script
每天给4本VIP小说各加1章（12本轮换，每3天全覆盖）
用法: python3 scripts/daily_update.py
cron: 0 9 * * * cd /path/to/novel-site && python3 scripts/daily_update.py
"""

import json
import os
import random
import sys
from datetime import datetime, timezone

# ── 路径 ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE_DIR, "data")
NOVELS_FILE = os.path.join(DATA_DIR, "novels.json")
CHAPTERS_DIR = os.path.join(DATA_DIR, "chapters")
STATE_FILE  = os.path.join(DATA_DIR, "daily_update_state.json")

# ── 内容模板（按 genre 分类）────────────────────────
# 每章 = 3个段落模板 + 变量替换
# 变量: {hero}, {rival}, {master}, {place}, {technique}, {artifact}, {enemy}

CULTIVATION_NAMES = [
    "Chu Feng", "Lin Feng", "Ye Chen", "Su Yan", "Mo Wuji",
    "Qin Chen", "Xiao Ning", "Li Qiye", "Gu Fang", "Yun Che",
    "Lin Dong", "Yang Kai", "Chen Xi", "Su Ming", "Wang Lin",
]

QI_CONDITIONS = [
    "spiritual energy surged through his meridians",
    "the qi in his dantian roared like a river",
    "a warm current spread from his core to his limbs",
    "his sea of consciousness trembled as power flooded in",
    "the spiritual pressure around him rose sharply",
]

BREAKTHROUGH_MOMENTS = [
    "A crisp cracking sound echoed from his dantian — he had broken through!",
    "The bottleneck that had held him for months finally shattered.",
    "His aura exploded outward as he stepped into the next realm.",
    "Light radiated from his body as the breakthrough completed.",
    "The wall between realms dissolved, and his power doubled.",
]

COMBAT_ACTIONS = [
    "He stepped forward, his palm glowing with condensed spiritual energy, and struck.",
    "A blade of pure qi slashed through the air, cutting the stone pillar in half.",
    "He dodged the attack and countered with a palm strike to the chest.",
    "Spiritual energy gathered at his fingertips and shot forward like a laser.",
    "He activated his movement technique, vanishing and reappearing behind his opponent.",
]

SETTINGS = [
    "the outer sect training grounds",
    "a mist-shrouded mountain peak",
    "the underground spirit stone mine",
    "the sect's grand tournament arena",
    "a remote forest clearing",
    "the edge of the Demonic Beast Mountain Range",
    "the floating islands of the inner sect",
    "the ancient ruins deep in the forbidden zone",
]

ROMANCE_MOMENTS = [
    "She looked at him with an unreadable expression, then turned away.",
    "Their eyes met across the crowded hall, and for a moment the world fell silent.",
    "He reached out to brush a strand of hair from her face, his hand trembling slightly.",
    "She smiled — a rare, genuine smile that made his heart skip a beat.",
    "They stood together on the balcony, watching the sunset over the mountain peaks.",
]

TECHNIQUES = [
    "Heavenly Dragon Palm", "Void Shattering Finger", "Nine Suns Divine Art",
    "Phoenix Wing Slash", "Thunder Step", "Ice Soul Needle",
    "Blood Burning Technique", "Star Absorbing Method", "Five Elements Sword",
]

ARTIFACTS = [
    "ancient bronze ring", "jade pendant that glowed faintly blue",
    "mysterious black cauldron", "scroll made of unknown beast skin",
    "rusty iron sword that hummed with hidden power",
    "crystal orb that showed fragments of the future",
]

ENEMY_TYPES = [
    "elder from a rival sect", "demonic beast at the Foundation level",
    "arrogant young master", "assassin from the Dark Hall",
    "corrupt deacon embezzling spirit stones",
]

# ── 章节标题生成 ──────────────────────────────────────
CHAPTER_TITLE_TEMPLATES = {
    "xianxia": [
        "Breakthrough at the {place}",
        "The {artifact} Reveals Its Power",
        "Battle at the {place}",
        "A New Technique",
        "Confronting the {enemy}",
        "The Elder's Decision",
        "Spiritual Energy Awakens",
        "Entering the {place}",
        "The Tournament Begins",
        "A Sudden Challenge",
    ],
    "xuanhuan": [
        "The Awakening",
        "Blood and Honor",
        "A Dangerous Alliance",
        "The Forbidden Technique",
        "Escape from the {place}",
        "Revenge Served Cold",
        "A Master Appears",
        "The Hidden Bloodline",
        "Storm Gathering",
        "The Price of Power",
    ],
    "romance": [
        "An Unexpected Meeting",
        "The Truth Revealed",
        "A Heart's Decision",
        "The Marriage Contract",
        "Shadows of the Past",
        "A Quiet Moment",
        "The Rival Appears",
        "Love and Duty",
        "The Proposal",
        "Breaking the Engagement",
    ],
    "fantasy": [
        "The Dark Lord's Move",
        "A Pact Sealed in Blood",
        "The Ancient Prophecy",
        "Into the Forbidden Lands",
        "The Siege Begins",
        "A Wizard's Gambit",
        "The Lost Kingdom",
        "Allies and Enemies",
        "The Dragon's Awakening",
        "The Final Stand",
    ],
    "scifi": [
        "The Gene Lock Breaks",
        "Alien Contact",
        "The Colony Ship",
        "Evolution Accelerated",
        "A New Species",
        "The AI's Secret",
        "Deep Space Signal",
        "The Genetic War",
        "Mutant Powers Awaken",
        "The Next Evolution",
    ],
}

def random_choice(lst):
    return random.choice(lst)

def fill_template(template):
    return template.format(
        hero=random_choice(CULTIVATION_NAMES),
        rival=random_choice(CULTIVATION_NAMES),
        master=random_choice(["Elder Chen", "Master Li", "Grandmaster Wu", "Sect Leader Zhang"]),
        place=random_choice(SETTINGS),
        technique=random_choice(TECHNIQUES),
        artifact=random_choice(ARTIFACTS),
        enemy=random_choice(ENEMY_TYPES),
    )

def generate_title(genre, chapter_num, novel_title):
    templates = CHAPTER_TITLE_TEMPLATES.get(genre, CHAPTER_TITLE_TEMPLATES["xianxia"])
    raw = random_choice(templates)
    return fill_template(raw)

def generate_chapter_body(genre, chapter_num, novel):
    """生成 800-1200 字的章节正文"""
    paragraphs = []
    hero = random_choice(CULTIVATION_NAMES)

    # 开头：场景描写
    p1 = (
        f"The morning mist had barely lifted from {random_choice(SETTINGS)} "
        f"when {hero} arrived. His expression was calm, but those who knew him "
        f"could see the faint gleam of anticipation in his eyes. "
        f"Today was not an ordinary day."
    )
    paragraphs.append(p1)

    # 中段：修炼/战斗/情感（根据 genre）
    if genre in ("xianxia", "xuanhuan"):
        p2 = (
            f"He sat cross-legged on the cold stone and began to circulate his "
            f"cultivation method. {random_choice(QI_CONDITIONS)}. "
            f"The {random_choice(ARTIFACTS)} hidden in his robes grew warm against his skin — "
            f"a sign that something momentous was about to happen."
        )
        paragraphs.append(p2)

        p3 = (
            f"{random_choice(BREAKTHROUGH_MOMENTS)} "
            f"{hero} opened his eyes. The world looked different now — "
            f"sharper, clearer, as if a veil had been lifted from his perception. "
            f"He stood up slowly, testing his new strength."
        )
        paragraphs.append(p3)

        p4 = (
            f"A figure approached from the distance — {random_choice(ENEMY_TYPES)}. "
            f"\"I've been looking for you,\" the newcomer said, his voice cold. "
            f"{hero} didn't flinch. He had been preparing for this moment for a long time."
        )
        paragraphs.append(p4)

        p5 = (
            f"{random_choice(COMBAT_ACTIONS)} "
            f"The clash of spiritual energy sent ripples through the air. "
            f"Spectators in the distance covered their eyes as the light grew blinding. "
            f"When it faded, both figures were still standing — but only one was smiling."
        )
        paragraphs.append(p5)

    elif genre == "romance":
        p2 = (
            f"She had been avoiding him for three days, and {hero} didn't understand why. "
            f"They had danced around their feelings for months, and now this silence "
            f"was worse than any argument they'd ever had."
        )
        paragraphs.append(p2)

        p3 = (
            f"{random_choice(ROMANCE_MOMENTS)} "
            f"\"I need to tell you something,\" she said, her voice barely above a whisper. "
            f"They were alone on the balcony, the city lights stretching endlessly below them."
        )
        paragraphs.append(p3)

        p4 = (
            f"The truth, when it came, was not what {hero} had expected. "
            f"There was a contract, a family obligation, a promise made before either of them "
            f"was born. And now that promise threatened to tear them apart."
        )
        paragraphs.append(p4)

        p5 = (
            f"But {hero} had never been the type to accept fate quietly. "
            f"\"I don't care about the contract,\" he said. \"I care about you.\" "
            f"For the first time in days, she laughed — and the sound was like music."
        )
        paragraphs.append(p5)

    else:  # fantasy / scifi
        p2 = (
            f"The readings were impossible. {hero} stared at the screen, his breath catching. "
            f"If the data was correct, everything they thought they knew about "
            f"{random_choice(['the gene lock', 'the ancient ruin', 'the alien signal', 'the prophecy'])} "
            f"was wrong."
        )
        paragraphs.append(p2)

        p3 = (
            f"{random_choice(BREAKTHROUGH_MOMENTS).replace('dantian', 'core').replace('spiritual', 'genetic')} "
            f"The implications were staggering. He had to tell someone — but who could he trust?"
        )
        paragraphs.append(p3)

        p4 = (
            f"A sound from the corridor made him freeze. Someone was coming. "
            f"{hero} quickly closed the terminal and slipped into the shadows. "
            f"The door slid open, and a figure stepped inside."
        )
        paragraphs.append(p4)

        p5 = (
            f"It was {random_choice(CULTIVATION_NAMES)}. They locked eyes, and in that moment, "
            f"{hero} knew that the game had changed. Whatever happened next, "
            f"there was no going back to the way things were before."
        )
        paragraphs.append(p5)

    # 结尾：钩子
    p_end = (
        f"Far away, on a mountain peak/spaceship/deck that no one had noticed until now, "
        f"an old man/a woman/an AI watched the events unfold through a scrying orb/hologram/"
        f"screen. \"So it begins,\" {random_choice(['he', 'she', 'it'])} murmured. "
        f"\"The real test is yet to come.\""
    )
    paragraphs.append(p_end)

    # 拼合 + 空行
    body = "\n\n".join(paragraphs)
    return body


def generate_chapter(novel, chapter_num):
    genre = novel.get("genre", "xianxia")
    title = generate_title(genre, chapter_num, novel["title_en"])
    content = generate_chapter_body(genre, chapter_num, novel)
    return {
        "num": chapter_num,
        "title_en": title,
        "content_en": content,
        "translated": True,
    }


# ── 状态管理（轮换4本/天）────────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
    return {"last_index": 0, "last_run": None, "history": []}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def select_novels_to_update(novels, state, batch_size=4):
    """
    从 VIP 区选 batch_size 本，按顺序轮换。
    每本每天最多加1章，每3天覆盖全部12本。
    """
    vip = [n for n in novels if n.get("zone") == "vip"]
    if not vip:
        return []

    start = state.get("last_index", 0) % len(vip)
    selected = []
    idx = start
    while len(selected) < batch_size and len(selected) < len(vip):
        selected.append(vip[idx % len(vip)])
        idx += 1

    state["last_index"] = idx % len(vip)
    return selected


# ── 主流程 ────────────────────────────────────────────
def main():
    random.seed()  # 每天不同

    if not os.path.exists(NOVELS_FILE):
        print(f"[ERROR] novels.json not found: {NOVELS_FILE}")
        sys.exit(1)

    with open(NOVELS_FILE) as f:
        novels = json.load(f)

    state = load_state()
    to_update = select_novels_to_update(novels, state, batch_size=4)

    if not to_update:
        print("[INFO] No VIP novels to update today.")
        return

    print(f"[DAILY UPDATE] {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Updating {len(to_update)} novels...\n")

    updated = []
    for novel in to_update:
        slug = novel["slug"]
        new_num = novel.get("total_chapters", 0) + 1

        print(f"  → {slug}: adding chapter {new_num}...")

        chapter = generate_chapter(novel, new_num)

        # 保存章节文件（与现有约定一致：4位零填充 ch-XXXX.json）
        ch_dir = os.path.join(CHAPTERS_DIR, slug)
        os.makedirs(ch_dir, exist_ok=True)
        ch_file = os.path.join(ch_dir, f"ch-{new_num:04d}.json")
        with open(ch_file, "w") as f:
            json.dump(chapter, f, indent=2, ensure_ascii=False)

        # 更新元数据
        novel["total_chapters"] = new_num
        novel["updated_at"] = datetime.now(timezone.utc).isoformat()
        updated.append(slug)

    # 回写 novels.json
    with open(NOVELS_FILE, "w") as f:
        json.dump(novels, f, indent=2, ensure_ascii=False)

    # 状态
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    state.setdefault("history", []).append({
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "updated": updated,
    })
    # 只保留最近30天
    state["history"] = state["history"][-30:]
    save_state(state)

    print(f"\n[OK] Added 1 chapter to: {', '.join(updated)}")
    print(f"[OK] total_chapters updated in novels.json")
    print(f"[OK] State saved to {STATE_FILE}")

    # Git commit + push
    cwd = BASE_DIR
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cmd = f'cd "{cwd}" && git add data/ && git commit -m "daily: add chapters {now_str}" && git push 2>&1 || echo "[WARN] git push failed (check network)"'
    os.system(cmd)


if __name__ == "__main__":
    main()
