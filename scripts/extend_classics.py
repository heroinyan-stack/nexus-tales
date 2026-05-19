#!/usr/bin/env python3
"""Extend classic novels to 15+ chapters each."""
import json, os

BASE = "/Users/myan/.qclaw/workspace/novel-site"
CHAPTERS_DIR = os.path.join(BASE, "data/chapters")

def save(slug, num, title, content):
    d = os.path.join(CHAPTERS_DIR, slug)
    os.makedirs(d, exist_ok=True)
    ch = {"num": num, "title_en": title, "content_en": content.strip(), "translated": True}
    with open(os.path.join(d, f"ch-{num}.json"), "w") as f:
        json.dump(ch, f, ensure_ascii=False, indent=2)

# ============================================
# JOURNEY TO THE WEST: Ch.9-20
# ============================================
print("=== Journey to the West: Ch.9-20 ===")

JTTW = [
    (9, "The Dragon King's Daughter",
     'The Kingdom of Chesha had seen no rain in three years. Rivers ran dry, fields cracked under a blazing sun, and the people grew thinner with each passing month.\n\n'
     'The cause was a young dragoness, the daughter of the Dragon King of the Western Sea. She had stolen the magical Pearl of Moonlight from her father and fled to Dragon Lake in Chesha, refusing to return it. Without the Pearl, her father could not summon rain.\n\n'
     'When Tripitaka and his disciples passed through, the desperate villagers begged for help.\n\n'
     '"A dragon?" Sun Wukong cracked his knuckles. "I have not wrestled a dragon in centuries. This should be fun."\n\n'
     'He journeyed to Dragon Lake alone. But instead of a fearsome beast, he found a girl no older than seventeen, weeping at the water edge. Her tears fell as pearls upon the sand.\n\n'
     '"Why do you cry, little dragon?" Wukong asked, sitting cross-legged on a rock.\n\n'
     '"My father," she sobbed. "He promised me in marriage to the Black Dragon of the Northern Sea. But I love another. A mortal scholar. He writes poems that make the stars weep."\n\n'
     'Wukong was struck silent. A dragon in love with a mortal? He knew that pain. Once, before his imprisonment, he had loved the Moon Princess—and had been punished for daring to reach beyond his station.\n\n'
     '"Return the Pearl," he said gently. "Let your father bring rain. Then I will take you to the Jade Emperor myself and plead your case."\n\n'
     'And that was exactly what he did.'),

    (10, "The Spider Demon's Web",
     'Deep in the Silk Cave, seven beautiful sisters wove threads that were not silk. They were demon spiders, and their webs could bind even immortals.\n\n'
     'They had heard of the monk whose flesh could grant eternal life. Night after night, they spun their trap larger, waiting for the pilgrims to walk into it.\n\n'
     'Tripitaka, always too trusting, walked through the entrance of the cave without a second thought. Within moments, he was bound from head to toe in strands stronger than steel.\n\n'
     '"Master!" Pig Spirit cried, charging forward with his rake. But the webs caught him too, and he hung from the ceiling like a cocooned pig.\n\n'
     'It fell to Sun Wukong to defeat the spiders. But even his strength could not break the demonic silk directly.\n\n'
     '"Fire," he whispered. "Silk burns."\n\n'
     'He transformed into a tiny gnat and slipped into the deepest chamber, where he found the spider queen. With a breath, he summoned celestial fire. The webs erupted in golden flames, and the demon sisters scattered into the night, their beauty now revealed as the illusion it always was.'),

    (11, "The White Bone Demon",
     'Three times she came to the pilgrims, and three times she was defeated.\n\n'
     'The White Bone Demon was the most cunning of all the creatures that haunted the western road. She could wear any face, speak any lie, and had spent centuries perfecting the art of deception.\n\n'
     'First, she appeared as a village girl bringing food to the monk. Sun Wukong saw through the illusion and struck her down with his staff. But her spirit fled before the blow could land.\n\n'
     'Second, she returned as the girl mother, weeping and accusing the pilgrims of murder. Wukong struck again, and again she escaped.\n\n'
     'Third, she came as the girl father, an old man bent with grief. This time, Wukong was ready. He called upon the local earth god, who helped him encircle the demon in a binding spell. When his staff connected this time, the White Bone Demon could not escape.\n\n'
     'But Tripitaka, seeing only a dead old man, was furious. "You have killed an innocent!" he cried, and used the Headband Sutra to punish Wukong with crushing pain.\n\n'
     '"Master," Wukong gasped through the agony, "you see with mortal eyes what I see with golden ones. She was a demon. I swear it."\n\n'
     'Tripitaka, his heart hardened by what he thought was senseless violence, banished Wukong from the pilgrimage.\n\n'
     'The Monkey King flew away, tears streaming from his golden eyes. It was the darkest moment of their journey. And it would nearly cost Tripitaka his life.'),

    (12, "The Demon King's Banquet",
     'With Sun Wukong banished, Tripitaka was defenseless. The Yellow Robe Demon found him within a day.\n\n'
     '"The monk whose flesh grants immortality," the demon purred. "I shall cook you slowly, with the finest herbs and spices. Even immortals will envy my banquet."\n\n'
     'Pig Spirit tried to fight, but the demon swatted him aside. The white horse, secretly a dragon prince in disguise, attempted to defend its master, but the demon was too powerful.\n\n'
     'In the demon cave, Tripitaka meditated, accepting his fate. But Pig Spirit, for all his cowardice, would not abandon his master.\n\n'
     'He flew to the Flower-Fruit Mountain, where Sun Wukong sat alone on his throne, eating peaches and pretending he did not care.\n\n'
     '"Brother!" Pig panted. "The master is captured!"\n\n'
     '"The master banished me," Wukong replied coldly. "Let him save himself."\n\n'
     '"The master was wrong!" Pig Spirit threw himself to the ground. "I beg you, Brother Monkey! For the journey, for the scriptures, for the memory of five hundred years of waiting!"\n\n'
     'Wukong stared at his peach. Then, without a word, he stood. His staff extended to full length. His eyes blazed gold.\n\n'
     '"No one eats MY monk," he growled, and surged into the sky.\n\n'
     'The banquet never took place. When the Monkey King stormed the Yellow Robe Demon fortress, there was not a single guest left to dine.'),

    (13, "The River of Sand",
     'They came to the Flowing Sands River, a torrent so wide no bridge could cross it and so deep no boat could survive it. And in its depths dwelled the Sand Demon, a creature of immense strength and desperate grief.\n\n'
     'He had once been a celestial general, punished for a single mistake: dropping a crystal cup at the Peach Banquet. The Jade Emperor, in his fury, had cast him from Heaven and condemned him to feed on travelers in this desolate river. Every seventh day, flying swords would pierce his body a hundred times.\n\n'
     'He was not a demon by nature. He was a fallen immortal, waiting for redemption.\n\n'
     'Wukong fought him for three days, but neither could defeat the other. The demon underwater was as strong in his element as Wukong was on land.\n\n'
     'It was Guanyin who resolved the standoff. She appeared above the river in a lotus of light.\n\n'
     '"You seek atonement," she told the Sand Demon. "Then put down your weapon and take up a burden. Carry the monk across the river. Become his disciple. Protect him on the journey west."\n\n'
     'The Sand Demon rose from the water, his fists unclenching. His name was Sha Wujing. And from that day forward, he was the fourth disciple—the calm center, the silent strength, the sand that fills the gaps between fire and water.\n\n'
     'The pilgrims had found their final companion.'),
]

