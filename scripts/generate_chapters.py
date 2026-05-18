#!/usr/bin/env python3
"""生成种子章节数据"""
import json
import os

CHAPTERS_DIR = "/Users/myan/.qclaw/workspace/novel-site/data/chapters"

NOVELS = {
    "martial-god-asura": {
        "title_zh": "武神至尊",
        "title_en": "Martial God Asura",
        "content_template": """
少年站在巨大的青铜鼎前，汗水顺着脸颊滑落。
{chapter_num}天的苦修，已让他的双手布满老茧。但那双眼睛里燃烧的火焰，比训练场上的篝火还要炽烈。
"还不够。"他低声自语，又一次将灵力注入双臂。
青铜鼎纹丝不动。
四周响起了窃窃私语。
"看，那个废物又在丢人现眼了。"
"区区外门弟子，还想挪动玄铁鼎？"
少年充耳不闻。他感受着一股从未体会过的力量在他的经脉中缓缓流淌——
那是丹田深处那颗神秘珠子散发的温热。
突然，青铜鼎微微一晃。
所有声音戛然而止。
少年嘴角扬起一丝弧度。这，只是开始。
"""
    },
    "against-the-gods": {
        "title_zh": "逆天邪神",
        "title_en": "Against the Gods",
        "content_template": """
{quote}
鲜血从指缝间滴落，在青石板上晕开一朵朵触目惊心的血花。
云澈缓缓站直身体。他的经脉尽断，丹田空空如也。在这苍风大陆，这就是废人中的废人。
但他没有倒下。
因为那颗从天外坠落的珠子，正在他的体内发出第一缕光芒。
"这是什么……"
一股从未感受过的力量，如同洪水般涌入四经八脉。那些断裂的经脉，在这股力量的冲刷下，竟开始以肉眼可见的速度愈合。
不，不仅是愈合。
每一根经脉都比原来宽阔了十倍不止。
云澈抬起头。他知道，从这一刻起，属于他的故事，刚刚开始。
"""
    },
    "i-shall-seal-the-heavens": {
        "title_zh": "我欲封天",
        "title_en": "I Shall Seal the Heavens",
        "content_template": """
山风呼啸，残阳如血。
孟浩站在靠山宗的悬崖边，手中那面铜镜映出他消瘦的脸庞。
三次科举，三次名落孙山。
他被强行带到这里时，以为此生再无希望。修真界？那是神仙的事情，与他一个文弱书生何干？
然而铜镜里，他看到的不再是自己的倒影。
那是一扇门。
一扇通往无尽可能的门。
孟浩闭上眼，再睁开时，他的气质已完全不同。他不再是一个落第书生，而是一个即将踏上封天之路的修士。
"从今日起，我孟浩，要封这片天。"
"""
    },
    "reverend-insanity": {
        "title_zh": "蛊真人",
        "title_en": "Reverend Insanity",
        "content_template": """
黑暗，无边的黑暗。
方源睁开眼时，发现自己躺在血迹斑斑的石台上。四周是腐朽的铁链和早已干涸的血痕。
他的嘴角浮现一抹冷笑。
别人重生，是天命所归，是逆天改命。
而他方源重生，只是为了完成一件小事——
杀回那个地方，亲手捏碎那些背叛者的喉咙。
他抬起手，一只漆黑的蛊虫从掌心钻出，发出令人牙酸的咀嚼声。
"老伙计，我们又见面了。"
这一次，他不会心慈手软。
这一次，他要让整个蛊道颤抖。
"""
    },
}

CHAPTER_TITLES = [
    ("废柴少年", "The Useless Youth"),
    ("神秘至宝", "The Mysterious Treasure"),
    ("天地异象", "Celestial Omen"),
    ("初次修炼", "First Cultivation"),
    ("突破瓶颈", "Breaking Through"),
    ("宗门试炼", "Sect Trial"),
    ("初露锋芒", "First Display of Strength"),
    ("仇人相见", "Meeting the Enemy"),
    ("神秘山洞", "The Mysterious Cave"),
    ("上古遗迹", "Ancient Ruins"),
    ("妖兽山谷", "Demon Beast Valley"),
    ("生死之战", "Battle of Life and Death"),
    ("惊天逆转", "Shocking Reversal"),
    ("天降机缘", "Fortune from Heaven"),
    ("实力暴涨", "Surge in Power"),
    ("以弱胜强", "Weak Overcomes Strong"),
    ("秘境开启", "Secret Realm Opens"),
    ("大战强敌", "Fighting the Powerful Enemy"),
    ("境界突破", "Realm Breakthrough"),
    ("名动天下", "Fame Across the World"),
]

QUOTES = [
    "命运的齿轮，在他最不经意的那一刻，悄然转动。",
    "天不佑我，我便逆天。",
    "有些人，生来就是为了打破规则的。",
    "弱者向命运低头，强者让命运低头。",
    "每个人心中都有一座山，翻过去，便是新世界。",
    "这世间，从来没有绝对的公平，除非你亲手去创造。",
    "十年磨一剑，霜刃未曾试。今日把示君，谁有不平事。",
    "所谓天才，不过是把别人喝咖啡的时间，用在了修炼上。",
]

import random

