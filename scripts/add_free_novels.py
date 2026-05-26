#!/usr/bin/env python3
"""Add 6 new free novels + reorganize novels list (2VIP, 1FREE interleaved)."""
import json, os, glob

DATA_DIR = '/Users/myan/.qclaw/workspace/novel-site/data'
CHAPTERS_DIR = os.path.join(DATA_DIR, 'chapters')
os.makedirs(CHAPTERS_DIR, exist_ok=True)

def write_chapter(slug, num, title, content):
    path = os.path.join(CHAPTERS_DIR, f'{slug}_{num}.json')
    with open(path, 'w') as f:
        json.dump({'title': title, 'content': content.strip()}, f, ensure_ascii=False)

# ── New Free Novels ─────────────────────────────────────────
NEW_FREE = [
    {
        'slug': 'strange-tales-chinese-studio',
        'title_en': 'Strange Tales from a Chinese Studio',
        'title_cn': '聊斋志异', 'author_en': 'Pu Songling', 'author_cn': '蒲松龄',
        'cover': '/covers/strange-tales.jpg', 'zone': 'free',
        'tags': ['supernatural','fox-spirits','classic','horror','romance'],
        'description': 'Nearly 500 supernatural tales from Qing Dynasty China. Fox spirits, ghosts, and immortals walk among mortals in this timeless classic of Chinese weird fiction.',
        'total_chapters': 12, 'rating': 4.6, 'reads': 156000, 'status': 'completed',
    },
    {
        'slug': 'investiture-of-the-gods',
        'title_en': 'Investiture of the Gods',
        'title_cn': '封神演义', 'author_en': 'Xu Zhonglin', 'author_cn': '许仲琳',
        'cover': '/covers/investiture-gods.jpg', 'zone': 'free',
        'tags': ['mythology','gods','epic','classic','war'],
        'description': 'The great war between the Shang and Zhou dynasties becomes a battlefield for gods and demons. Jiang Ziya must bestow divine titles upon the fallen.',
        'total_chapters': 12, 'rating': 4.7, 'reads': 189000, 'status': 'completed',
    },
    {
        'slug': 'gullivers-travels',
        'title_en': "Gulliver's Travels",
        'title_cn': '格列佛游记', 'author_en': 'Jonathan Swift', 'author_cn': '乔纳森·斯威夫特',
        'cover': '/covers/gulliver.jpg', 'zone': 'free',
        'tags': ['adventure','fantasy','classic','satire'],
        'description': "Lemuel Gulliver voyages to Lilliput, Brobdingnag, Laputa, and beyond — a timeless adventure of wonder, satire, and dark truth about human nature.",
        'total_chapters': 8, 'rating': 4.3, 'reads': 320000, 'status': 'completed',
    },
    {
        'slug': 'creation-of-the-gods',
        'title_en': 'Creation of the Gods',
        'title_cn': '开天辟地', 'author_en': 'Nexus Tales', 'author_cn': '裂缝故事',
        'cover': '/covers/creation-gods.jpg', 'zone': 'free',
        'tags': ['mythology','creation','origins','pantheon'],
        'description': 'Before heaven and earth, there was chaos. Witness the birth of Pangu, the mending of the sky by Nüwa, and the first gods taking their celestial thrones.',
        'total_chapters': 7, 'rating': 4.4, 'reads': 41000, 'status': 'completed',
    },
    {
        'slug': 'monkey-kings-birth',
        'title_en': "The Monkey King's Birth",
        'title_cn': '美猴王出世', 'author_en': 'Nexus Tales', 'author_cn': '裂缝故事',
        'cover': '/covers/monkey-king-birth.jpg', 'zone': 'free',
        'tags': ['cultivation','origins','mythology','adventure','humor'],
        'description': 'From a stone egg atop the Mountain of Flowers and Fruit, Sun Wukong is born. Follow his earliest days: the discovery of the Water Curtain Cave, his quest for immortality, and the mischief that makes him legend.',
        'total_chapters': 8, 'rating': 4.8, 'reads': 87000, 'status': 'completed',
    },
    {
        'slug': 'white-snake-legend',
        'title_en': 'Legend of the White Snake',
        'title_cn': '白蛇传', 'author_en': 'Nexus Tales', 'author_cn': '裂缝故事',
        'cover': '/covers/white-snake.jpg', 'zone': 'free',
        'tags': ['romance','supernatural','immortal','tragedy'],
        'description': 'A thousand-year-old white snake spirit falls in love with a mortal man at West Lake. One of China\'s Four Great Folktales, retold for modern readers.',
        'total_chapters': 8, 'rating': 4.6, 'reads': 124000, 'status': 'completed',
    },
]

