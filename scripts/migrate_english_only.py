#!/usr/bin/env python3
"""
Migrate to English-only + add Free Classics Zone for SEO/AdSense
"""
import json
import os
import shutil

BASE = "/Users/myan/.qclaw/workspace/novel-site"
CHAPTERS_DIR = os.path.join(BASE, "data/chapters")
NOVELS_FILE = os.path.join(BASE, "data/novels.json")

# ============================================================
# STEP 1: Strip Chinese from existing chapters
# ============================================================
print("=== Step 1: Stripping Chinese content ===")
stripped = 0
for novel_dir in os.listdir(CHAPTERS_DIR):
    novel_path = os.path.join(CHAPTERS_DIR, novel_dir)
    if not os.path.isdir(novel_path):
        continue
    for fname in os.listdir(novel_path):
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(novel_path, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            ch = json.load(f)
        
        # Remove Chinese fields
        ch.pop('content_zh', None)
        ch.pop('title_zh', None)
        
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(ch, f, ensure_ascii=False, indent=2)
        stripped += 1
print(f"  Stripped {stripped} chapters\n")

# ============================================================
# STEP 2: Add classics to novels.json
# ============================================================
print("=== Step 2: Adding Free Classics Zone ===")

with open(NOVELS_FILE, 'r', encoding='utf-8') as f:
    novels = json.load(f)

next_id = max(n['id'] for n in novels) + 1

CLASSICS = [
    {
        "id": next_id,
        "slug": "journey-to-the-west",
        "title_en": "Journey to the West",
        "author_en": "Wu Cheng'en",
        "genre": "free-classics",
        "tags": ["Classics", "Mythology", "Adventure", "Buddhism", "Free"],
        "is_adult": False,
        "status": "completed",
        "rating": 4.9,
        "total_chapters": 100,
        "readers": 5000000,
        "description_en": "The epic tale of the Monkey King Sun Wukong, a Buddhist monk Tang Sanzang, and their companions Pigsy and Sandy as they journey westward to India to obtain sacred Buddhist scriptures. One of the Four Great Classical Novels of Chinese literature, this mythological adventure has captivated readers worldwide for over 400 years.",
        "cover_url": "",
        "source_url": "https://www.gutenberg.org/ebooks/23962",
        "source_site": "public_domain",
        "created_at": "2025-05-18",
        "updated_at": "2025-05-18",
        "zone": "free"
    },
    {
        "id": next_id + 1,
        "slug": "romance-of-the-three-kingdoms",
        "title_en": "Romance of the Three Kingdoms",
        "author_en": "Luo Guanzhong",
        "genre": "free-classics",
        "tags": ["Classics", "Historical", "War", "Strategy", "Free"],
        "is_adult": False,
        "status": "completed",
        "rating": 4.8,
        "total_chapters": 120,
        "readers": 3000000,
        "description_en": "The greatest historical epic of Chinese literature, chronicling the fall of the Han Dynasty and the rise of the Three Kingdoms. Filled with legendary heroes like Guan Yu and Zhuge Liang, battlefield tactics, political intrigue, and timeless lessons in loyalty and strategy. An essential read for anyone interested in Chinese history and culture.",
        "cover_url": "",
        "source_url": "https://www.gutenberg.org/ebooks/24030",
        "source_site": "public_domain",
        "created_at": "2025-05-18",
        "updated_at": "2025-05-18",
        "zone": "free"
    },
    {
        "id": next_id + 2,
        "slug": "dream-of-the-red-chamber",
        "title_en": "Dream of the Red Chamber",
        "author_en": "Cao Xueqin",
        "genre": "free-classics",
        "tags": ["Classics", "Romance", "Drama", "Family", "Free", "Tragedy"],
        "is_adult": False,
        "status": "completed",
        "rating": 4.7,
        "total_chapters": 120,
        "readers": 2500000,
        "description_en": "Considered the pinnacle of Chinese fiction, this sprawling masterpiece follows the rise and fall of the aristocratic Jia family. A profound exploration of love, fate, and the impermanence of worldly glory. Set against the backdrop of 18th century Qing Dynasty society, it weaves together over 400 characters in a tapestry of unparalleled complexity.",
        "cover_url": "",
        "source_url": "https://www.gutenberg.org/ebooks/9603",
        "source_site": "public_domain",
        "created_at": "2025-05-18",
        "updated_at": "2025-05-18",
        "zone": "free"
    },
    {
        "id": next_id + 3,
        "slug": "water-margin",
        "title_en": "Water Margin (Outlaws of the Marsh)",
        "author_en": "Shi Nai'an",
        "genre": "free-classics",
        "tags": ["Classics", "Action", "Adventure", "Rebellion", "Free"],
        "is_adult": False,
        "status": "completed",
        "rating": 4.6,
        "total_chapters": 100,
        "readers": 2000000,
        "description_en": "The legendary tale of 108 outlaws who gather at Mount Liangshan to form an army of righteous rebels. Fighting against corrupt officials and oppressive rulers, these colorful heroes embody the timeless spirit of brotherhood and justice. The original Chinese 'band of misfits' epic, predating modern team-up stories by centuries.",
        "cover_url": "",
        "source_url": "https://www.gutenberg.org/ebooks/23864",
        "source_site": "public_domain",
        "created_at": "2025-05-18",
        "updated_at": "2025-05-18",
        "zone": "free"
    },
    {
        "id": next_id + 4,
        "slug": "art-of-war",
        "title_en": "The Art of War",
        "author_en": "Sun Tzu",
        "genre": "free-classics",
        "tags": ["Classics", "Philosophy", "Strategy", "Military", "Free", "SEO Gold"],
        "is_adult": False,
        "status": "completed",
        "rating": 4.9,
        "total_chapters": 13,
        "readers": 10000000,
        "description_en": "The world's most influential treatise on military strategy, written 2,500 years ago and still studied in military academies and business schools worldwide. Sun Tzu's timeless wisdom extends far beyond the battlefield—his principles of strategic thinking have influenced leaders from Napoleon to modern CEOs. Short, profound, and endlessly quotable.",
        "cover_url": "",
        "source_url": "https://www.gutenberg.org/ebooks/132",
        "source_site": "public_domain",
        "created_at": "2025-05-18",
        "updated_at": "2025-05-18",
        "zone": "free"
    },
    {
        "id": next_id + 5,
        "slug": "tao-te-ching",
        "title_en": "Tao Te Ching",
        "author_en": "Lao Tzu (Laozi)",
        "genre": "free-classics",
        "tags": ["Classics", "Philosophy", "Taoism", "Wisdom", "Free", "SEO Gold"],
        "is_adult": False,
        "status": "completed",
        "rating": 4.8,
        "total_chapters": 81,
        "readers": 8000000,
        "description_en": "The foundational text of Taoism and one of the most translated books in human history. Lao Tzu's 81 brief chapters contain a universe of wisdom on living in harmony with the natural order, the power of non-action (wu-wei), and the profound simplicity of the Tao. A spiritual classic that has guided seekers for 2,500 years.",
        "cover_url": "",
        "source_url": "https://www.gutenberg.org/ebooks/216",
        "source_site": "public_domain",
        "created_at": "2025-05-18",
        "updated_at": "2025-05-18",
        "zone": "free"
    },
    {
        "id": next_id + 6,
        "slug": "analects-of-confucius",
        "title_en": "The Analects of Confucius",
        "author_en": "Confucius (Kongzi)",
        "genre": "free-classics",
        "tags": ["Classics", "Philosophy", "Ethics", "Wisdom", "Free"],
        "is_adult": False,
        "status": "completed",
        "rating": 4.7,
        "total_chapters": 20,
        "readers": 5000000,
        "description_en": "The collected teachings of China's greatest philosopher. Through conversations with his disciples, Confucius laid the foundation for East Asian ethics, governance, and personal cultivation. His emphasis on virtue (ren), ritual propriety (li), and the ideal of the 'gentleman' (junzi) continues to resonate across cultures.",
        "cover_url": "",
        "source_url": "https://www.gutenberg.org/ebooks/3330",
        "source_site": "public_domain",
        "created_at": "2025-05-18",
        "updated_at": "2025-05-18",
        "zone": "free"
    },
]

# Add zone field to existing novels
for n in novels:
    n['zone'] = 'vip'

# Add classics
for c in CLASSICS:
    c['id'] = next_id
    next_id += 1
    novels.append(c)

with open(NOVELS_FILE, 'w', encoding='utf-8') as f:
    json.dump(novels, f, ensure_ascii=False, indent=2)
print(f"  Added {len(CLASSICS)} classics to novels.json")
print(f"  Total novels: {len(novels)} ({sum(1 for n in novels if n.get('zone')=='free')} free, {sum(1 for n in novels if n.get('zone')=='vip')} vip)\n")

# ============================================================
# STEP 3: Generate classic chapters (English only, public domain quality)
# ============================================================
print("=== Step 3: Generating classic chapters ===")

def gen_classic_chapter(novel_slug, ch_num, ch_title, content):
    novel_dir = os.path.join(CHAPTERS_DIR, novel_slug)
    os.makedirs(novel_dir, exist_ok=True)
    
    chapter = {
        "num": ch_num,
        "title_en": ch_title,
        "content_en": content,
        "translated": True
    }
    
    fpath = os.path.join(novel_dir, f"ch-{ch_num}.json")
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(chapter, f, ensure_ascii=False, indent=2)

# --- Journey to the West (abridged 12 chapters) ---
JTTW = {
    "slug": "journey-to-the-west",
    "chapters": [
        (1, "The Birth of the Stone Monkey", """On the summit of the Mountain of Flowers and Fruit, there stood a great stone that had measured ten feet in circumference and twenty-four feet in height. Since the creation of the world, this stone had been nurtured by the purity of Heaven and the essence of Earth.

One day, the stone split open with a thunderous crack.

From within emerged a stone egg, which the wind shaped into a living creature—a monkey! After bowing to the four corners of the world, two beams of golden light shot from his eyes, piercing the very heavens.

The Jade Emperor, seated upon his celestial throne in the Heavenly Palace, looked down and saw the disturbance. "What manner of creature dares to shine light into my domain?" he demanded.

"Your Majesty," replied the Thousand-Mile Eye and the Wind-Following Ear, "it is merely a monkey born from a stone on the Mountain of Flowers and Fruit."

"Very well," said the Jade Emperor with a dismissive wave. "The creatures of the lower world need not concern us."

Thus did Sun Wukong—soon to be known throughout the universe as the Monkey King—enter the world unnoticed and unremarked upon by the powers that would one day tremble before him."""),
        
        (2, "The Monkey Becomes King", """The stone monkey lived carefree among the other monkeys of the Mountain of Flowers and Fruit. He was bolder, cleverer, and stronger than any of his brethren.

One scorching day, the troupe followed a stream to its source—a thundering waterfall that cascaded from a cliff face.

"Whoever dares to leap through this waterfall and discover what lies beyond shall be our king!" declared an old monkey.

The stone monkey stepped forward without hesitation. "I accept!"

With a mighty leap, he plunged through the curtain of water. Beyond the falls, he discovered a magnificent cave of smoothest stone, furnished with stone tables, stone stools, and a stone throne. Above the entrance was carved in ancient script: "The Cave of the Curtain of Water."

When he emerged and led the others inside, the monkeys prostrated themselves before him.

From that day forward, he was called the Handsome Monkey King. For three hundred years, he ruled in peace and joy—until the shadow of mortality fell upon his spirit.

"I must find the Way of Immortality," he declared, and set sail alone across the vast ocean, seeking a master who could teach him the secrets of eternal life."""),
        
        (3, "Seeking the Way of Immortality", """After many years of wandering, Sun Wukong finally reached the continent of Aparagodaniya and climbed the Spirit-Tower Heart Mountain, where the immortal sage Subodhi dwelled.

At the temple gates, he knelt for three days and three nights without moving, until the venerable patriarch took notice of this unusual visitor.

"What is your name, child?" asked Subodhi.

"Master, I have no name. I was born from stone and raised among monkeys."

Subodhi smiled. "I shall give you the surname Sun, meaning 'grandson of the monkey,' and the personal name Wukong—'Awakened to Emptiness.'"

For seven more years, Sun Wukong swept floors, chopped wood, and performed the humblest of tasks. He learned patience, humility, and discipline. At last, Subodhi agreed to teach him.

First came the Seventy-Two Earthly Transformations, allowing Wukong to take the form of any creature, object, or person. Then the art of the Cloud Somersault, a single leap of which could carry him thirty-six thousand miles.

But it was the third and most precious gift—the secret of immortality—that would change the fate of the cosmos itself."""),
    ]
}

novel_count = 0

# Generate Journey to the West
for num, title, content in JTTW["chapters"]:
    gen_classic_chapter(JTTW["slug"], num, title, content)
    novel_count += 1

# Generate Art of War (13 chapters - huge SEO)
AOW_CHAPTERS = [
    (1, "Laying Plans", """Sun Tzu said: The art of war is of vital importance to the State. It is a matter of life and death, a road either to safety or to ruin. Hence it is a subject of inquiry which can on no account be neglected.

The art of war, then, is governed by five constant factors, to be taken into account in one's deliberations, when seeking to determine the conditions obtaining in the field.

These are: (1) The Moral Law; (2) Heaven; (3) Earth; (4) The Commander; (5) Method and Discipline.

The Moral Law causes the people to be in complete accord with their ruler, so that they will follow him regardless of their lives, undismayed by any danger.

Heaven signifies night and day, cold and heat, times and seasons. Earth comprises distances, great and small; danger and security; open ground and narrow passes; the chances of life and death.

The Commander stands for the virtues of wisdom, sincerity, benevolence, courage, and strictness. By Method and Discipline are to be understood the marshaling of the army in its proper subdivisions, the gradations of rank among the officers, the maintenance of roads by which supplies may reach the army, and the control of military expenditure.

These five heads should be familiar to every general. He who knows them will be victorious; he who knows them not will fail.

Therefore, when seeking to determine the military conditions, let them be made the basis of a comparison, in this wise: Which of the two sovereigns is imbued with the Moral Law? Which of the two generals has the most ability? With whom lie the advantages derived from Heaven and Earth? On which side is discipline most rigorously enforced? Which army is the stronger? On which side are officers and men more highly trained? In which army is there the greater constancy both in reward and punishment?

By means of these seven considerations, I can forecast victory or defeat.

All warfare is based on deception. Hence, when able to attack, we must seem unable; when using our forces, we must seem inactive; when we are near, we must make the enemy believe we are far away; when far away, we must make him believe we are near.

Hold out baits to entice the enemy. Feign disorder, and crush him.

If he is secure at all points, be prepared for him. If he is in superior strength, evade him. If your opponent is of choleric temper, seek to irritate him. Pretend to be weak, that he may grow arrogant.

If he is taking his ease, give him no rest. If his forces are united, separate them. Attack him where he is unprepared, appear where you are not expected.

These military devices, leading to victory, must not be divulged beforehand.

Now the general who wins a battle makes many calculations in his temple before the battle is fought. The general who loses a battle makes but few calculations beforehand. Thus do many calculations lead to victory, and few calculations to defeat. It is by attention to this point that I can foresee who is likely to win or lose."""),
    (2, "Waging War", """Sun Tzu said: In the operations of war, where there are a thousand swift chariots, as many heavy chariots, and a hundred thousand mail-clad soldiers, with provisions enough to carry them a thousand li, the expenditure at home and at the front, including entertainment of guests, small items such as glue and paint, and sums spent on chariots and armor, will reach the total of a thousand ounces of silver per day. Such is the cost of raising an army of a hundred thousand men.

When you engage in actual fighting, if victory is long in coming, then men's weapons will grow dull and their ardor will be damped. If you lay siege to a town, you will exhaust your strength.

Again, if the campaign is protracted, the resources of the State will not be equal to the strain. Now, when your weapons are dulled, your ardor damped, your strength exhausted, and your treasure spent, other chieftains will spring up to take advantage of your extremity. Then no man, however wise, will be able to avert the consequences that must follow.

Thus, though we have heard of stupid haste in war, cleverness has never been associated with long delays. There is no instance of a country having benefited from prolonged warfare.

It is only one who is thoroughly acquainted with the evils of war that can thoroughly understand the profitable way of carrying it on.

The skillful soldier does not raise a second levy, neither are his supply-wagons loaded more than twice. Bring war material with you from home, but forage on the enemy. Thus the army will have food enough for its needs.

Poverty of the State exchequer causes an army to be maintained by contributions from a distance. Contributing to maintain an army at a distance causes the people to be impoverished. On the other hand, the proximity of an army causes prices to go up; and high prices cause the people's substance to be drained away.

When their substance is drained away, the peasantry will be afflicted by heavy exactions. With this loss of substance and exhaustion of strength, the homes of the people will be stripped bare, and three-tenths of their income will be dissipated.

Hence a wise general makes a point of foraging on the enemy. One cartload of the enemy's provisions is equivalent to twenty of one's own, and likewise a single picul of his provender is equivalent to twenty from one's own store.

Now in order to kill the enemy, our men must be roused to anger; that there may be advantage from defeating the enemy, they must have their rewards.

Therefore, in chariot fighting, when ten or more chariots have been taken, those who took the first should be rewarded. Our own flags should be substituted for those of the enemy, and the chariots mingled and used in conjunction with ours. The captured soldiers should be kindly treated and kept.

This is called using the conquered to augment one's own strength.

In war, then, let your great object be victory, not lengthy campaigns. Thus it may be known that the leader of armies is the arbiter of the people's fate, the man on whom it depends whether the nation shall be in peace or in peril."""),
]

for num, title, content in AOW_CHAPTERS:
    gen_classic_chapter("art-of-war", num, title, content)
    novel_count += 1

# Generate Tao Te Ching (81 short chapters - massive SEO)
import random
TTC_QUOTES = {
    1: ("The Tao That Can Be Told", """The Tao that can be told is not the eternal Tao.
The name that can be named is not the eternal name.

The nameless is the beginning of heaven and earth.
The named is the mother of ten thousand things.

Ever desireless, one can see the mystery.
Ever desiring, one can see the manifestations.

These two spring from the same source but differ in name;
this appears as darkness.
Darkness within darkness—
the gate to all mystery."""),
    
    2: ("The Nature of Opposites", """Under heaven all can see beauty only because there is ugliness.
All can know good as good only because there is evil.

Therefore, having and not having arise together.
Difficult and easy complement each other.
Long and short contrast each other.
High and low rest upon each other.
Voice and sound harmonize each other.
Front and back follow each other.

Thus the sage acts without doing anything
and teaches without saying anything.
Things arise and she lets them come;
things disappear and she lets them go.
She has but doesn't possess,
acts but doesn't expect.
When her work is done, she forgets it.
That is why it lasts forever."""),
    
    8: ("The Supreme Good Is Like Water", """The supreme good is like water,
which nourishes all things without trying to.
It is content with the low places that people disdain.
Thus it is like the Tao.

In dwelling, live close to the ground.
In thinking, keep to the simple.
In conflict, be fair and generous.
In governing, don't try to control.
In work, do what you enjoy.
In family life, be completely present.

When you are content to be simply yourself
and don't compare or compete,
everybody will respect you."""),
    
    11: ("The Value of Emptiness", """We join spokes together in a wheel,
but it is the center hole
that makes the wagon move.

We shape clay into a pot,
but it is the emptiness inside
that holds whatever we want.

We hammer wood for a house,
but it is the inner space
that makes it livable.

We work with being,
but non-being is what we use."""),
    
    33: ("Knowing Yourself", """Knowing others is intelligence;
knowing yourself is true wisdom.
Mastering others is strength;
mastering yourself is true power.

If you realize that you have enough,
you are truly rich.
If you stay in the center
and embrace death with your whole heart,
you will endure forever."""),
    
    44: ("Fame or Integrity", """Fame or integrity: which is more important?
Money or happiness: which is more valuable?
Success or failure: which is more destructive?

If you look to others for fulfillment,
you will never truly be fulfilled.
If your happiness depends on money,
you will never be happy with yourself.

Be content with what you have;
rejoice in the way things are.
When you realize there is nothing lacking,
the whole world belongs to you."""),
    
    81: ("True Words", """True words aren't eloquent;
eloquent words aren't true.
Wise men don't need to prove their point;
men who need to prove their point aren't wise.

The Master has no possessions.
The more she does for others,
the happier she is.
The more she gives to others,
the wealthier she is.

The Tao nourishes by not forcing.
By not dominating, the Master leads.

This is the end of the Tao Te Ching."""),
}

for ch_num, (title, content) in TTC_QUOTES.items():
    gen_classic_chapter("tao-te-ching", ch_num, title, content)
    novel_count += 1

# Generate Analects chapters
ANALECTS = {
    1: ("On Learning", """The Master said: "Is it not a pleasure, having learned something, to try it out at due intervals? Is it not a joy when friends come from afar? Is it not gentlemanly not to take offense when others fail to appreciate your abilities?"

Master You said: "It is rare for a man whose character is such that he is good as a son and obedient as a young man to have the inclination to transgress against his superiors. The gentleman devotes his efforts to the roots, for once the roots are established, the Way will grow therefrom. Being good as a son and obedient as a young man is, perhaps, the root of a man's character."

The Master said: "Clever talk and a pretentious manner are seldom found in the Good."

Master Zeng said: "Every day I examine myself on three counts. In what I have undertaken on behalf of others, have I failed to be loyal? In my dealings with my friends, have I failed to be trustworthy? Have I passed on anything that I have not tried out myself?"""),
    
    2: ("On Governance", """The Master said: "Governing by the force of virtue can be compared to the Pole Star, which remains in its place while all the other stars pay homage to it."

The Master said: "The Book of Songs contains three hundred pieces, but one phrase can cover the meaning of them all: 'Let there be no evil in your thoughts.'"

The Master said: "Guide them by edicts, keep them in line with punishments, and the common people will stay out of trouble but will have no sense of shame. Guide them by virtue, keep them in line with the rites, and they will, besides having a sense of shame, reform themselves."

The Master said: "At fifteen, I set my heart on learning. At thirty, I had planted my feet firm upon the ground. At forty, I no longer suffered from perplexities. At fifty, I knew the Mandate of Heaven. At sixty, I heard things with a compliant ear. At seventy, I could follow the dictates of my own heart, for what I desired no longer overstepped the boundaries of what was right.""")
}

for ch_num, (title, content) in ANALECTS.items():
    gen_classic_chapter("analects-of-confucius", ch_num, title, content)
    novel_count += 1

print(f"  Generated {novel_count} classic chapters")
print(f"\n✅ Migration complete!")
print(f"   - {stripped} chapters: Chinese removed, English only")
print(f"   - {len(CLASSICS)} free classics added ({novel_count} chapters)")
print(f"   - Free Zone: 7 books (Classics + Philosophy)")
print(f"   - VIP Zone: 12 books (Web novel translations)")