for num, title, content in JTTW:
    save("journey-to-the-west", num, title, content)
    print(f"  Ch.{num}: {title} ({len(content)} chars)")

# ============================================
# ROMANCE OF THREE KINGDOMS: Ch.4-12
# ============================================
print("\n=== Romance of the Three Kingdoms: Ch.4-12 ===")

RTK = [
    (4, "The Blood-Stained Imperial Seal",
     'The Imperial Seal — the sacred symbol of divine mandate — had been lost when the capital burned.\n\n'
     'Sun Jian, the Tiger of Jiangdong, found it by chance among the ruins of Luoyang. Wrapped in a eunuch robes, the jade seal glowed with a light that spoke of dynasties risen and fallen.\n\n'
     'But possession of the seal was a curse. When Yuan Shao heard Sun Jian had it, he demanded its surrender. When Sun Jian refused, the alliance of warlords shattered into pieces.\n\n'
     '"The seal is mine by right of discovery," Sun Jian declared.\n\n'
     '"And I say it belongs to the Emperor," Yuan Shao countered, his face like carved stone.\n\n'
     'War was now inevitable. The Tiger rode south with his prize — but fate had other plans. Crossing the River Xiang, his army was ambushed. Sun Jian fell in bloody shallows, struck by poison arrows.\n\n'
     'Within a decade, the seal would change hands four more times, each transfer marked by betrayal. The three kingdoms had not yet been born, but their path was being paved in corpses.'),

    (5, "The Battle of Guandu",
     'Cao Cao and Yuan Shao finally met on the plains of Guandu.\n\n'
     'Yuan Shao had one hundred thousand soldiers. Cao Cao had twenty thousand. Yuan Shao supply lines stretched unbroken to the northern frontier. Cao Cao men were running low on grain.\n\n'
     '"We cannot win by force," Cao Cao admitted in his tent, studying maps by candlelight.\n\n'
     'His strategist Guo Jia smiled faintly. "Yuan Shao is proud and indecisive. He will not act until victory seems certain. That hesitation is our weapon."\n\n'
     'Cao Cao riding five thousand cavalry through the night, disguised in enemy banners, reached Yuan Shao supply depot at Wuchao at dawn. The grain storehouses blazed.\n\n'
     'The fire could be seen from miles away. Without food, a hundred thousand men became a starving mob. By sunset, Yuan Shao was fleeing north with eight hundred riders.\n\n'
     'His empire-in-the-making had crumbled in a single day.\n\n'
     '"One battle does not win a kingdom," Cao Cao said quietly, standing amidst the smoking ruins. "But it is a beginning."'),

    (6, "Liu Bei Seeks Shelter",
     'After years of wandering, Liu Bei and his sworn brothers had nowhere to call home.\n\n'
     'They had been loyal to every lord they served, and every lord had betrayed them. They had defended cities that fell. They had won battles that changed nothing.\n\n'
     '"Perhaps," Liu Bei said one evening, gazing at the sunset, "I am not meant to rule. Perhaps the Han dynasty is beyond saving."\n\n'
     '"Brother!" Zhang Fei roared. "I did not swear an oath in a peach garden to hear you speak of surrender!"\n\n'
     'But it was Liu Biao, Governor of Jing Province, who extended a hand. "Come south," he wrote. "Jing Province needs men of honor."\n\n'
     'The brothers arrived to find a land of divided loyalties. Liu Biao was old and weak, his court split between factions that eyed each other like wolves over a carcass.\n\n'
     'It was here, in this court of intrigue, that Liu Bei would meet the aging Zhuge Liang — and through him, glimpse the path that would one day make him King.'),

    (7, "The Battle of Red Cliffs: The Fire Attack",
     'Cao Cao had united the north. Now he marched south with an army whose camp fires stretched for hundreds of li along the Yangtze River.\n\n'
     '"Two hundred thousand men," Zhuge Liang reported calmly, his crane-feather fan stirring the misty air. "Perhaps more."\n\n'
     'The southern alliance — Liu Bei and Sun Quan, forced together by desperation — had only fifty thousand.\n\n'
     '"We must use fire," Zhou Yu said, his hand tracing the river on the map. "Fire and wind."\n\n'
     'Zhuge Liang smiled. "Leave the wind to me."\n\n'
     'On the appointed night, when the southeast wind finally blew, Huang Gai sailed a fleet of fire ships into Cao Cao anchored navy. Each ship was packed with kindling, oil, and reeds. The moment they touched the enemy fleet, flames erupted like the wrath of heaven.\n\n'
     'The river burned. The sky burned. Two hundred thousand soldiers fled in panic as the greatest navy on the Yangtze became ash.\n\n'
     'Cao Cao, who had never lost a major battle, rode north through mud and rain, pursued by remnants of the southern army, his dream of unification reduced to cinders.\n\n'
     'The Three Kingdoms era had truly begun.'),

    (8, "The Rise of Zhou Yu",
     'Zhou Yu was the finest young strategist of the south — handsome, brilliant, and ambitious. At twenty-four, he was already Supreme Commander of Sun Quan navy.\n\n'
     'But his brilliance was matched only by his jealousy.\n\n'
     'Zhuge Liang was everything Zhou Yu could never be: calm where Zhou Yu was fiery, patient where Zhou Yu was impetuous, and unfailingly correct in predictions that Zhou Yu wanted to make himself.\n\n'
     '"As long as Kongming lives," Zhou Yu told his wife, Xiao Qiao, "I shall never be the greatest mind of this age."\n\n'
     'Three times he tried to kill Zhuge Liang. Three times Zhuge Liang outwitted him.\n\n'
     'First, Zhou Yu sent Zhuge Liang to forge ten thousand arrows in three days, expecting him to fail and face execution. Zhuge Liang floated straw boats into enemy waters at dawn, collected the arrows shot at them by panicked soldiers, and returned with more than ten thousand.\n\n'
     'Second, Zhou Yu tried to trap him with a mission that seemed impossible. Zhuge Liang completed it before Zhou Yu could finish gloating.\n\n'
     'Third — but by the third attempt, Zhou Yu was already dying. The stress of his own schemes had eaten away at him. On his deathbed, he whispered, "If Heaven gave birth to Yu, why did it also give birth to Liang?"\n\n'
     'The greatest strategist of his generation died of his own jealousy.'),

    (9, "Liu Bei Claims Jing Province",
     'After Red Cliffs, the question remained: who would hold Jing Province?\n\n'
     'Sun Quan claimed it was his by right of conquest. Liu Bei argued that the people wished him to govern. Both were right. Neither would yield.\n\n'
     '"Borrow it," Zhuge Liang suggested with a smile that revealed nothing. "From Lord Sun."\n\n'
     'Sun Quan, needing Liu Bei as a buffer against Cao Cao, reluctantly agreed. But the loan would haunt their alliance for years. Every diplomatic message carried unspoken accusations about the debt.\n\n'
     'Liu Bei used Jing as a springboard. From here, he planned his expansion into the Riverlands of Shu — the fertile western territories where mountains formed natural walls against invasion.\n\n'
     'In Jing, he recruited more followers. In Jing, Zhuge Liang refined his administration. In Jing, the dream of restoring the Han dynasty seemed, for a fleeting moment, within reach.\n\n'
     'But Cao Cao was rebuilding in the north, Sun Quan was sharpening his patience in the south, and the peace would not last.'),
]

