import fs from 'fs';
import path from 'path';

// ========== 类型定义 ==========
export interface Novel {
  id: number;
  slug: string;
  title_en: string;
  author_en: string;
  author_zh?: string;
  genre: string;
  tags: string[];
  is_adult: boolean;
  status: string;
  rating: number;
  total_chapters: number;
  available_chapters?: number;
  readers: number;
  description_en: string;
  cover_url: string;
  source_url: string;
  source_site: string;
  zone: string;
  created_at: string;
  updated_at: string;
}

export interface Chapter {
  num: number;
  title_en: string;
  content_en: string;
  translated: boolean;
}

// ========== 数据目录 ==========
const DATA_DIR = path.join(process.cwd(), 'data');
const NOVELS_FILE = path.join(DATA_DIR, 'novels.json');
const CHAPTERS_DIR = path.join(DATA_DIR, 'chapters');

const PUBLIC_DIR = path.join(process.cwd(), 'public');

export function getCoverUrl(slug: string): string {
  const jpgPath = path.join(PUBLIC_DIR, 'covers', `${slug}.jpg`);
  const svgPath = path.join(PUBLIC_DIR, 'covers', `${slug}.svg`);
  const pngPath = path.join(PUBLIC_DIR, 'covers', `${slug}.png`);
  if (fs.existsSync(jpgPath)) return `/covers/${slug}.jpg`;
  if (fs.existsSync(svgPath)) return `/covers/${slug}.svg`;
  if (fs.existsSync(pngPath)) return `/covers/${slug}.png`;
  // generated SVG fallback
  const genSvg = path.join(PUBLIC_DIR, 'covers', `${slug}-gen.svg`);
  if (fs.existsSync(genSvg)) return `/covers/${slug}-gen.svg`;
  return `/covers/default.svg`; // absolute fallback
}

// ========== 工具函数 ==========
function readJsonFile<T>(filePath: string): T | null {
  try {
    if (!fs.existsSync(filePath)) {
      return null;
    }
    const content = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(content) as T;
  } catch (error) {
    console.error(`Error reading ${filePath}:`, error);
    return null;
  }
}

// ========== Novel 数据访问 ==========
export function getAllNovels(): Novel[] {
  const data = readJsonFile<Novel[]>(NOVELS_FILE);
  return data || [];
}

export function getNovelBySlug(slug: string): Novel | null {
  const novels = getAllNovels();
  return novels.find((n) => n.slug === slug) || null;
}

export function getFeaturedNovels(limit: number = 8): Novel[] {
  const novels = getAllNovels();
  // 按评分排序，排除成人内容（除非显式要求）
  return novels
    .filter((n) => !n.is_adult)
    .sort((a, b) => b.rating - a.rating)
    .slice(0, limit);
}

export function getNovelsByGenre(genre: string, includeAdult: boolean = false): Novel[] {
  let novels = getAllNovels();
  
  if (!includeAdult) {
    novels = novels.filter((n) => !n.is_adult);
  }
  
  if (genre && genre!== 'all') {
    novels = novels.filter((n) => n.genre === genre);
  }
  
  return novels.sort((a, b) => b.rating - a.rating);
}

export function searchNovels(query: string): Novel[] {
  const novels = getAllNovels();
  const lowerQuery = query.toLowerCase();
  
  return novels.filter(
    (n) =>
      n.title_en.toLowerCase().includes(lowerQuery) ||
      n.author_en.toLowerCase().includes(lowerQuery) ||
      n.tags.some((tag) => tag.toLowerCase().includes(lowerQuery))
  );
}

export function getFreeNovels(): Novel[] {
  return getAllNovels().filter((n) => n.zone === 'free');
}

export function getVipNovels(): Novel[] {
  return getAllNovels().filter((n) => n.zone === 'vip');
}

export function getGenres(): { name: string; count: number; is_adult: boolean }[] {
  const novels = getAllNovels();
  const genreMap = new Map<string, { count: number; is_adult: boolean }>();
  
  novels.forEach((novel) => {
    const existing = genreMap.get(novel.genre);
    if (existing) {
      existing.count++;
    } else {
      genreMap.set(novel.genre, { count: 1, is_adult: novel.is_adult });
    }
  });
  
  return Array.from(genreMap.entries()).map(([name, data]) => ({
    name,
    count: data.count,
    is_adult: data.is_adult,
  }));
}

// ========== Chapter 数据访问 ==========
// ── Chapter helpers (supports both old ch-N.json and new chapter-N.json) ──
function findChapterFile(novelDir: string, chapterNum: number): string | null {
  // Try: ch-1.json, ch-0001.json, chapter-1.json, chapter-0001.json
  const variants = [
    `${chapterNum}`,                        // 1
    `${String(chapterNum).padStart(3, '0')}`,  // 001
    `${String(chapterNum).padStart(4, '0')}`,  // 0001
    `${String(chapterNum).padStart(5, '0')}`,  // 00001
  ];
  const prefixes = ['ch-', 'chapter-'];
  for (const prefix of prefixes) {
    for (const variant of variants) {
      const name = `${prefix}${variant}.json`;
      const p = path.join(novelDir, name);
      if (fs.existsSync(p)) return name;
    }
  }
  // Fallback: scan directory for any matching file
  if (fs.existsSync(novelDir)) {
    const files = fs.readdirSync(novelDir)
      .filter(f => f.endsWith('.json') && (f.startsWith('ch-') || f.startsWith('chapter-')));
    for (const f of files) {
      try {
        const raw = JSON.parse(fs.readFileSync(path.join(novelDir, f), 'utf-8'));
        const num = raw.num || raw.chapter_number;
        if (num === chapterNum) return f;
      } catch { /* skip malformed */ }
    }
  }
  return null;
}

