#!/usr/bin/env python3
"""Batch generate 3 chapters for each classic novel (<5 chapters).
Each chapter: 5 paragraphs English adaptation of the original Chinese classic.
"""
import json, os, time

CHAPTERS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'chapters')
NOVELS_JSON = os.path.join(os.path.dirname(__file__), '..', 'data', 'novels.json')

TEMPLATES = {

'analects': {
  'intro': 'Confucius said',
  'chapters': [
    {
      'title': 'On Learning and Practice',
      'lines': [
        'The Master said: "Is it not a pleasure to learn and practice what you have learned? Is it not delightful to have friends come from afar? Is it not gentlemanly not to feel resentment when others do not recognize your worth?"',
        'Adept Youzi added: "A man who respects his parents and elders rarely challenges authority. When the root is firm, the Way grows. Filial piety and fraternal respect — these are the root of humaneness."',
        'The Master said: "Clever words and an ingratiating appearance are rarely signs of humaneness."',
        'Master Zeng examined himself daily on three points: "Have I been loyal in serving others? Have I been trustworthy with friends? Have I practiced what I teach?"',
        'The Master said: "To govern a state of a thousand chariots, attend to business with reverence, be trustworthy, keep expenditures frugal, love the people, and employ the people at proper seasons."',
      ]
    },
    {
      'title': 'On Virtue and Integrity',
      'lines': [
        'The Master said: "The gentleman understands righteousness; the small man understands profit."',
        '"When you see a worthy person, think of how to emulate them. When you see an unworthy person, examine yourself."',
        '"Virtue is not solitary; it always has neighbors."',
        '"The gentleman is broad-minded and not prejudiced. The small man is prejudiced and not broad-minded."',
        'Ji Kangzi asked Confucius about governing: "What if I kill the unprincipled for the good of the principled?" The Master replied: "Why use killing in governing? If you desire goodness, the people will be good. The virtue of the gentleman is the wind; the virtue of the small man is grass. When the wind blows, the grass bends."',
      ]
    },
    {
      'title': 'On Wisdom and Self-Cultivation',
      'lines': [
        'The Master said: "At fifteen I set my heart on learning. At thirty I stood firm. At forty I had no doubts. At fifty I understood the Mandate of Heaven. At sixty my ear was attuned. At seventy I could follow my heart without transgressing."',
        '"To know what you know and to know what you do not know — that is true knowledge."',
        '"Learning without thinking is labor lost. Thinking without learning is perilous."',
        '"The gentleman is at ease without arrogance. The small man is arrogant without ease."',
        'Zigong asked: "Is there one word that can guide one through life?" The Master replied: "Reciprocity. Do not impose on others what you yourself do not desire."',
      ]
    },
  ]
},

'book-of-songs': {
  'intro': 'From the Book of Songs',
  'chapters': [
    {
      'title': 'The Ospreys',
      'lines': [
        'Guan-guan, cry the ospreys, on the islet in the river. The gentle and graceful maiden — a fit companion for the gentleman.',
        'Short and long the water plants, left and right we gather them. The gentle and graceful maiden — waking and sleeping he longs for her. Longing, longing without reaching her, waking and sleeping he thinks of her.',
        'Tossing and turning, unable to rest. Short and long the water plants, left and right we pluck them. The gentle and graceful maiden — with lutes great and small we welcome her.',
        'Short and long the water plants, left and right we choose the finest. The gentle and graceful maiden — with bells and drums we delight her.',
        'This poem, the first in the Classic of Poetry, captures the essential rhythm of Chinese verse: nature mirroring human emotion, restrained yet deeply felt. Three thousand years later, the ospreys still cry on the islets of the Yellow River.',
      ]
    },
    {
      'title': 'Songs of Love and Longing',
      'lines': [
        'In the wilds there is a dead deer. White grass wraps it round. A maiden has thoughts of spring. A fine gentleman leads her on.',
        'In the woods are clustering shrubs. In the wilds is a dead deer, wrapped in white grass. There is a maiden, fair as jade.',
        '"Slowly, gently, do not move my kerchief! Do not make the dog bark!"',
        'The peach tree is young and tender, its blossoms glowing bright. This maiden goes to her new home — fitting bride for a fitting groom.',
        'These folk songs, collected from the states of ancient China, speak across three millennia with startling immediacy. Love, longing, the beauty of the natural world — nothing essential has changed.',
      ]
    },
    {
      'title': 'Odes of the Temple and Altar',
      'lines': [
        'Silent and solemn are the spirits. Cannot they be seen? They descend at the offering of flesh and grain.',
        'How great is King Wen! His brilliance shines above. Although Zhou is an old state, its Mandate is new.',
        'The millet grows thick and tall, the sacrificial grain ripens. We fill the vessels, we offer the pure wine.',
        'The music rises, the dancers move in rhythm. The ancestors draw near, blessing the living with prosperity.',
        'These temple odes mark the founding moment of Chinese civilization as a self-conscious tradition. The Zhou dynasty invented the idea that heaven grants its mandate to the virtuous ruler. This concept would shape East Asian politics for three thousand years.',
      ]
    },
  ]
},

'zhuangzi': {
  'intro': 'Master Zhuang said',
  'chapters': [
    {
      'title': 'Happy Excursion',
      'lines': [
        'In the northern darkness there is a fish named Kun. Its size is unknown — thousands of miles across. It transforms into a bird named Peng. The Peng\'s back is unknown — thousands of miles across. When it rises in flight, its wings are like clouds covering the sky.',
        'The cicada and the little dove laughed at the Peng: "We fly up to the elm tree, sometimes not even making it, and fall back to the ground. Why would anyone fly ninety thousand miles to the south?"',
        'Zhuangzi smiled: "A small knowledge cannot match great knowledge. The morning mushroom knows nothing of twilight and dawn. The summer cicada knows nothing of spring and autumn."',
        '"The perfect man has no self. The spiritual man has no achievement. The sage has no name."',
        'Zhuangzi dreamed he was a butterfly. Fluttering happily, he was a butterfly, conscious only of his butterfly joy. Suddenly he woke — and there he was, Zhuangzi. Was Zhuangzi dreaming he was a butterfly? Or was the butterfly dreaming it was Zhuangzi?',
      ]
    },
    {
      'title': 'The Equality of Things',
      'lines': [
        'The sound of the earth is the wind blowing through ten thousand hollows. The sound of heaven — what is it? The wind blows differently through every opening. Each thing makes its own sound. Who is the musician?',
        '"Everything is right. Everything is wrong. From one perspective, yes. From another, no. The sage does not argue. He watches from the center of the ring where all opposites meet."',
        '"When we sleep, the soul communes with spirits. When we wake, the body resumes its cage. Day after day we struggle and strive — and do we know where it all ends?"',
        'A keeper of monkeys said: "I\'ll give you three acorns in the morning and four in the evening." The monkeys were angry. "Then four in the morning and three in the evening." The monkeys were delighted. The acorns were the same number. The monkeys were mastered by their own emotions.',
        '"The Way has no boundaries. Words have no fixed meaning. Only because we draw boundaries do boundaries exist. Heaven and earth were born with me. The ten thousand things and I are one."',
      ]
    },
    {
      'title': 'Nourishing Life',
      'lines': [
        'Cook Ding was cutting up an ox for Lord Wenhui. Where his hand touched, his shoulder leaned, his foot pressed, his knee braced — zip, whoosh! The blade sang, never missing a beat, moving in rhythm like the Dance of the Mulberry Grove.',
        '"A good cook changes his knife once a year — he cuts. A mediocre cook changes his knife once a month — he hacks. I\'ve used this knife for nineteen years, cutting thousands of oxen, and the blade is still as sharp as when it came from the whetstone."',
        '"There are spaces in the joints. The blade has no thickness. When what has no thickness enters where there is space — how much room to spare! That\'s why after nineteen years the blade is still sharp."',
        '"What I care about is the Way, which goes beyond skill. When I first began cutting oxen, I saw nothing but oxen. After three years, I no longer saw the whole ox. Now I go by spirit, not by sight."',
        'Lord Wenhui said: "Excellent! From the words of Cook Ding, I have learned how to nourish life." Zhuangzi teaches us: there is a way through every difficulty, a space between the joints of every problem. Find the gap, and the blade never dulls.',
      ]
    },
  ]
},

'sunzi': {
  'intro': 'Sunzi said',
  'chapters': [
    {
      'title': 'Laying Plans',
      'lines': [
        'Warfare is the greatest affair of state, the foundation of life and death, the Way to survival or extinction. It must be thoroughly studied.',
        'The art of war is governed by five constant factors: the Moral Law, Heaven, Earth, the Commander, and Method and Discipline.',
        '"All warfare is based on deception. When able, appear unable. When near, appear far. When far, appear near. Hold out baits to entice the enemy. Feign disorder and strike."',
        '"If you know the enemy and know yourself, you need not fear the result of a hundred battles. If you know yourself but not the enemy, for every victory you will suffer a defeat. If you know neither the enemy nor yourself, you will succumb in every battle."',
        'The supreme art of war is to subdue the enemy without fighting. He who excels at resolving difficulties does so before they arise.',
      ]
    },
    {
      'title': 'Strategic Offensive',
      'lines': [
        'In war, the best policy is to take the enemy\'s state whole and intact. To destroy it is inferior. To capture the enemy\'s army whole is better than to destroy it. To capture a regiment, a company, or a squad whole is better than to destroy them.',
        '"He who excels in warfare does not win a hundred victories in a hundred battles. Instead, he subdues the enemy\'s army without fighting at all."',
        '"There are three ways a ruler can bring misfortune upon his army: ordering advance when the army cannot, ordering retreat when the army cannot, and interfering with military administration."',
        '"Know when to fight and when not to fight. Know how to handle both superior and inferior forces. Have an army animated by the same spirit throughout all ranks. Be prepared and wait to take the enemy unprepared."',
        'The victorious strategist seeks battle only after the victory has been won. He who is destined to defeat fights first and then looks for victory.',
      ]
    },
    {
      'title': 'The Nine Variables',
      'lines': [
        'In difficult terrain, do not encamp. In intersecting terrain, join with allies. In desperate terrain, fight. There are roads not to follow. There are armies not to attack. There are walled cities not to besiege. There are positions not to contest. There are commands of the sovereign not to obey.',
        '"The art of war teaches us to rely not on the likelihood of the enemy not coming, but on our own readiness to receive him. Not on the chance of him not attacking, but on making our own position unassailable."',
        '"Consider five dangers that may befall a general: reckless courage leading to death, cowardice leading to capture, a hot temper provoked by insults, a delicacy of honor sensitive to shame, and excessive compassion for his men leading to worry and trouble."',
        '"If your opponent is of choleric temper, seek to irritate him. Pretend to be weak so that he grows arrogant. If he is at ease, give him no rest. If his forces are united, separate them."',
        'Attack where he is unprepared. Emerge where you are not expected. These are the keys to victory in warfare.',
      ]
    },
  ]
},

'da-xue': {
  'intro': 'The Great Learning teaches',
  'chapters': [
    {'title': 'The Way of the Great Learning', 'lines': [
      'The Way of the Great Learning lies in manifesting bright virtue, in loving the people, and in resting in the highest good.',
      'Knowing where to rest, one becomes settled. Being settled, one can be tranquil. Being tranquil, one can be at peace. Being at peace, one can reflect. Only through reflection can one attain understanding.',
      'Things have their roots and branches. Affairs have their beginnings and ends. To know what comes first and what comes last — that is to draw near to the Way.',
      'The ancients who wished to manifest bright virtue throughout the world first ordered their states. To order their states, they first regulated their families. To regulate their families, they first cultivated themselves.',
      'From the Son of Heaven down to the common people, all must regard self-cultivation as the root. When the root is in disorder, the branches cannot be well-ordered.',
    ]},
    {'title': 'On Self-Cultivation', 'lines': [
      'What is meant by "cultivating oneself lies in rectifying the heart" is this: When one is affected by anger, the heart is not correct. When affected by fear, the heart is not correct. When affected by fondness, the heart is not correct.',
      'When the mind is not present, we look but do not see, we listen but do not hear, we eat but do not taste. This is what is meant by "cultivation of the person lies in rectifying the heart."',
      'What is meant by "regulating the family lies in cultivating oneself" is this: People are partial toward those they love, biased toward those they despise, in awe of those they revere.',
      'Thus, few in the world can recognize the faults of those they love, or see the virtues of those they dislike. As the saying goes: "A man does not know the faults of his son; he does not know the richness of his own growing corn."',
      'This is why cultivation of oneself is required before regulating the family. Without self-cultivation, one cannot see clearly.',
    ]},
    {'title': 'On Governing', 'lines': [
      'The ruler who has virtue will have the people. He who has the people will have the territory. He who has the territory will have wealth. He who has wealth will have resources to use.',
      'Virtue is the root. Wealth is the branch. If the root is neglected while the branch is emphasized, the people will scatter and the state will fall.',
      '"Do not use what you hate in those above you to command those below. Do not use what you hate in those below you to serve those above."',
      '"If one word can ruin an undertaking, that word is this: getting wealth."',
      'The noble person first practices what he preaches, and then preaches what he practices. The Way of the Great Learning is, in the end, remarkably simple, and remarkably difficult: be good, and goodness will follow.',
    ]},
  ]
},

'zhong-yong': {
  'intro': 'The Doctrine of the Mean',
  'chapters': [
    {'title': 'The Central Harmony', 'lines': [
      'What Heaven has conferred is called Nature. According to this nature is called the Way. Cultivating the Way is called Instruction.',
      'The Way cannot be departed from for even a moment. What can be departed from is not the Way. Therefore, the gentleman is cautious where he is not seen and apprehensive where he is not heard.',
      'Before the feelings of pleasure, anger, sorrow, and joy arise, this is called the center. When they arise and all attain their proper measure, this is called harmony.',
      'The center is the great root of all under heaven. Harmony is the all-pervading Way of the world. Let the center and harmony be perfectly realized, and heaven and earth will find their proper place and all things will be nourished.',
      'Confucius said: "The gentleman embodies the Mean. The petty person acts contrary to the Mean. The gentleman\'s embodiment of the Mean comes from his being a gentleman who is always in the center. The petty person\'s contrary action comes from his being a petty person who has no caution."',
    ]},
    {'title': 'The Way of the Gentleman', 'lines': [
      'The Master said: "The Way is not far from man. When a man pursues the Way by departing from human nature, that cannot be the Way."',
      '"The gentleman seeks it in himself. The petty man seeks it in others."',
      '"In archery we have something resembling the Way of the gentleman. When the archer misses the center of the target, he turns and seeks the cause of his failure within himself."',
      'The gentleman does what is proper to his position and does not wish to go beyond it. In a position of wealth and honor, he does what is proper to wealth and honor. In a position of poverty and lowliness, he does what is proper to poverty and lowliness.',
      'The Way of the gentleman may be compared to traveling a great distance: one must start from what is near. It may be compared to ascending a height: one must start from below.',
    ]},
    {'title': 'Sincerity as the Way', 'lines': [
      'Sincerity is the Way of Heaven. The attainment of sincerity is the Way of man. He who possesses sincerity achieves the mean without effort, apprehends without thinking, and embodies the Way with ease.',
      'He who attains to sincerity is he who chooses the good and holds fast to it. Study it extensively. Inquire into it accurately. Reflect on it carefully. Discriminate it clearly. Practice it earnestly.',
      'If another succeeds with one effort, I will use a hundred. If another succeeds with ten, I will use a thousand. If one truly follows this path, though foolish, one will become enlightened; though weak, one will become strong.',
      'Sincerity means the completion of the self. The Way means guiding oneself. Sincerity is the beginning and end of all things. Without sincerity, there is nothing.',
      'It is only the most sincere person under Heaven who can fully develop his nature, and thus assist in the transforming and nourishing powers of Heaven and Earth.',
    ]},
  ]
},

'hanfeizi': {
  'intro': 'Master Han Fei wrote',
  'chapters': [
    {'title': 'The Five Vermin', 'lines': [
      'In ancient times, men did not plow but plants and trees were sufficient for food. Women did not weave but the skins of animals were sufficient for clothing. The people were few and goods abundant, so there was no strife.',
      'Now, a man with five children is not considered to have many. Each child in turn has five children, and before the grandfather dies, there may be twenty-five descendants. Thus people are many and goods scarce, so they struggle and fight.',
      'Confucians with their learning confuse the law. Wandering swordsmen with their martial prowess violate prohibitions. Partisan talkers with their sophistry create disorder.',
      'The sovereign who rules a state must destroy these five vermin: scholars, speech-makers, swordsmen, palace guards who evade military service, and merchants who deal in luxury goods.',
      'A wise ruler does not cultivate benevolence. He cultivates laws. When the law is clear, the people know what to do and what to avoid. The state that follows the law prospers. The state that follows the whims of men perishes.',
    ]},
    {'title': 'The Two Handles', 'lines': [
      'The enlightened ruler controls his ministers by means of two handles alone: punishment and reward. By punishment is meant the power to inflict death. By reward is meant the power to bestow honors.',
      'If the ministers are able to speak but the ruler does not judge their words according to results, how can there be any means of preventing them from deceiving the ruler?',
      'The ruler must never reveal his desires. If he reveals what he likes, the ministers will flatter accordingly. If he reveals what he hates, the ministers will hide what he dislikes.',
      'Hence the saying: "Remove likes and dislikes, and the ministers reveal their true form. Remove wisdom and cleverness, and the ministers will behave properly."',
      'Han Fei was a student of the Confucian Xunzi but took a radically different path. Where Confucius looked to the goodness of the sage-ruler, Han Fei looked to the effectiveness of the legal system. His ideas helped Qin Shi Huang unify China.',
    ]},
    {'title': 'The Difficulty of Persuasion', 'lines': [
      'The difficulty of persuasion lies not in my knowing what to say, nor in my being able to express what I know, nor in my daring to speak fully. The difficulty lies in knowing the mind of the person I am trying to persuade and fitting my words to it.',
      'If the one you persuade is seeking fame and you speak to him of profit, he will consider you base. If he secretly desires profit but outwardly seeks fame, and you speak to him of fame, he will outwardly accept but inwardly reject you.',
      'When speaking of affairs, do not touch on matters that cause suspicion. When praising a person, do not do so in a way that seems to criticize another. Speak of achievements, not of failures.',
      'A dragon is a creature that can be tamed and ridden. Yet on the underside of its throat are scales that are a foot wide. Whoever touches these dies. The ruler, too, has his reverse scales. The persuader who avoids them will succeed.',
      'Han Fei himself could not avoid the ruler\'s reverse scales. Imprisoned by Li Si on false charges, he died in the very legal system he championed. His writings, however, survived to shape two thousand years of Chinese statecraft.',
    ]},
  ]
},

'xunzi': {
  'intro': 'Master Xun said',
  'chapters': [
    {'title': 'Encouraging Learning', 'lines': [
      'The gentleman says: Learning must never cease. Blue comes from indigo but is bluer than indigo. Ice comes from water but is colder than water.',
      'Wood that meets the carpenter\'s line becomes straight. Metal that meets the whetstone becomes sharp. The gentleman who studies broadly and examines himself daily will become wise and free from error.',
      '"I have spent an entire day thinking, and it was not as good as a moment of study. I have stood on tiptoe to look, and it was not as good as climbing high to see."',
      'If you do not climb a high mountain, you will not know the height of heaven. If you do not look into a deep valley, you will not know the thickness of the earth. If you do not hear the words of the ancient kings, you will not know the greatness of learning.',
      'Unlike Mencius who believed human nature is good, Xunzi argued that human nature is evil and must be corrected through ritual, education, and law. He was the teacher of Han Fei and Li Si — the architects of the Qin unification.',
    ]},
    {'title': 'Human Nature is Evil', 'lines': [
      'Human nature is evil. Goodness is the result of conscious activity. By nature, people are born with a love of profit. If they follow this, struggle and robbery ensue, and courtesy dies.',
      'By nature, people are born with envy and hatred. If they follow these, injury and destruction follow, and loyalty and trust perish. By nature, people desire the pleasures of the senses. If they follow this, lewdness ensues, and ritual and righteousness collapse.',
      'A warped piece of wood must be straightened with the press-frame and steamed into shape before it becomes straight. A blunt piece of metal must be ground on the whetstone before it becomes sharp. Similarly, the evil nature of man must be corrected by teachers and ritual.',
      '"Ask why the sage is a sage, and I will answer: it is because of the conscious effort he has made. Ask why the ordinary person is ordinary, and I will answer: it is because he has let his nature run free."',
      'Mencius said human nature is good. Xunzi said human nature is evil. Both agreed on the cure: education, ritual, and self-cultivation. The disagreement was about the starting point, not the destination.',
    ]},
    {'title': 'On Ritual', 'lines': [
      'Where did ritual arise? Humans are born with desires. When desires are not satisfied, there is seeking. When seeking has no measure or limit, there is conflict. Conflict leads to disorder. The ancient kings hated disorder, so they established ritual and righteousness to make distinctions.',
      'Ritual provides the measure. It is to human life what the balance-beam is to weight, what the ink-line is to straightness, what the compass is to roundness.',
      'Music enters deeply into people and transforms them quickly. Therefore, the ancient kings valued music. Joyful music produces harmony; solemn music produces reverence.',
      'When music is played in the ancestral temple, ruler and minister, high and low, listen together and none fail to be harmoniously respectful. When it is played in the household, father and son, elder and younger, listen together and none fail to be harmoniously affectionate.',
      'Xunzi\'s genius was to give ritual a rational foundation rather than a supernatural one. Ritual does not appease the gods — it structures human desire so that civilization can flourish.',
    ]},
  ]
},

'thirty-six-stratagems': {
  'intro': 'Ancient wisdom teaches',
  'chapters': [
    {'title': 'Stratagems of Deception', 'lines': [
      'Cross the sea without Heaven\'s knowledge: Hide your true intentions by doing the ordinary. When something is done repeatedly, it becomes invisible. Conceal the secret within the open.',
      'Besiege Wei to rescue Zhao: Avoid the strong and attack the weak. When the enemy is too powerful to attack directly, strike at something they hold dear.',
      'Kill with a borrowed knife: Use a third party to do your work. Cause harm indirectly. Let an ally weaken your enemy while you preserve your strength.',
      'Wait at ease for the exhausted enemy: When the enemy exhausts themselves through movement, remain still, preserve your energy, and strike when they are weak and you are strong.',
      'Loot a burning house: When chaos reigns, strike. When your enemy is in internal turmoil, that is your moment. A state in confusion offers the greatest opportunity.',
    ]},
    {'title': 'Stratagems of Confrontation', 'lines': [
      'Make a sound in the east, strike in the west: Create a feint. When the enemy\'s attention is drawn in one direction, the real attack comes from the opposite side.',
      'Create something from nothing: A lie told often enough becomes truth. Fake a reality so convincingly that the enemy accepts it as fact.',
      'Openly repair the walkway, secretly march to Chencang: Deceive with an obvious action while executing a hidden plan. The visible project draws all eyes; the invisible one achieves the goal.',
      'Watch the fire from the other shore: When your enemies destroy each other, do not intervene. Patience is a weapon. Let the fire burn; only cross the river after it dies.',
      'Hide a knife behind a smile: Befriend your enemy while preparing to destroy them. The warmest welcome may conceal the sharpest blade.',
    ]},
    {'title': 'Stratagems for Desperate Situations', 'lines': [
      'The beauty trap: Use charm to weaken the enemy. The strongest fortress falls to the gentlest seduction.',
      'The empty fort strategy: When you have nothing, pretend you have everything. Open the gates, sweep the path, and sit calmly. The enemy, suspecting an ambush, will retreat.',
      'Use the enemy\'s own spies against them: Turn the enemy\'s intelligence network into your own weapon. Feed them false information. Make their eyes your eyes.',
      'Inflict injury on yourself to win trust: The only way to be trusted by the enemy is to share their wounds. The deepest deception comes wrapped in shared suffering.',
      'If all else fails, retreat: When defeat is inevitable, withdrawal is not cowardice — it is strategy. Live to fight another day. Three kingdoms, thirty-six stratagems, one eternal truth: the best battle is the one not fought.',
    ]},
  ]
},

'tang-shi': {
  'intro': 'Tang Dynasty poets sang',
  'chapters': [
    {'title': 'Drinking Alone Under the Moon', 'lines': [
      'A jug of wine among the flowers. I drink alone, no friend nearby. Raising my cup, I invite the bright moon. With my shadow, we make three.',
      'The moon does not know how to drink. My shadow only follows my body. Still, moon and shadow will be my companions for now. We must enjoy spring while it lasts.',
      'I sing, and the moon lingers. I dance, and my shadow tangles. While sober, we share our joy. Once drunk, we go our separate ways.',
      'Forever bound in friendship without emotion, we will meet again in the distant River of Stars. Li Bai wrote this poem in exile, far from the imperial court that once celebrated him.',
      'Li Bai — also known as Li Po — is perhaps China\'s most beloved poet. Legend says he drowned trying to embrace the moon\'s reflection in the water. It is impossible to know where the man ends and the legend begins — and that, perhaps, is the point.',
    ]},
    {'title': 'Spring Landscape', 'lines': [
      'The nation is broken, but mountains and rivers remain. Spring fills the city — grass and trees grow thick. Touched by the times, flowers shed tears. Hating separation, birds startle the heart.',
      'Beacon fires have burned for three months now. A letter from home would be worth ten thousand pieces of gold. I scratch my white head — the hair grows thinner, too thin now even for a pin.',
      'Du Fu wrote these lines during the An Lushan Rebellion, when the Tang capital Chang\'an fell to rebels and the poet was separated from his family.',
      'Where Li Bai soared like a Daoist immortal, Du Fu stayed rooted in the soil of human suffering. He wrote of war, hunger, separation, and the quiet dignity of ordinary people.',
      'In Chinese literary tradition, Li Bai is the "Immortal Poet" and Du Fu the "Poet Sage." Together they represent the two poles of the Chinese poetic spirit: transcendence and compassion.',
    ]},
    {'title': 'Quiet Night Thoughts', 'lines': [
      'Before my bed, the bright moonlight — could it be frost upon the ground? Lifting my head, I gaze at the bright moon. Lowering my head, I think of home.',
      'These twenty words by Li Bai are the most memorized poem in Chinese history. Every schoolchild in China knows them. The poem captures in a single breath the universal experience of homesickness.',
      'Tang poetry achieved its perfection through compression. Every character carries weight; every image opens onto infinity. A mountain is never just a mountain — it is solitude, permanence, the indifference of nature to human suffering.',
      '"In the vast desert, smoke rises straight. Over the long river, the sun sinks round." Wang Wei\'s couplet is pure Tang poetry: the horizontal line of desert smoke, the vertical circle of the setting sun, and the silence between them.',
      'Three hundred years of Tang poetry gave us fifty thousand poems that survive. They represent the golden age of Chinese verse, when everything — love, war, nature, exile, friendship, death — was compressible into eight lines of five or seven characters.',
    ]},
  ]
},

'dao-de-jing': {
  'intro': 'Laozi said',
  'chapters': [
    {'title': 'The Nameless Origin', 'lines': [
      'The Way that can be spoken is not the eternal Way. The name that can be named is not the eternal name.',
      'Nameless — the origin of heaven and earth. Named — the mother of the ten thousand things.',
      'Free from desire, you see the mystery. Filled with desire, you see only the manifestations. These two emerge together but differ in name. The unity is called darkness. Darkness within darkness — the gate to all mystery.',
      'The Tao is empty, yet when used, it never needs to be filled. So deep — it seems to be the ancestor of all things. It blunts the sharp, unties the tangled, softens the glare, and settles the dust.',
      'I do not know whose child it is. It seems to have existed before the Lord.',
    ]},
    {'title': 'The Valley Spirit', 'lines': [
      'The highest good is like water. Water benefits the ten thousand things without contention. It flows to places men despise. Thus it is close to the Way.',
      'Thirty spokes share one hub. It is the empty space at the center that makes the wheel useful. Shape clay into a vessel. It is the hollow inside that makes the vessel useful. Cut doors and windows for a room. It is the emptiness that makes the room useful.',
      'Therefore, benefit comes from what is there. Usefulness comes from what is not there.',
      'The five colors blind the eye. The five tones deafen the ear. The five flavors dull the palate. Racing and hunting madden the mind. Rare goods tempt men to wrongdoing.',
      'Therefore the sage is for the belly, not for the eye. He rejects that and chooses this.',
    ]},
    {'title': 'Returning to the Root', 'lines': [
      'Attain the ultimate emptiness. Hold to the deepest stillness. The ten thousand things arise together — I watch their return.',
      'All things flourish, then each returns to its root. Returning to the root is stillness. Stillness is returning to destiny. Returning to destiny is the eternal. Knowing the eternal is enlightenment.',
      'Not knowing the eternal, one acts blindly — and comes to harm. Knowing the eternal, one is all-embracing. Being all-embracing, one is impartial. Being impartial, one is kingly. Being kingly, one is of heaven. Being of heaven, one is of the Tao. Being of the Tao, one endures.',
      '"The Tao produces one. One produces two. Two produces three. Three produces the ten thousand things. The ten thousand things carry yin and embrace yang. The blending of these vital forces produces harmony."',
      '"A journey of a thousand miles begins with a single step." This is perhaps the most famous line in the Dao De Jing — and it is not in the received text at all, but a later saying inspired by the spirit of Laozi.',
    ]},
  ]
},

'three-character-classic': {
  'intro': 'The Three Character Classic',
  'chapters': [
    {'title': 'On Human Nature and Education', 'lines': [
      'People at birth are fundamentally good in nature. Their natures are similar; their habits make them different.',
      'If a child is not taught, their nature will go astray. The way of teaching demands complete dedication.',
      'Once, the mother of Mencius chose a neighborhood. When her son did not study, she cut the loom. To teach her child, she would not give up.',
      'Dou Yanshan had the right method. He taught five sons, each raised the family name. To feed without teaching is a father\'s fault. To teach without strictness is a teacher\'s laziness.',
      'If a child does not learn, it is not right. If they do not learn in youth, what will they be when old? Jade that is not cut cannot be a vessel. A person who does not learn cannot understand righteousness.',
    ]},
    {'title': 'The Order of Learning', 'lines': [
      'First, practice filial piety and fraternal respect. Next, learn to see and hear. Know a certain number; know a certain pattern.',
      'One to ten, ten to a hundred, a hundred to a thousand, a thousand to ten thousand. The three powers are heaven, earth, and man. The three luminaries are sun, moon, and stars.',
      'The three bonds are: duty between ruler and subject, love between father and son, harmony between husband and wife.',
      'Spring and summer, autumn and winter — these four seasons revolve without end. South and north, west and east — these four directions correspond to the center.',
      'Water and fire, wood and metal, earth — these are the five elements, rooted in number. Humaneness and justice, ritual and wisdom, trustworthiness — these five constants must not be confused.',
    ]},
    {'title': 'Classics and Histories', 'lines': [
      'The Analects, in twenty sections, groups the disciples, recording the good words. The Works of Mencius, in seven chapters, teaches the Way and speaks of virtue and humaneness.',
      'The Doctrine of the Mean was written by Zisi. The mean is not biased; the constant is not changed. The Great Learning was written by Master Zeng. It teaches self-cultivation, family regulation, and governing.',
      'When the Classic of Filial Piety is understood, the Six Classics can be read in sequence. The Book of Songs, the Book of Documents, the Book of Rites, the Book of Changes, the Spring and Autumn Annals — these are the Six Classics, which must be studied.',
      'From Fu Xi through the Yellow Emperor was the Age of Legend. Yao and Shun were called the Two Emperors. Yu of Xia and Tang of Shang were called the Two Kings. The Zhou lasted eight hundred years — the longest dynasty.',
      'Study history to understand the rise and fall of nations. Read the classics to comprehend the Way of Heaven and Man. Diligent study brings success. Neglect brings only regret.',
    ]},
  ]
},

'chinese-poetry': {
  'intro': 'Classical Chinese Poetry',
  'chapters': [
    {'title': 'The Rise of Poetry', 'lines': [
      'Chinese poetry begins with the Book of Songs, compiled around 600 BCE. Its 305 poems — folk songs, court hymns, ritual odes — established the patterns that would echo through three millennia.',
      'The shi form dominated for centuries: lines of four, five, or seven characters, with strict tonal patterns and end rhyme. This was the form of Li Bai, Du Fu, and Wang Wei in the Tang dynasty.',
      'The ci form emerged in the late Tang and flourished in the Song. Written to existing melodies, ci poems have lines of varying length. Li Qingzhao, China\'s greatest female poet, mastered this form.',
      '"Searching, searching — lonely, cold, and clear. In misery, in sorrow, and in woe." Li Qingzhao\'s lines capture the grief of losing her husband and her country to Jurchen invaders. The repetition of the opening words — xun xun mi mi — creates a soundscape of desperation that no translation can fully capture.',
      'The qu form of the Yuan dynasty brought vernacular language and humor to poetry. And through all these changes, one thing remained constant: the Chinese poet as witness — to nature, to love, to the rise and fall of dynasties.',
    ]},
    {'title': 'Nature and the Poetic Gaze', 'lines': [
      '"Empty mountain, no one in sight. Only the sound of someone talking. Sunlight enters the deep wood, shines on the green moss again." Wang Wei\'s Deer Enclosure is twenty characters and an entire world.',
      'The Chinese poet does not describe nature — they inhabit it. The mountain is not a backdrop but a companion. The river is not a metaphor but a teacher.',
      '"A thousand mountains, no bird in flight. Ten thousand paths, no human trace. A solitary boat, bamboo cloak and hat — an old man fishing the cold river snow." Liu Zongyuan wrote this after being exiled to the southern wilderness for political dissent.',
      'Tao Yuanming quit his government post to farm chrysanthemums. "I pluck chrysanthemums beneath the eastern hedge and gaze afar toward the southern mountains." This single couplet became the emblem of the Chinese hermit-poet ideal.',
      'The poetic gaze in the Chinese tradition is not about conquering nature with language. It is about making oneself small enough to enter the landscape — and in that smallness, finding infinity.',
    ]},
    {'title': 'Poetry of Friendship and Farewell', 'lines': [
      '"The city walls, three layers of defense. But the sorrow of parting — ten thousand layers deep." Chinese poetry is full of farewells. Officials were constantly being posted to distant provinces. Friendships were maintained across vast distances through poems sent by courier.',
      '"I urge you to drink one more cup of wine. West of the Yang Pass, there are no old friends." Wang Wei\'s farewell poem was set to music and sung at every parting for over a thousand years.',
      'Bai Juyi and Yuan Zhen exchanged hundreds of poems over decades of separation. "I think of you, sir, as I read your poems by lamplight. When the lamp goes out, the sky is not yet bright."',
      '"Green hills north of the wall, white waters east of the city. This place — once we have parted, the lone tumbleweed will journey ten thousand li. Floating clouds — the traveler\'s thoughts. Setting sun — an old friend\'s feelings." Li Bai to a friend departing for a distant post.',
      'In the Chinese tradition, the poem is a gift, a social act, a thread connecting two souls across time and space. To send a poem is to send a piece of oneself.',
    ]},
  ]
},

}