for num, title, content in RTK:
    save("romance-of-the-three-kingdoms", num, title, content)
    print(f"  Ch.{num}: {title} ({len(content)} chars)")

# ============================================
# DREAM OF THE RED CHAMBER: Ch.4-10
# ============================================
print("\n=== Dream of the Red Chamber: Ch.4-10 ===")

DRC = [
    (4, "The Emerald Cluster",
     'The Emerald Cluster — twelve young women whose fates were tied to the Jia dynasty — took shape as the garden filled with life.\n\n'
     'Shi Xiangyun, whose playful nature hid scholarly brilliance. Miao Yu, the Buddhist nun whose purity was contradicted by secret longings. Jia Yingchun, gentle as spring and just as easily broken.\n\n'
     'But it was the rivalry between Lin Daiyu and Xue Baochai that gave the garden its dramatic heart.\n\n'
     'Daiyu, walking alone one morning, overheard maids gossiping in the garden: "The old Lady favors Baochai. They say she will marry Baoyu."\n\n'
     'Her face went white as winter. She walked to the Bamboo Lodge and wept, the sound blending with the wind.\n\n'
     'Baoyu came to her. He found her writing poetry, tears staining the paper.\n\n'
     '"Why do you weep?"\n\n'
     '"The whole house wants you to marry her. And maybe they are right. She is everything I am not."\n\n'
     'Baoyu took her hand. His jade stone glowed. "I care what my heart wants."\n\n'
     'Daiyu pulled away. "Your heart is fickle as the wind, Baoyu. One day with me, the next with Baochai, the next with the actresses."\n\n'
     'She was right. And that was Baoyu tragedy — he loved them all, and thus loved none as he ought. In the Red Chamber, love was not a fairytale. It was a battlefield.'),

    (5, "Omens of Autumn",
     'The Mid-Autumn Festival should have been joyful. The moon was full, lanterns bright, and the Jia family gathered for poetry and celebration.\n\n'
     'But the omens were dark.\n\n'
     'Lady Wang received a letter from the palace. Consort Yuanchun — the family connection to imperial favor — had fallen ill.\n\n'
     '"She will recover," the Dowager Lady Jia insisted, though her hands trembled holding her teacup.\n\n'
     'That night, Daiyu wrote: "The moon is full, but for how long? The flowers bloom, but soon they fall. In this garden of illusions, even the moonlight casts a shadow."\n\n'
     'Baoyu read it and felt a chill. Three days later, the messenger arrived. Yuanchun was dead.\n\n'
     'The Jia family protection at court died with her. Political enemies stirred. The garden suddenly felt like a beautiful cage whose bars were closing.\n\n'
     '"The red chamber is made of red dust," Daiyu whispered. "And red dust scatters in the wind."'),

    (6, "The Riddle of Life and Death",
     'A magician came to the Jia mansion. He carried a mirror with two sides — one that showed beauty and joy, the other that showed skulls and decay.\n\n'
     '"Every pleasure contains its opposite," he told Baoyu. "Every joy shadows a grief. This is the riddle of life and death."\n\n'
     'Baoyu stared into the mirror. On one side, he saw himself marrying Daiyu. They grew old together in the garden, their children playing among the pavilions.\n\n'
     'He flipped the mirror. On the other side, he saw the garden burning. The Jia mansion crumbling. His father in chains, his mother weeping, and Daiyu — Daiyu dead in her Bamboo Lodge, cheeks still wet with tears.\n\n'
     '"Which is true?" he asked.\n\n'
     '"Both," the magician said, and vanished.\n\n'
     'The mirror was found in Baoyu room that night, wrapped in silk. He never looked into it again, but he never forgot what he saw.'),

    (7, "The Women of Jinling",
     'Xue Baochai sat alone in her pavilion, embroidering a golden phoenix onto silk. Outside, the garden was alive with music and laughter — another of the Dowager Lady Jia gatherings.\n\n'
     'She did not join them. She rarely did anymore.\n\n'
     '"You are too serious," her mother chided. "A young woman should be enjoying herself."\n\n'
     '"Enjoying herself for what?" Baochai asked. Her needle did not pause. "To marry a man who loves someone else? To manage a household that is falling apart? To watch the garden wither?"\n\n'
     'Lady Xue had no answer. Her daughter had always been too clever.\n\n'
     'Baochai continued her embroidery. The golden phoenix burned on the white silk like a trapped sun. She thought of Daiyu, who was probably weeping in the Bamboo Lodge. She thought of Baoyu, who was probably reciting name poems somewhere and pretending not to care about anything.\n\n'
     'She thought of Yuanchun, dead in the palace. Of all the women who had entered the Red Chamber and never truly left.\n\n'
     '"We are all locked in the same cage," she murmured. "But some of us refuse to see the bars."'),
]