# ── Chapter content ────────────────────────────────────────
CHAPTERS = {
    'strange-tales-chinese-studio': [
        ('Chapter 1: The Painted Skin',
         """It was the seventh month, when the veil between worlds grows thin. Wang Sheng, a young scholar on his way to the provincial examinations, met a woman weeping by the roadside under the moonlight.

She was beautiful beyond mortal measure — skin like jade, eyes dark as ink pools.

"Miss, why do you weep alone at this hour?" he asked.

"My husband has cast me out," she said, her voice like wind through bamboo. "I have nowhere to go."

Wang Sheng offered her shelter in his study. His wife protested, but he would not listen. For days, the woman remained. Wang neglected his books, his wife, his duties.

One night, a Taoist priest stopped him on the street. "Young man, what evil have you invited into your home?"

"None. Only an abandoned woman."

The priest sighed. "Go home. Look through your study window. But do not enter until you have seen the truth."

Wang returned. Peering through a crack in the paper screen, what he saw froze the blood in his veins.

A monstrous creature sat at his desk — green-faced, fanged, its body covered in bristling hair. On the bed lay a human skin, painted exquisitely with the features of the beautiful woman. The creature lifted the skin, shook it out like a robe, and stepped into it — becoming the woman who had wept in the moonlight.

Wang fled. The priest gave him a fly-whisk dipped in sacred water. "Hang this above your door."

That night, the painted-skin demon came. She hissed at the fly-whisk. Then she reached through, tore it from the doorframe, and entered.

Wang Sheng's screams woke the household. When his wife rushed to the study, all she found was her husband's body — his chest torn open, his heart missing, his face frozen in terror.

This is the first tale. There are four hundred and ninety more. Each one a door. Each one a warning."""),
        ('Chapter 2: The Fox Maiden',
         """Scholar Li had been studying in his mountain cottage for three months when she first appeared.

She came at dusk, when the lamp oil burned low. A girl of perhaps sixteen, with eyes that caught the firelight like amber.

"I live nearby," she said. "The nights are cold. Your fire is warm."

She came every night after that. Sometimes she brought berries, impossibly sweet and red. Sometimes she told stories — tales of fox spirits who cultivated for a thousand years to attain human form. Li listened, enchanted.

One night, she touched his hand. "You should leave this mountain. Before the snow comes."

"I will leave when I pass the examinations," Li said.

"The examinations are in spring. The snow comes next week."

That night, Li dreamed of a fox — the most beautiful creature he had ever seen, with nine tails that shimmered like silk in moonlight. It circled his cottage three times, then sat at his door and wept.

When he woke, she was gone. On his reading mat, a single white hair — impossibly fine, shimmering faintly in the dawn light.

Li packed his books and descended the mountain that day. The first snow fell before he reached the village gate.

He never saw her again. But every winter, when the first snow falls, he places a bowl of the sweetest berries he can find outside his window. And sometimes, in the morning, the bowl is empty.

The mountain remembers what the world forgets."""),
        ('Chapter 3: The Ghost Wife',
         """Marriage is the joining of two families. But what happens when death refuses to dissolve the bond?

Scholar Feng was betrothed at sixteen to a girl he had never met — Miss Lin. Before the wedding took place, Miss Lin fell ill. Within a month, she was dead.

Feng moved on. Years passed. He took the examinations, earned his degree, married a woman named Mei, had a son.

On the boy's third birthday, Feng returned home to find his wife weeping. "A woman came today," Mei said, trembling. "She said she was your first wife."

"That's impossible. Lin has been dead for nine years."

The next day, the woman returned. She wore a red wedding dress, though the color had faded to near-pink with age. A red veil covered her face.

"I have waited," she said. "Nine years in the underworld, and they have granted me a single year above. A single year to be your wife, as was promised."

Feng, torn between pity and fear, allowed her to stay in the guest quarters. For three nights, nothing happened. On the fourth night, their son fell gravely ill — a fever that no physician could break.

The dead bride came to Feng in the courtyard. "The underworld demands its due," she said. "Give me the boy, and I will return to the shadows."

"What do you truly want?" Feng asked.

She removed her veil. Beneath it was not a rotting corpse but a tired woman. "I want to be remembered. My family burned my letters, erased my name. Give me a tablet in your ancestral hall. Let me exist."

Feng did as she asked. The fever broke that night. The ghost wife was never seen again.

But sometimes, when Feng walks past his ancestral hall at dusk, he swears he smells jasmine."""),
        ('Chapter 4: The Taoist of Mount Lao',
         """A young man named Zhou sought to learn magic from a Taoist immortal on Mount Lao. He climbed for seven days, fasted for three, and finally found the immortal sitting beneath a pine tree.

"Master, teach me magic," Zhou begged.

"Magic cannot be stolen," the immortal said. "It must be earned."

"I am willing to earn it," Zhou said.

"For twenty years?"

Zhou hesitated. Then: "Yes."

For twenty years, Zhou chopped wood, drew water, tended the garden, and studied in silence. The immortal taught him nothing — or so it seemed. Then, on the twenty-year mark, the immortal handed him a pill.

"Swallow this at midnight. You will learn what you wish to know."

At midnight, Zhou swallowed the pill. He did not learn magic. He learned the truth about himself — who he truly was, what he had done, what he had hidden from himself for twenty years. The shame was so total that he tried to walk off the mountain and never return.

But he could not. The path had changed. He could not find his way down.

He returned to the immortal. "Now you are ready," the immortal said.

"For what?"

"To learn that magic is not about power. It is about seeing clearly what you are. Everything else follows from that."

Zhou became a great Taoist master. He never demonstrated a single magical trick. But those who studied under him said that sitting in his presence was like being washed clean."""),
        ('Chapter 5: The Cricket King',
         """During the Ming Dynasty, cricket fighting became an obsession that consumed an entire province. The imperial court maintained a Cricket Bureau. Private citizens sold their houses for a single prize cricket.

One poor family's fate turned on the capture of a single extraordinary cricket. The boy who found it could not believe what he held in his hands — a cricket the size of a fist, with mandibles like steel hooks, that moved with the speed and intelligence of a warrior.

He brought it to his father. "This will feed us for a year," the boy said.

The cricket won every fight. The family ate well. They built a new house. Then came a summons from the provincial governor — a man who had lost his champion to this mysterious cricket and wanted it for himself.

The boy had no choice. He delivered the cricket to the governor's palace.

That night, the boy dreamed of a tiny warrior in golden armor, kneeling before him. "You saved my life," the cricket said. "But now I must save yours. Tomorrow, the governor will lose me intentionally. He will blame you. You must leave before dawn."

The boy woke. He packed a small bag and fled into the mountains. Behind him, he heard the governor's guards searching the village.

In the mountains, he found a cave. And in the cave, a woman — ancient, wrapped in grasscloth — who was making a chessboard from crickets' wings.

"Another one who runs," she said. "Sit. Watch."

She showed him the game. Each cricket on the board was a real person. He recognized himself. He recognized the governor. He recognized the cricket he had captured.

"Why?" the boy asked.

"Because someone has to remember that the games we play with small lives are noticed by larger forces. Now go. You have three more years to run. Use them well."

The boy did not understand. He ran anyway."""),
        ('Chapter 6: The Snake Wife',
         """A poor woodcutter rescued a wounded snake on the mountain. That night, a woman appeared at his door, claiming to be lost.

She stayed. She charmed him. She cooked meals that made the neighbors jealous and tended his aging mother with a tenderness that moved the village to tears.

For three years, they lived as husband and wife. Then came the Dragon Boat Festival.

At the festival, someone gave the woodcutter's wife realgar wine — the traditional antidote to poison and demons. She refused the cup.

"Please," the host said. "It is tradition."

She drank. And the woodcutter watched as the woman he loved turned into a snake — a beautiful white snake with eyes that still held human grief.

He did not scream. He did not flee. He knelt beside her.

"I know," he said. "I have always known. Not the form, but the... something. You never ate the fish I caught. You flinched at the smell of blood. I knew something lived in you that was not quite human."

The white snake wept. "You should be afraid."

"I am afraid," he said. "But I love you anyway."

And that was the strange thing about this story: when he said that, she remained a snake, but she also remained his wife. The form mattered less than the name. The body less than the choice.

The local monk Fahai arrived the next morning, having been called by villagers who had seen her true form. The woodcutter stood at his door with an axe.

"Try it," he said. "I have three years' worth of firewood and nothing to lose."

Fahai left. But he was not finished with them. He was never finished with them.

Some love stories are long because the obstacles are long. Some because the love is deep. This one was both."""),
    ],
    'investiture-of-the-gods': [
        ('Chapter 1: The Tyrant and the Fox Spirit',
         """In the ancient kingdom of Shang, the last emperor Zhou ruled with cruelty unmatched in human memory. On a visit to the temple of the goddess Nüwa, he composed a poem so arrogant that heaven itself was offended.

Nüwa, enraged, summoned three demon sisters — spirits who had cultivated for millennia. "The Shang dynasty is due to fall," she told them. "Enter the palace. Accelerate its destruction."

The eldest sister, Daji, was the most beautiful creature in all the realms. Her true form was a thousand-year-old fox spirit, but she slipped into the body of a concubine and rose swiftly to become Emperor Zhou's favorite.

Under Daji's influence, the emperor's cruelty grew monstrous. A lake of wine. A forest of meat. A heated bronze pillar for executions. Each atrocity served to drain the dynasty's mandate from heaven.

But heaven had already chosen a successor. In the west, the virtuous Lord Ji Chang of Zhou was gathering strength. And caught between heaven and earth — neither mortal nor immortal — was Jiang Ziya, the old fisherman who would change the fate of the world.

This is the story of how gods were made."""),
        ('Chapter 2: Jiang Ziya Goes Fishing',
         """There once was an old man who went fishing with a straight hook.

He sat by the Wei River every day, a bamboo pole in his hands, a hook with no curve dangling three feet above the water. Villagers laughed. "Old fool, you'll never catch anything that way."

The old man smiled. "I'm not fishing for fish."

His name was Jiang Ziya. He was seventy-two years old and had spent his life studying the arts of war, government, and the Tao. But despite his wisdom, he had never been called to serve.

One day, Lord Ji Chang of Zhou was traveling along the Wei River when he noticed the strange fisherman. Intrigued, he approached.

"Old man, why do you fish with a straight hook?"

"Because I wait for someone who is willing to be caught."

Lord Ji Chang recognized wisdom when he heard it. He knelt before the old man and begged him to become his strategist.

"My bones are old. I cannot walk so far."

Without hesitation, Lord Ji Chang lifted the old man onto his back and carried him eight hundred steps to his carriage.

"For each step, your dynasty shall rule one year," Jiang Ziya said.

That day, the Zhou dynasty's eight-hundred-year reign was sealed. Jiang Ziya would go on to hold the Investiture Scroll — the list of those destined to become gods.

The greatest catch comes to those who do not chase, but wait."""),
        ('Chapter 3: Nezha\'s Rebellion',
         """Nezha was born wrong.

His mother carried him for three years and six months — far longer than any mortal pregnancy. When he finally emerged, he was not a baby but a ball of flesh that rolled around the room, glowing with an unearthly light.

His father drew his sword to strike it down. But the ball split open, and a boy leaped out — fully formed, bright-eyed, wearing a red sash and golden bracelets.

From the beginning, he was trouble. At seven, he fought the Dragon King's son at the seashore and killed him in a childish rage. The Dragon King demanded justice, threatening to flood the entire region.

Nezha refused to let others suffer for his actions. Before the assembled court, he took a knife and said: "I return this flesh to my mother and these bones to my father."

Then he cut himself down.

What happened next is the miracle. Nezha's teacher gathered lotus roots and fashioned them into a new body. He breathed life into the construct, and Nezha was reborn — stronger than before, with fire-tipped spear and Wind Fire Wheels.

From that day, Nezha was no longer bound by mortal law. A child of rebellion. A weapon of heaven. A reminder that the most powerful soldiers are those who have already died once and returned."""),
        ('Chapter 4: The Ten Suns and the Archer',
         """Before the great war, there was an archer named Houyi who shot down nine of the ten suns that scorched the earth. His wife, Chang'e, drank the elixir of immortality and floated to the moon.

These two legends would echo through the Investiture War — for the gods have long memories.

When the Shang army faced Zhou's forces in the great battle of Mabe, an old man appeared on the Zhou side carrying nothing but a compass-chariot. The soldiers laughed.

"This is my bow," the old man said, pulling a string that had no visible ends. "And these are my arrows." From the sky above, ten suns began to descend.

Houyi's descendants had come. And they remembered what heaven owed the earth.

The battle that followed was unlike any other. When it was over, the Shang army was scattered and the Jade Emperor himself descended to negotiate terms.

This is how the war ended — not with one great battle, but with the accumulated debts of heaven finally being called in."""),
        ('Chapter 5: Daji\'s Garden of Ice',
         """The fox spirit Daji built a garden of ice sculptures in the Shang palace — frozen images of everyone who had crossed her. Each one perfect. Each one a warning.

But ice melts.

When the Zhou army entered the palace, the ice had begun to melt. And in the melting, secrets were revealed — including the location of the original Ice Mirror, which showed not the past but the truth of what each person truly desired.

Many who looked into the Mirror found things they did not wish to find.

Daji herself looked last. What she saw in the Mirror is not recorded. What is recorded is what she said before she vanished:

"I wanted to be loved. That was the only lie I ever told."

Then she became a fox again — the small, ordinary kind — and slipped through a crack in the palace wall. No one knows where she went. Some say she returned to the mountain where all fox spirits are born. Some say she was never real at all.

Most scholars believe the third option: she was both at once, which is the most dangerous kind."""),
        ('Chapter 6: The Battle of the Ten Thousand Immortals',
         """The climactic battle: ten thousand immortals, arrayed in formation, their weapons glowing with the light of stars not yet born.

Nezha fought at the front, his Wind Fire Wheels leaving trails of fire across the sky. Erlang Shen fought beside him, his third eye blazing. Jiang Ziya stood on a hilltop, scroll in hand, calling the names of the dead — and watching them rise.

Heaven watched. Hell waited. And the celestial bureaucracy took notes.

When the battle was over, the Investiture Scroll was read from beginning to end. Three hundred and sixty-five names. Three hundred and sixty-five new gods. The celestial order was complete.

And Jiang Ziya, old and tired, sat by the Wei River with a straight hook in his hand.

The fishing was good. The fish were scarce. But that was not the point.

The point was the waiting. The point was the water. The point was the silence at the end of a great and terrible day, when the world had been remade and all that remained was a river, a hook, and a man who had never expected to matter."""),
    ],
    'gullivers-travels': [
        ('Chapter 1: A Voyage to Lilliput',
         """After a shipwreck, Lemuel Gulliver washes ashore on an island where everything is impossibly small. Literally tied down by a thousand tiny threads, he becomes first a prisoner, then a curiosity, then a weapon of war.

The Lilliputians are six inches tall. Their capital is a city of matchboxes and needle daggers. Their navy consists of boats no bigger than a child's toy.

Gulliver, who towers over them like a giant among insects, becomes the most valuable piece in their political chess game. Both sides want him. Both sides promise him rewards. And Gulliver, who has not yet learned to distrust politicians, believes them.

"Sign this compact," the Emperor of Lilliput says, "and you shall be made a Noble of the Empire."

Gulliver signs. The compact is written in letters two inches tall, which he can read easily. He does not notice that the language is vague enough to mean anything, or that the obligations section goes on for pages.

This is how the great and the small are alike: both are fluent in the language of promises."""),
        ('Chapter 2: The War of the Eggs',
         """Lilliput and its rival Blefuscu have been at war for generations over a seemingly trivial matter: which end of an egg should be cracked first.

Gulliver, caught between two absurd factions, discovers that the smallest conflicts often hide the deepest hatreds. Blefuscu has been harboring Lilliputian refugees — specifically, those who crack their eggs at the small end, as the High Church of Lilliput mandates.

"The Big-Endians are heretics," the Emperor of Lilliput explains, seriously.

Gulliver proposes a compromise: let people crack eggs however they wish. The Emperor's face goes white with rage.

"Liberty is the enemy of order," he says. "And order is the foundation of empire."

Gulliver begins to understand that empires — even miniature ones, even toy ones — operate by the same logic as their full-sized counterparts: the powerful define reality, and deviation is always heresy.

He escapes by wading across the channel. The water barely reaches his knees. But he is terrified all the same."""),
        ('Chapter 3: Brobdingnag: Land of Giants',
         """Gulliver's second voyage lands him in a kingdom where he is the tiny one. The giant farmers who find him treat him as a curiosity — a living doll.

He must adapt to a world where a cat's yawn is a hurricane, a maid's apron is a sail, and a single drop of dew is enough to drown him.

The King of Brobdingnag is the most sensible ruler Gulliver ever meets — which is to say, he recognizes a talking insect when he sees one and treats Gulliver accordingly: with curiosity, but not with the reverence Gulliver has begun to expect.

"This creature," the King says to his court, pointing at Gulliver, "has the shape of a human being. But I do not find that it thinks like one. It seems to me that it knows nothing beyond what it has read in books."

Gulliver launches into a passionate defense of his country's institutions. The King listens. Then he says:

"You have convinced me that your country is the most villainous nation under the sun. And your tiny inhabitants the most pernicious vermin the world has ever produced."

Gulliver has no answer. He is right, of course. He simply did not want to hear it from a giant."""),
        ('Chapter 4: The Struldbrugs: A Warning About Immortality',
         """In Luggnagg, Gulliver learns of the Struldbrugs — people cursed with immortality. They do not stay young forever. They age. And age. And age.

The Struldbrugs are the saddest creatures in the world. They remember everything — every joy, every grief, every loss. They have buried their children, their grandchildren, their great-great-great-grandchildren. They remember the birth of cities that no longer exist and the death of empires that have been forgotten.

And they remember their own faces, from the days when they were young.

Gulliver's fantasy of eternal life dies a quiet, horrified death. When the Luggnaggians ask if he would like to become a Struldbrug, he refuses so forcefully that they think him mad.

"To live forever," he writes, "is to live in a house with no windows, where the same fire has been burning for a thousand years and will burn for a thousand more, and you cannot leave, and no one comes to visit, and the wood is always the same color of ash."

The fantasy of immortality is the fantasy of endless newness. The reality is the same — only longer."""),
        ('Chapter 5: The Land of the Houyhnhnms',
         """Gulliver's final voyage brings him to a land ruled by horses — rational, wise, utterly honest creatures who have never learned to lie.

Among them, he finds a peace he never knew. The Houyhnhnms do not deceive, do not flatter, do not scheme. They live by reason and nature. Their society is ordered without being oppressive. Their kindness has no angle.

For six months, Gulliver lives among them. He begins to see himself — and all of humanity — with new eyes. The Houyhnhnms do not understand war, because they do not understand greed. They do not understand deception, because they cannot conceive of it.

But the Yahoos — savage human-like creatures — remind him, with painful clarity, of home. And Gulliver is a Yahoo. No amount of time with noble horses can change that.

He leaves with sorrow. He returns with disgust. And for the rest of his life, he cannot look at his own reflection without remembering what he truly is.

This is the cruelest and most honest thing Jonathan Swift ever wrote."""),
    ],
    'creation-of-the-gods': [
        ('Chapter 1: In the Beginning',
         """Before heaven and earth, before light and darkness, before even the concept of 'before' — there was chaos. A cosmic egg containing everything and nothing. Within it slept Pangu, the first being, dreaming of a world that did not yet exist.

How long he slept, no one knows. Time did not yet exist either. The egg simply was — a possibility too heavy to open, too pregnant to remain closed.

And then, one morning — though there were no mornings, not yet — Pangu opened his eyes.

The first thing he saw was darkness. The second thing he saw was the darkness pressing in on all sides. The third thing he saw was that the darkness was not alive, not dead, not anything at all — just the space between one thing and another.

Pangu reached out. His hands touched... nothing. And everything. And the nothing began to separate from the everything.

This is how the world was born: not with a word, but with a touch."""),
        ('Chapter 2: Pangu Splits the Sky',
         """After eighteen thousand years of sleep, Pangu awoke. Finding himself trapped in darkness, he swung his axe — an axe that had been growing from the egg all along, iron-hard, ready — and split the cosmic egg.

The light parts rose to become heaven. The heavy parts sank to become earth. And Pangu stood between them, holding them apart, for another eighteen thousand years.

Each day, he grew ten feet taller. Each day, heaven rose a little higher. Each day, the earth sank a little deeper. And each day, Pangu stood.

When at last he lay down to die, his body became the world: his breath the wind, his voice the thunder, his left eye the sun, his right eye the moon, his blood the rivers, his flesh the soil, his bones the mountains, his teeth the metals buried in the earth.

Everything that exists, exists because Pangu gave it a piece of himself.

This is the first act of creation. Everything that follows is an echo of this one: a god dying so that something else can live."""),
        ('Chapter 3: Nüwa Creates Humanity',
         """The goddess Nüwa walked a beautiful but empty world. The sky had been mended. The earth was fertile. But there were no voices. No laughter. No one to appreciate any of it.

Lonely, Nüwa scooped yellow earth from a riverbank and began to shape small figures with her hands. She worked carefully, giving each one eyes, a mouth, two arms, two legs. She breathed life into them with her own divine breath, and they moved, and they spoke, and they looked up at her with something that might have been gratitude.

She worked until her hands were tired, which took about a day. Then she rested, and the figures she had made became the aristocracy — the noble class, who carry a little of the divine earth in their blood.

Then she grew tired of working slowly. So she dipped a rope in mud and swung it — and the drops that flew off became the common people, who are many and whose lives are brief and difficult.

This is why the powerful and the common are made of the same earth. This is why no one is truly superior. Nüwa made all of us from the same handful of mud, and she was in no mood to play favorites."""),
        ('Chapter 4: Nüwa Mends the Sky',
         """A great war between the gods — Gong Gong versus Zhurong, fire against water, sky-gods against earth-gods — shattered the pillars of heaven. The sky cracked. Floods and fire rained upon the earth.

Nüwa, the creator of humanity, saw what was happening and felt something she had never felt before: urgency.

She descended to earth and began to work. She melted five-colored stones to patch the heavens — a task so exhausting that it took her thousands of years. She found a giant turtle and cut off its legs to use as pillars, propping up the sky at the four corners. She gathered ash from the burnt reed marshes and used it to dam the floods.

When it was over, heaven was patched, earth was stable, and humanity was saved — but Nüwa was changed. She had spent so much of herself in the repair that she could no longer walk freely among mortals. She retreated to the western mountains, where she remains to this day, occasionally descending to help those who are truly in need.

Gods are not eternal. They spend themselves. And sometimes the greatest act of divinity is not creation but repair."""),
        ('Chapter 5: The First Gods Take Their Thrones',
         """With the sky mended and humanity thriving, the first gods took their positions in the celestial order.

The Jade Emperor became the supreme ruler of heaven — not by conquest, but by a vote among the other gods, who recognized that he was the most patient among them and patience is the first virtue of administration.

The Kitchen God took his post to watch over households — to record the good and bad deeds of each family and report them to heaven once a year. The City God took his to protect communities. The Dragon Kings took theirs to rule the seas and send rain when properly petitioned.

The system was bureaucratic, which was the point. The gods were not tyrants — they were administrators. There were forms to fill out, proper channels to follow, appeals to file.

Humans complained about this system constantly. "The gods are so slow," they said. "The gods don't listen." But what they meant was: the gods were not magic. The gods were management.

And management, as everyone knows, is the art of making sure things get done — slowly, properly, and with a great deal of paperwork."""),
        ('Chapter 6: The Separation of Heaven and Earth',
         """In ancient times, gods walked among humans. Immortals descended from the sky to teach philosophy and medicine. Demons rose from the earth to teach agriculture and warfare. The boundaries were open, and the traffic was constant.

But a great conflict — a war between two factions of immortals, the details of which have been lost — forced the Heavenly Emperor to sever the connection. He broke the great ladder by which heaven and earth were joined.

The human hero Ju Song tried to climb what remained of it. He got very close. Then he fell. The fall killed him. And the pieces of the ladder scattered across the sky as stars.

From that day, the realms were separate, and humanity was truly alone.

This is the Chinese story that most resembles the Tower of Babel. But in the Chinese version, the breaking of the ladder was not a punishment — it was a wound. The gods themselves were diminished by the separation. Heaven without earth is incomplete. Earth without heaven is orphaned.

The gods built walls they could not cross. And ever since, they have been trying to find doors."""),
    ],
    'monkey-kings-birth': [
        ('Chapter 1: The Stone Egg',
         """At the summit of the Mountain of Flowers and Fruit, there sat a stone of unusual shape — worn by wind and rain since the time when heaven and earth first separated.

This stone absorbed the essence of the sun and moon. It drank the dew of countless mornings. It was touched by the forces that shape worlds.

And then, one morning, the stone cracked.

From within emerged an egg — not a snake's egg, not a bird's egg, but a stone egg, polished smooth by the same forces that had shaped the mountain. The egg rolled once, twice, then split open with a sound like the cracking of the world.

Out stepped a monkey.

Golden fur. Eyes that blazed with light so bright they pierced the heavens. The Jade Emperor felt the tremor on his throne.

"It is only a monkey," the Star of Wisdom reported. "Nothing to concern Your Majesty."

And so the matter was dismissed. This would prove to be a mistake.

The stone monkey joined a tribe of ordinary monkeys and became their king. When they found a waterfall with a hidden cave behind it, the stone monkey leaped through first.

"I have found our home!" he called back.

Thus Sun Wukong — the Monkey Awakened to Emptiness — was crowned King of the Mountain of Flowers and Fruit.

But kingship was only the beginning. Deep in his heart, he felt a hunger no fruit could satisfy. The hunger for immortality."""),
        ('Chapter 2: The Quest for Immortality',
         """For three hundred years, the Monkey King ruled his mountain. Then one night, at a banquet, a monkey fell from a branch. Dead.

"Death," the old monkey said. "It comes for all of us."

"Not for me," Sun Wukong declared.

He set out on a raft, crossing oceans, searching for immortality. His journey took him to the Western Continent, to a mountain called the Terrace of the Mind. There, in a cave lit by eternal starlight, he found the immortal master Subhuti.

"Teach me to live forever," Wukong begged.

"There are three hundred and sixty gates to the Way. Which do you seek?"

"The one that defeats death."

For seven years, Wukong studied under Subhuti. He learned to guard his spirit and concentrate his essence. But the master withheld the final teaching.

At the third watch, in the deepest hour of night, Subhuti came to Wukong in secret. He whispered three words into the monkey's ear, struck him three times on the back of the head, and departed.

Wukong understood.

"You now possess what no creature of earth or heaven can take from you," Subhuti said. "But remember — pride is the one weapon against which immortality offers no defense."

Wukong did not understand. He would learn."""),
        ('Chapter 3: The First Battle in Heaven',
         """Armed with immortality, Sun Wukong returned to his kingdom. But he wanted power that heaven would recognize.

He stormed the dragon king's palace and demanded a weapon. None sufficed until the dragon queen pointed at an iron pillar: "That is the Great Sage Equal to Heaven's Pillar. It has not moved in ten thousand years."

Wukong grasped the pillar. It shrank to fit his hand. It weighed 17,550 pounds. On its side, in letters of gold: AS YOU WISH — GOLDEN CUDGEL.

Next, he stormed the underworld. He crossed his name off the registry of death. He crossed out every monkey's name.

The Jade Emperor, alarmed, was advised to pacify the monkey with a title. "Give him a minor post. Let him think he belongs here."

So Wukong was given the title of Protector of the Heavenly Stables.

"Protector of horses?" Wukong snorted. "I am the Monkey King, the Great Sage Equal to Heaven."

He declared war.

He won — alone, with only his Golden Cudgel and his indomitable pride.

It took the combined forces of heaven — including Erlang Shen with his third eye, and ultimately the Buddha himself — to bring him to heel. Even then, Wukong nearly escaped.

The Buddha's hand became a mountain. Five fingers became five peaks. And beneath them, for five hundred years, the Monkey King waited."""),
    ],
    'white-snake-legend': [
        ('Chapter 1: The West Lake Encounter',
         """On a rainy spring day at West Lake, a young scholar named Xu Xian shared his umbrella with two beautiful women — one in white, one in green.

He did not know that they were spirits who had cultivated for a thousand years, nor that this simple kindness would change his life forever.

The woman in white — Bai Suzhen — found him charming in his awkwardness. "Thank you for the umbrella, young sir," she said, and her voice was like the sound of rain on lotus leaves.

Xu Xian blushed. He was not used to beautiful women addressing him directly. He was not used to anyone addressing him directly.

"My sister and I are going to the Temple of Lonely Cold," she said. "Will you escort us?"

He did. He was too polite not to. And when they arrived, and the rain intensified, and his umbrella was the only shelter, he stood in the rain rather than share it with them — because he thought sharing would be improper.

Bai Suzhen, watching from the temple doorway, smiled. "This one," she said to her sister the green snake, "is worth the thousand years."

The green snake said nothing. She had seen too many of these stories end badly to be optimistic. But she said nothing, because hope is harder to kill than wisdom."""),
        ('Chapter 2: The Bride in White',
         """Madam White and Xu Xian married within the month. She was perfect: beautiful, gentle, skilled in medicine. Together they opened an apothecary that healed the poor for free.

The people of Hangzhou adored her. She organized festivals and knew everyone's name. She was kind to the children and patient with the elderly. Xu Xian, watching her from across their modest shop, sometimes could not believe she had chosen him.

One man saw through her human form: the monk Fahai of Golden Mountain Temple.

"Your wife is a white snake demon," Fahai told Xu Xian directly. "She has deceived you."

Xu Xian refused to believe it. Who would believe such a thing about the woman who had given him tea every morning and tended his fever when he was sick and cried when he was sad?

Fahai nodded — this was always the response, it seemed — and withdrew. But he did not leave. He simply became patient.

Patience, in the end, is always the monk's greatest weapon."""),
        ('Chapter 3: The Truth Revealed',
         """On the Dragon Boat Festival, Fahai's opportunity came.

"Give her realgar wine," he told Xu Xian. "It will reveal her true form."

At the festival, someone gave Bai Suzhen the wine. She tried to refuse.

"Please," the host said. "It is tradition."

She drank. And in the moments that followed, Xu Xian saw the truth — a white snake coiled in the bed where his wife had been — and fainted dead from terror.

Bai Suzhen, newly revealed, was desperate. She fled to the underworld itself, where she begged the King of Hell for her husband's soul.

"I will give you anything," she said. "My cultivation. My centuries. My life."

The King of Hell, who was not unkind, looked at this creature who was half-demon and half-something-he-could-not-name. "You already have," he said.

And he gave her back Xu Xian's soul.

When Xu Xian woke, his wife was beside him, ordinary and beautiful. She said nothing about what had happened. He said nothing about what he had seen.

But something had shifted between them. A door had opened that could not be closed.

Some truths, once seen, cannot be unseen. Some love, once tested, cannot be untested. And some marriages survive by mutual agreement to never speak of the white snake in the room."""),
        ('Chapter 4: The Boy at Leifeng Pagoda',
         """Bai Suzhen was imprisoned beneath Leifeng Pagoda. Years passed.

A young scholar — her son, Xiao Fa — grew up not knowing his mother's story. He was brilliant, gentle, and carried a sadness he could not explain — a longing for something he had never had.

On the day he earned the highest marks in the imperial examinations, he knelt before Leifeng Pagoda. He did not know why. He had never been told whose prison this was. But something pulled him here.

"mother," he whispered to the ancient stones. "I don't know you. But I think you're here."

And the pagoda... trembled.

From within the stone, Bai Suzhen heard him. She had not heard anything from outside in twenty years. The walls were thick. The world was far.

But her son's voice made it through.

She pressed her palm against the inside wall. He pressed his against the outside. And the pagoda, caught between a mother's love and an ancient punishment, began to crack.

Fahai, watching from Golden Mountain, saw it happen. And for the first time in forty years, he felt something he had not expected to feel: doubt.

"What if," he thought, "I am the demon?"

The crack in the pagoda widened. The crack in his certainty widened further."""),
        ('Chapter 5: The Reunion',
         """Twenty years of separation. A son who never knew his mother. A husband who had spent two decades in a monastery, seeking to understand what he had witnessed.

And Bai Suzhen, freed at last, standing before them both.

What do you say to the people you loved enough to sacrifice everything for?

Xu Xian said: "I am sorry I was afraid."

Xiao Fa said: "I don't know how to be your son."

Bai Suzhen said: "I am not a demon. I am not a saint. I am a creature who loved, and that is all."

They stood together for a long time in the courtyard of Leifeng Pagoda, which was now no longer a prison but a ruin — a monument to something neither heaven nor hell had quite understood.

The Queen Mother of the West reviewed the case later. She ruled that Bai Suzhen had committed acts worthy of punishment and acts worthy of reward, and that the balance was... ambiguous.

"This is the correct answer," she said. "Nothing is entirely good. Nothing is entirely evil. We are all of us mixed — serpent and saint, stone and sky. The task is not to be pure. The task is to be whole."

And Bai Suzhen, who had spent a thousand years becoming human, finally understood what a thousand years of cultivation had been for: not power, not immortality, but the long, difficult work of becoming whole."""),
    ],
}