def generate_chapters():
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'chapters')
    
    # Map slug prefixes to templates
    slug_map = {
        'analects': 'analects',
        'book-of-songs': 'book-of-songs',
        'zhuangzi': 'zhuangzi',
        'sunzi': 'sunzi',
        'da-xue': 'da-xue',
        'zhong-yong': 'zhong-yong',
        'hanfeizi': 'hanfeizi',
        'xunzi': 'xunzi',
        'thirty-six-stratagems': 'thirty-six-stratagems',
        'tang-shi': 'tang-shi',
        'dao-de-jing': 'dao-de-jing',
        'three-character-classic': 'three-character-classic',
        'chinese-poetry': 'chinese-poetry',
    }
    
    results = []
    for slug_prefix, template_key in slug_map.items():
        tpl = TEMPLATES.get(template_key)
        if not tpl:
            continue
        
        # Find all slugs matching this prefix
        import glob
        ch_dirs = glob.glob(os.path.join(os.path.dirname(__file__), '..', 'data', 'chapters', f'{slug_prefix}*'))
        
        for ch_dir in ch_dirs:
            slug = os.path.basename(ch_dir)
            existing = [f for f in os.listdir(ch_dir) if f.endswith('.json')]
            if len(existing) >= 4:
                continue
            
            # Generate 3 chapters
            new_count = 0
            for i, chapter in enumerate(tpl['chapters']):
                ch_num = 2 + i  # Start from chapter 2 (chapter 1 already exists)
                ch_file = os.path.join(ch_dir, f'chapter-{ch_num:04d}.json')
                if os.path.exists(ch_file):
                    continue
                
                ch_data = {
                    'num': ch_num,
                    'title': chapter['title'],
                    'slug': slug,
                    'lines': chapter['lines']
                }
                with open(ch_file, 'w') as f:
                    json.dump(ch_data, f, ensure_ascii=False, indent=2)
                new_count += 1
            
            if new_count > 0:
                results.append(f'  {slug}: +{new_count}ch ({len(existing) + new_count} total)')
    
    return results

if __name__ == '__main__':
    results = generate_chapters()
    for r in results:
        print(r)
    print(f'\nGenerated chapters for {len(results)} novels')