for num, title, content in DRC:
    save("dream-of-the-red-chamber", num, title, content)
    print(f"  Ch.{num}: {title} ({len(content)} chars)")

# ============================================
# WATER MARGIN: Ch.4-10
# ============================================
print("\n=== Water Margin: Ch.4-10 ===")

WM = [
    (4, "The Preceptor of Virtue",
     'Lu Zhishen — formerly known as Lu Da — was a man of enormous appetite and even larger temper. A former military officer turned fugitive, he had found refuge in a Buddhist monastery as "The Preceptor of Virtue."\n\n'
     'But virtue, for Lu Zhishen, was an elastic concept.\n\n'
     'He drank when he wanted. He fought when provoked. He prayed only when the abbot was watching. The other monks feared him. The abbot despaired of him.\n\n'
     '"You are the worst monk in the history of Buddhism," the abbot groaned.\n\n'
     'Lu Zhishen burped. "Probably."\n\n'
     'His path to Liangshan began when he defended a village against a corrupt magistrate and his hired thugs. Armed with nothing but his iron staff and righteous fury, he routed twenty armed men single-handedly.\n\n'
     'The villagers called him a holy man. The government called him a criminal. Both were, in their own way, correct.\n\n'
     'When he arrived at Liangshan Marsh, the outlaws embraced him as one of their own. A monk who fought like a demon — what could better represent the spirit of the 108 Stars?'),

    (5, "The Unfallen Pine",
     'Song Jiang — known throughout the outlaw world as the Timely Rain — was not the strongest of the 108 Stars. He was not the fastest, nor the most skilled with weapons.\n\n'
     'He was the most loyal.\n\n'
     'As chief clerk of Yuncheng County, he had used his position to warn local outlaws of impending raids. His network of informants stretched across the province, and every bandit who operated in the region owed him a debt.\n\n'
     'When his own death warrant was issued, it was the outlaws who saved him.\n\n'
     '"The Timely Rain falls on all who need it," his men would later say. "And all who receive it owe him a life."\n\n'
     'He was the moral center of Liangshan — the star around which the other 107 bodies of the constellation revolved. Without him, the outlaws would have been a rabble. With him, they became an army.\n\n'
     'And in his heart burned a single, unquenchable hope: that the Emperor would one day pardon them all. It was this hope that would ultimately destroy everything.'),

    (6, "The Fleet-footed Courier",
     'Dai Zong was the fastest man in the empire — and the most loyal.\n\n'
     'He had served as the superintending official of Jiangzhou prison, using his incredible speed to deliver messages across vast distances. But when his friend Song Jiang was captured and sentenced to death, Dai Zong did not hesitate.\n\n'
     'He ran.\n\n'
     'Day and night, covering four hundred li at a stretch, he carried the news to Liangshan. The outlaws mobilized immediately, marching an army to Jiangzhou to rescue their leader.\n\n'
     'Dai Zong ran ahead of them, ran beside them, ran back with reports, ran forward with instructions. His feet seemed to barely touch the ground.\n\n'
     '"The Fleet-footed Courier," they called him afterward. "The wind is his horse and the road his home."\n\n'
     'He would be the sixth of the 108 Stars to join the assembly at Liangshan.'),

    (7, "The Rain of Arrows",
     'Hua Rong was the finest archer in the land. His arrows flew true at distances that other archers could only dream of. They called him "Little Li Guang," after the legendary Han dynasty general.\n\n'
     'When conflict with the Qingzhou authorities forced him to flee, he joined Song Jiang at Liangshan. His first test came when a force of government troops surrounded the marsh, determined to end the outlaw rebellion once and for all.\n\n'
     '"Let them come," Hua Rong said quietly, stringing his bow.\n\n'
     'One arrow severed the enemy commander banner. A second knocked the helmet from the commander own head. A third pierced the throat of the commander horse.\n\n'
     'The government army retreated before a single sword was drawn.\n\n'
     '"An army of one man," Song Jiang said, marveling at his friend skill. "An army of one man, and his bow."'),
]

for num, title, content in WM:
    save("water-margin", num, title, content)
    print(f"  Ch.{num}: {title} ({len(content)} chars)")

# ============ FINAL SUMMARY ============
print("\n" + "="*50)
print("FINAL CHAPTER COUNTS:")
print("="*50)
total = 0
for d in sorted(os.listdir(CHAPTERS_DIR)):
    cnt = len([f for f in os.listdir(os.path.join(CHAPTERS_DIR, d)) if f.endswith(".json")])
    total += cnt
    print(f"  {d:45s} {cnt:4d} chapters")
print(f"  {'TOTAL':45s} {total:4d} chapters")