function listChapterFiles(novelDir: string): string[] {
  if (!fs.existsSync(novelDir)) return [];
  return fs.readdirSync(novelDir).filter(
    (f) => (f.startsWith('ch-') || f.startsWith('chapter-')) && f.endsWith('.json')
  );
}

// Reads JSON that may have 'title' (crawler) or 'title_en' (legacy)
function readChapterRaw(filePath: string): Record<string, any> | null {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch {
    return null;
  }
}

function readChapterSafe(filePath: string): Chapter | null {
  const raw = readChapterRaw(filePath);
  if (!raw) return null;
  return {
    num: raw.num || 0,
    title_en: raw.title_en || raw.title || '',
    content_en: raw.content_en || raw.content_zh || raw.content || '',
    translated: raw.translated ?? true,
  };
}

export function getChapter(novelSlug: string, chapterNum: number): Chapter | null {
  const novelDir = path.join(CHAPTERS_DIR, novelSlug);
  const fileName = findChapterFile(novelDir, chapterNum);
  if (!fileName) return null;
  return readChapterSafe(path.join(novelDir, fileName));
}

/** Returns REAL chapters only (no placeholders) */
export function getChapterList(novelSlug: string): { num: number; title_en: string }[] {
  const novelDir = path.join(CHAPTERS_DIR, novelSlug);
  const files = listChapterFiles(novelDir);
  const result: { num: number; title_en: string }[] = [];
  
  for (const file of files) {
    const chapter = readChapterSafe(path.join(novelDir, file));
    if (chapter && chapter.num > 0) {
      // Only include chapters with valid English content
      if (isValidEnglish(chapter.content_en)) {
        result.push({ num: chapter.num, title_en: chapter.title_en || `Chapter ${chapter.num}` });
      }
    }
  }
  
  return result.sort((a, b) => a.num - b.num);
}

/** Check if a novel has valid English translations for ALL its chapters */
export function isNovelFullyTranslated(slug: string): boolean {
  const novelDir = path.join(CHAPTERS_DIR, slug);
  if (!fs.existsSync(novelDir)) return false;
  
  const files = fs.readdirSync(novelDir).filter(
    (f) => (f.startsWith('ch-') || f.startsWith('chapter-')) && f.endsWith('.json')
  );
  
  if (files.length === 0) return false;
  
  for (const file of files) {
    const raw = readChapterRaw(path.join(novelDir, file));
    if (!raw) return false;
    if (!isValidEnglish(raw.content_en)) return false;
  }
  
  return true;
}

/** Returns only placeholder chapters for novels with no actual files */
export function getChapterListFallback(novelSlug: string, max = 50): { num: number; title_en: string }[] {
  const real = getChapterList(novelSlug);
  if (real.length > 0) return real;
  
  const novel = getNovelBySlug(novelSlug);
  if (!novel) return [];
  const count = Math.min(novel.total_chapters, max);
  return Array.from({ length: count }, (_, i) => ({
    num: i + 1,
    title_en: `Chapter ${i + 1}`,
  }));
}

// Check if text is mostly CJK (Chinese/Japanese/Korean) characters
function isMostlyCJK(text: string): boolean {
  if (!text || text.length < 30) return false;
  const sample = text.slice(0, 1000);
  const total = sample.length;
  let cjk = 0;
  for (let i = 0; i < total; i++) {
    const c = sample.charCodeAt(i);
    // CJK Unified Ideographs + CJK Extension A
    if ((c >= 0x4E00 && c <= 0x9FFF) || (c >= 0x3400 && c <= 0x4DBF)) cjk++;
  }
  return cjk / total > 0.15; // >15% CJK = Chinese content
}

// Check if content looks like valid English (not Chinese, not garbled)
function isValidEnglish(text: string): boolean {
  if (!text || typeof text !== 'string' || text.length < 50) return false;
  return !isMostlyCJK(text);
}

export function getChapterContent(novelSlug: string, chapterNum: number): string {
  const novelDir = path.join(CHAPTERS_DIR, novelSlug);
  const fileName = findChapterFile(novelDir, chapterNum);
  
  if (!fileName) {
    return `Chapter ${chapterNum}\n\nThis chapter is being translated. Please check back soon!`;
  }
  
  const raw = readChapterRaw(path.join(novelDir, fileName));
  if (!raw) return 'Content not available.';
  
  // 1. Try content_en — must be actual English (not Chinese)
  if (raw.content_en && typeof raw.content_en === 'string' && isValidEnglish(raw.content_en)) {
    return raw.content_en;
  }
  
  // 2. content_en exists but is Chinese → this chapter was never translated
  if (raw.content_en && typeof raw.content_en === 'string' && isMostlyCJK(raw.content_en)) {
    return `Chapter ${chapterNum}\n\nThis chapter is being translated. Please check back soon!`;
  }
  
  // 3. No content_en → show being-translated message
  return `Chapter ${chapterNum}\n\nThis chapter is being translated. Please check back soon!`;
}