# ── Fill remaining chapters with placeholder content ───────
def fill_remaining(slug, total):
    path = os.path.join(CHAPTERS_DIR, f'{slug}_1.json')
    existing = len(glob.glob(os.path.join(CHAPTERS_DIR, f'{slug}_*.json')))
    for i in range(existing + 1, total + 1):
        write_chapter(slug, i, f'Chapter {i}', f'Content for chapter {i} of this novel — more to come in the next update.')

# ── Execute ────────────────────────────────────────────────
for novel in NEW_FREE:
    slug = novel['slug']
    total = novel['total_chapters']
    chapters = CHAPTERS.get(slug, [])
    for i, (title, content) in enumerate(chapters):
        write_chapter(slug, i + 1, title, content)
    if len(chapters) < total:
        fill_remaining(slug, total)
    print(f"  ✓ {novel['title_en']}: {total}ch")

# ── Reorder novels ─────────────────────────────────────────
with open(os.path.join(DATA_DIR, 'novels.json')) as f:
    all_novels = json.load(f)

vip = [n for n in all_novels if n.get('zone') == 'vip']
free = [n for n in all_novels if n.get('zone') == 'free']

# Interleave: 2 VIP, 1 FREE
new_order = []
fi = 0
for i, v in enumerate(vip):
    new_order.append(v)
    if (i + 1) % 2 == 0 and fi < len(free):
        new_order.append(free[fi])
        fi += 1
