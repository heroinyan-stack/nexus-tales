import fs from 'fs';
import path from 'path';

// ========== 类型定义 ==========
export interface Novel {
  id: number;
  slug: string;
  title_zh: string;
  title_en: string;
  author_zh: string;
  author_en: string;
  genre: string;
  tags: string[];
  is_adult: boolean;
  status: string;
  rating: number;
  total_chapters: number;
  readers: number;
  description_zh: string;
  description_en: string;
  cover_url: string;
  source_url: string;
  source_site: string;
  created_at: string;
  updated_at: string;
}

export interface Chapter {
  num: number;
  title_zh: string;
  title_en: string;
  content_zh: string;
  content_en: string;
  translated: boolean;
}

// ========== 数据目录 ==========
const DATA_DIR = path.join(process.cwd(), 'data');
const NOVELS_FILE = path.join(DATA_DIR, 'novels.json');
const CHAPTERS_DIR = path.join(DATA_DIR, 'chapters');

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
      n.title_zh.toLowerCase().includes(lowerQuery) ||
      n.author_en.toLowerCase().includes(lowerQuery) ||
      n.author_zh.toLowerCase().includes(lowerQuery) ||
      n.tags.some((tag) => tag.toLowerCase().includes(lowerQuery))
  );
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
export function getChapter(novelSlug: string, chapterNum: number): Chapter | null {
  const chapterPath = path.join(CHAPTERS_DIR, novelSlug, `ch-${chapterNum}.json`);
  return readJsonFile<Chapter>(chapterPath);
}

export function getChapterList(novelSlug: string): { num: number; title_en: string; title_zh: string }[] {
  const novelDir = path.join(CHAPTERS_DIR, novelSlug);
  
  if (!fs.existsSync(novelDir)) {
    // 返回模拟章节列表
    const novel = getNovelBySlug(novelSlug);
    if (!novel) return [];
    
    return Array.from({ length: Math.min(novel.total_chapters, 50) }, (_, i) => ({
      num: i + 1,
      title_en: `Chapter ${i + 1}`,
      title_zh: `第${i + 1}章`,
    }));
  }
  
  const files = fs.readdirSync(novelDir).filter((f) => f.startsWith('ch-') && f.endsWith('.json'));
  
  const result: { num: number; title_en: string; title_zh: string }[] = [];
  
  for (const file of files) {
    const chapter = readJsonFile<Chapter>(path.join(novelDir, file));
    if (chapter) {
      result.push({ num: chapter.num, title_en: chapter.title_en, title_zh: chapter.title_zh });
    }
  }
  
  return result.sort((a, b) => a.num - b.num);
}

export function getChapterContent(novelSlug: string, chapterNum: number): string {
  const chapter = getChapter(novelSlug, chapterNum);
  
  if (!chapter) {
    // 返回模拟内容
    return `Chapter ${chapterNum}\n\nThis chapter is being translated. Please check back soon!\n\n（本章正在翻译中，请稍后再来！）`;
  }
  
  // 返回英文内容，如果没有就用中文
  return chapter.content_en || chapter.content_zh || 'Content not available.';
}
