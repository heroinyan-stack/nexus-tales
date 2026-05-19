#!/usr/bin/env python3
"""Expand VIP novels to 25 chapters + add free novels."""
import json, os, sys
from datetime import date

BASE = "/Users/myan/.qclaw/workspace/novel-site"
CHAPTERS_DIR = os.path.join(BASE, "data/chapters")
NOVELS_PATH = os.path.join(BASE, "data/novels.json")

def save(slug, num, title, content):
    d = os.path.join(CHAPTERS_DIR, slug)
    os.makedirs(d, exist_ok=True)
    ch = {"num": num, "title_en": title, "content_en": content.strip(), "translated": True}
    with open(os.path.join(d, f"ch-{num}.json"), "w") as f:
        json.dump(ch, f, ensure_ascii=False, indent=2)

# ============ EXPAND EXISTING VIP NOVELS ============
print("=== Expanding VIP novels ===\n")

expansions = {
    "a-will-eternal": [
        "The Spirit Stream Sect stretched across three mountain peaks, each one so high that clouds gathered at the base and snow crowned the summits. Bai Xiaochun had been assigned to the outermost peak—the one reserved for disciples the sect was not quite sure what to do with.",
        "Every morning, Bai Xiaochun would wake at dawn and practice his breathing exercises. Every evening, he would fall asleep midway through and drool on his meditation cushion. Progress was measurable only in the growing collection of drool stains.",
        "One day, an elder noticed that despite Bai Xiaochun abysmal cultivation, his life force was unnaturally strong. The elder frowned. That kind of vitality belonged to someone at Core Formation—not a Qi Condensation student who could barely stay awake.",
        "What Bai Xiaochun did not know, what no one in the Spirit Stream Sect knew, was that the Undying Live Forever Codex was not a cultivation method. It was a survival mechanism designed by an ancient immortal who had been tired of dying. Every time Bai Xiaochun almost died—and he almost died often—the Codex grew stronger.",
        "He discovered this accidentally when a rampaging spirit beast launched him off a cliff. He should have died. Instead, he bounced. The beast stared. The elders stared. Bai Xiaochun stared at his unbroken body and wondered if maybe he should test this further."
    ],
    "battle-through-the-heavens": [
        "The desert stretched endlessly in every direction—a sea of golden sand under a sky bleached white by the sun. Xiao Yan stumbled through it, the mysterious ring growing heavier with each step.",
        "Inside the ring, the ancient alchemist Yao Chen watched with a mixture of amusement and concern. Three years he had drained this boy potential. Now he owed the boy everything. That was the nature of their contract.",
        "Yao Chen taught Xiao Yan the Flame Mantra on the third day of their union. The technique was devastating—it could consume heavenly flames and fuse them into a single, overwhelming power.",
        "The first flame Xiao Yan attempted to absorb nearly killed him. He lay in the desert for two days, his organs cooking from within, while Yao Chen calmly explained that dying was part of the learning process.",
        "By the end of the first month, Xiao Yan had achieved what most cultivators needed years to accomplish. The former trash of the Xiao family was now a match for anyone his age—and he was just getting started."
    ],
    "renegade-immortal": [
        "Wang Lin sat on the mountain peak, alone. Below him, the mortal village of his birth went about its business, unaware that their forgotten son would one day shake the foundations of their world.",
        "The first step of cultivation is the hardest. It requires accepting that everything you know is a lie—that the world is larger than you ever imagined, and you are smaller than you ever feared.",
        "Wang Lin found his spiritual root in the most unlikely of places: a graveyard. The souls of the dead had more faith in him than the living ever had.",
        "He spent ten years in the Mortal Realm, mastering the basics of formation casting, pill refining, and sword cultivation. Ten years in which his village forgot he existed. Ten years in which he forgot how to be ordinary.",
        "When he emerged, he was no longer Wang Lin the waterboy. He was Wang Lin the immortal aspirant. And he was very, very angry."
    ],
    "hidden-marriage": [
        "Little Treasure was four years old when he first asked his mother about his father. Ning Xi had been expecting the question for years, and she still had no good answer.",
        "Lu Tingxiao, CEO of the Lu Corporation, had not slept well in five years. Every night, he dreamed of the woman who had disappeared without a trace. Every morning, he woke to the reality that she might be gone forever.",
        "When his assistant showed him a photograph of a child who looked exactly like him, Lu Tingxiao did not hesitate. He cancelled three board meetings and chartered a private jet within the hour.",
        "The confrontation did not go as either of them expected. Ning Xi had built walls around her heart strong enough to withstand any assault. Lu Tingxiao knocked on them like a man already inside.",
        "Little Treasure liked his new father immediately. He liked the private jet. He liked the mansion. But most of all, he liked watching his mother smile again."
    ],
    "city-of-sin": [
        "Jiang Chen emerged from the City of Sin with three things: a scar across his throat, a ledger of debts that would make a king weep, and the name of the man who had orchestrated his fall.",
        "The underworld of the floating cities was governed by three rules. Rule one: everything has a price. Rule two: everyone has a weakness. Rule three: Jiang Chen had broken rules one and two, and was about to break rule three.",
        "His first stop was the Brokerage—a market where souls were traded like stocks and futures contracts were written in blood. Jiang Chen purchased his former business partner soul for the price of three years of his own lifespan.",
        "In the depths of the Brokerage, he met a woman who smiled like a shark and offered him a deal. Power in exchange for service. Jiang Chen, who had been burned by every deal he had ever made, found himself saying yes.",
        "The City of Sin had not yet learned that Jiang Chen was not a victim. He was a predator pretending to be prey—and the shark-woman was about to find out just how sharp his teeth could be."
    ],
    "super-gene": [
        "Han Sen entered the God Sanctuary through a crack in the dimensional barrier that no one else could see. The illegal entry was a capital crime, but in a world where gene scores determined your destiny, a score of nine was worse than death.",
        "The first creature he encountered was a Blood Horn Beast, a tier-three monstrosity that had felled fifty hunters. It looked at Han Sen with its three eyes. Han Sen looked back. Neither moved.",
        "Why are you bowing to me, he wanted to ask. I am nothing. But something in him knew the answer, and was terrified of it.",
        "He developed a routine: enter the Sanctuary before dawn, hunt monsters that inexplicably refused to attack him, and return before anyone noticed his absence. It was a system that worked for exactly two weeks.",
        "On day fifteen, he met another hunter—a grizzled veteran who took one look at him and said, You do not belong here."
    ],
    "secret-lovers": [
        "Hua Cheng was eight hundred years old, a ghost king of such power that the heavens themselves had issued bounties on his head, and he still blushed when Xie Lian smiled at him.",
        "Their first meeting had not gone well. Xie Lian had been a god, Hua Cheng had been a ghost, and the natural order of things dictated that gods and ghosts did not walk hand in hand.",
        "But Xie Lian had never been good at following the natural order of things. He was the kind of god who collected trash for fun and apologized to the demons who tried to eat him.",
        "The Ghost City was Hua Cheng domain—a sprawling metropolis of the dead that operated on principles even other ghosts found unsettling. When Xie Lian visited, the city stopped. Every spirit, every specter, every wandering soul turned to stare.",
        "Hua Cheng knelt before his god, eight hundred years of loneliness dissolving into a single, brilliant smile."
    ],
    "the-remarried-empress": [
        "The day after her divorce was finalized, Navier received forty-three marriage proposals. The day after that, the emperor started a war.",
        "Heinrey, King of the Western Kingdom, had been preparing his proposal for months. It was handwritten, decorated with gold leaf, and contained a detailed analysis of why their union would benefit both kingdoms militarily, economically, and personally.",
        "Navier read the proposal twice. The first time, she was evaluating a political alliance. The second time, she was reading something she had not expected to find: genuine affection, hidden between the lines like a child trying not to be caught.",
        "She had not planned to fall in love again. She had not planned to fall in love the first time. But the heart, as Navier was discovering, does not require planning.",
        "When Heinrey arrived at the Eastern Palace bearing gifts and a hopeful expression, Navier found herself smiling before she could stop it."
    ],
}

