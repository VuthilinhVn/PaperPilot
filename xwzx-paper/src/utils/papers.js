import { getPaperCategoryName } from './paperCategories'

export const normalizePaper = (paper) => ({
  ...paper,
  id: paper.id,
  abstract: paper.abstract ?? paper.description ?? '',
  author: paper.first_author ?? paper.firstAuthor ?? paper.author ?? '',
  publishTime: paper.submitted_at ?? paper.submitted_date ?? paper.publishTime ?? '',
  categoryId: paper.categoryId ?? paper.category_id,
  categoryName: getPaperCategoryName(
    paper.category_name ?? paper.categoryName ?? paper.primary_category ?? ''
  ),
  pdfUrl: paper.pdf_url ?? paper.pdfUrl ?? '',
  arxivUrl: paper.arxiv_url ?? paper.arxivUrl ?? '',
  relatedPapers: paper.relatedPapers ?? paper.related_papers ?? paper.relatedNews ?? [],
  views: paper.views ?? paper.view_count ?? 0,
  favoriteTime: paper.favoriteTime ?? paper.favorite_time,
  viewTime: paper.viewTime ?? paper.view_time
})