def generate_chapters(novel_slug, novel_info, count=20):
    novel_dir = os.path.join(CHAPTERS_DIR, novel_slug)
    os.makedirs(novel_dir, exist_ok=True)
    
    for i in range(count):
        ch_num = i + 1
        if i < len(CHAPTER_TITLES):
            zh_title, en_title = CHAPTER_TITLES[i]
        else:
            zh_title = f"第{ch_num}章"
            en_title = f"Chapter {ch_num}"
        
        content_zh = novel_info["content_template"].format(
            chapter_num=ch_num,
            quote=random.choice(QUOTES)
        ).strip()
        
        # 生成英文翻译（模拟翻译质量）
        content_en = generate_english_content(content_zh, novel_info["title_en"], ch_num)
        
        chapter = {
            "num": ch_num,
            "title_zh": zh_title,
            "title_en": en_title,
            "content_zh": content_zh,
            "content_en": content_en,
            "translated": True
        }
        
        filepath = os.path.join(novel_dir, f"ch-{ch_num}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(chapter, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ {novel_slug}/ch-{ch_num}.json")
    
    print(f"✅ {novel_info['title_en']}: {count} chapters generated")

def generate_english_content(zh_text, title, ch_num):
    """生成模拟英文翻译"""
    templates = {
        "martial-god-asura": f"""The young man stood before the massive bronze cauldron, sweat sliding down his cheeks.

{ch_num} days of grueling training had left his hands covered in calluses. But the fire burning in his eyes burned brighter than the bonfires on the training ground.

"Not enough," he murmured to himself, channeling his spiritual energy into his arms once more.

The bronze cauldron remained motionless.

Whispers erupted around him.

"Look, that useless waste is embarrassing himself again."

"A mere outer disciple thinks he can move the Black Iron Cauldron?"

The young man paid no attention. He felt an unfamiliar power flowing slowly through his meridians—a warmth emanating from the mysterious pearl deep within his dantian.

Suddenly, the bronze cauldron trembled slightly.

Every voice fell silent.

A slight curve appeared at the corner of the young man's lips. This was only the beginning.

---
*Chapter {ch_num}: Each day brought him closer to his destiny. The path of the Martial God was not walked in a single step, but forged through countless battles against oneself.*""",
        
        "against-the-gods": f"""Blood dripped from between his fingers, blooming into startling crimson blossoms on the blue stone floor.

Yun Che slowly straightened his body. His meridians were shattered, his dantian empty as a void. In the Azure Wind Continent, this was the definition of worthless—a waste among wastes.

But he did not fall.

Because the pearl that had fallen from beyond the heavens was emitting its first ray of light within his body.

"What is this..."

A power unlike anything he had ever felt surged through his broken meridians like a flood. The shattered pathways began healing at a speed visible to the naked eye.

No—not merely healing.

Every meridian was expanding, becoming ten times wider than before.

Yun Che raised his head. He knew that from this moment on, his story had truly begun.

---
*Chapter {ch_num}: Fate had finally turned its gaze upon him. The crippled youth who had been trampled into the dust would soon make the heavens themselves tremble.*""",
        
        "i-shall-seal-the-heavens": f"""The mountain wind howled as the setting sun painted the sky crimson.

Meng Hao stood at the edge of the cliff, the bronze mirror in his hand reflecting his gaunt face.

Three imperial examinations. Three failures.

When he was forcibly taken to the Reliance Sect, he thought his life held no more hope. The cultivation world? That was the business of immortals—what did it have to do with a frail scholar?

But in the bronze mirror, he no longer saw his own reflection.

He saw a door.

A door leading to infinite possibilities.

Meng Hao closed his eyes. When he opened them again, his entire bearing had changed. He was no longer a failed scholar, but a cultivator about to embark on the path of sealing the heavens.

"From this day forward, I, Meng Hao, shall seal... this heaven."

---
*Chapter {ch_num}: Sometimes the greatest journeys begin not with a step forward, but with the courage to look in the mirror and see who you truly are.*""",
        
        "reverend-insanity": f"""Darkness. Endless darkness.

When Fang Yuan opened his eyes, he found himself lying on a blood-stained stone platform. Rusted chains surrounded him alongside long-dried pools of blood.

A cold smile spread across his lips.

When others are reborn, it is destiny's calling, a chance to defy the heavens.

But Fang Yuan was reborn for a single, simple purpose—

To slaughter his way back to that place and personally crush the throats of those who had betrayed him.

He raised his hand. A pitch-black Gu worm emerged from his palm, emitting a grating chewing sound.

"Old friend, we meet again."

This time, there would be no mercy.

This time, he would make the entire Gu Dao tremble.

---
*Chapter {ch_num}: In a world where only the ruthless survive, Fang Yuan was determined to become the most ruthless of all. The Reverend of Insanity had returned.*"""
    }
    
    return templates.get(title.lower().replace(" ", "-"), f"Chapter {ch_num}\n\nThe path of cultivation is long and treacherous. Each step forward brings new challenges and new revelations.\n\n---\n*This chapter is being translated. Please check back soon.*")

if __name__ == "__main__":
    for slug, info in NOVELS.items():
        generate_chapters(slug, info, count=20)
    
    print(f"\n🎉 All done! Generated content for {len(NOVELS)} novels, 20 chapters each.")
    print(f"   Total: {len(NOVELS) * 20} chapter files")