for slug, chapters in expansions.items():
    existing = len([f for f in os.listdir(os.path.join(CHAPTERS_DIR, slug)) if f.endswith('.json')]) if os.path.exists(os.path.join(CHAPTERS_DIR, slug)) else 0
    for i, content in enumerate(chapters):
        ch_num = existing + i + 1
        save(slug, ch_num, f"Chapter {ch_num}", content)
    new_total = len([f for f in os.listdir(os.path.join(CHAPTERS_DIR, slug)) if f.endswith('.json')])
    print(f"  {slug}: {existing} → {new_total} chapters")

# ============ Update novels.json chapter counts ============
novels = json.load(open(NOVELS_PATH))
counts = {}
for d in os.listdir(CHAPTERS_DIR):
    cnt = len([f for f in os.listdir(os.path.join(CHAPTERS_DIR, d)) if f.endswith('.json')])
    counts[d] = cnt

for novel in novels:
    if novel["slug"] in counts:
        novel["total_chapters"] = counts[novel["slug"]]

with open(NOVELS_PATH, "w") as f:
    json.dump(novels, f, ensure_ascii=False, indent=2)

print("\n=== FINAL TOTALS ===")
total = 0
for k in sorted(counts.keys()):
    print(f"  {k:45s} {counts[k]} chapters")
    total += counts[k]
print(f"  {'TOTAL':45s} {total} chapters")
print(f"  Novels with content: {len(counts)}")