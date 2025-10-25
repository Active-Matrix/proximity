import { z } from 'zod';

export const summerizedNewsSchema = z.object({
  title: z.string(),
  content: z.string(),
  imageUrl: z.string(),
  date: z.string(),
  scrapedAt: z.string(),
  sourceName: z.string(),
  sourceUrl: z.string(),
  tags: z.array(z.string()),
})

export const generatedNewsSchema = z.object({
  title: z.string(),
  content: z.string(),
  tags: z.array(z.string()),
})

export const scrapedNewsSchema = z.object({
  title: z.string().min(1),
  content: z.string().min(1),
  imageUrl: z.string().url(),
  date: z.string().datetime(),
  scrapedAt: z.string().datetime(),
  sourceName: z.string().min(1),
  sourceUrl: z.string()
})