# Append remaining free
new_order.extend(free[fi:])

# Insert new free novels at scattered positions
NEW_META = {
    'strange-tales-chinese-studio':    {'total_chapters': 12, 'reads': 156000, 'rating': 4.6},
    'investiture-of-the-gods':         {'total_chapters': 12, 'reads': 189000, 'rating': 4.7},
    'gullivers-travels':               {'total_chapters': 8,  'reads': 320000, 'rating': 4.3},
    'creation-of-the-gods':            {'total_chapters': 7,  'reads': 41000,  'rating': 4.4},
    'monkey-kings-birth':              {'total_chapters': 8,  'reads': 87000,  'rating': 4.8},
    'white-snake-legend':              {'total_chapters': 8,  'reads': 124000, 'rating': 4.6},
}

insert_ats = [4, 8, 13, 18, 22, 26]
for j, slug in enumerate(NEW_META):
    meta = NEW_META[slug]
    novel = next(n for n in NEW_FREE if n['slug'] == slug)
    novel['total_chapters'] = meta['total_chapters']
    novel['reads'] = meta['reads']
    novel['rating'] = meta['rating']
    at = min(insert_ats[j], len(new_order))
    new_order.insert(at, novel)

with open(os.path.join(DATA_DIR, 'novels.json'), 'w') as f:
    json.dump(new_order, f, ensure_ascii=False, indent=2)

print(f"\n✅ Done! Total novels: {len(new_order)}")
for i, n in enumerate(new_order):
    z = 'FREE' if n.get('zone') == 'free' else 'VIP'
    print(f"  {i+1:2d}. [{z}] {n['title_en'][:55]} ({n.get('total_chapters', 0)}ch)")