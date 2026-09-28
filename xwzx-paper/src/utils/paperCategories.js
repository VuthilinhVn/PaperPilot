export const PAPER_CATEGORY_DEFINITIONS = [
  { code: 'cs.CV', name: 'Computer Vision', key: 'computerVision' },
  { code: 'cs.LG', name: 'Machine Learning', key: 'machineLearning' },
  { code: 'cs.CL', name: 'Computation and Language (NLP)', key: 'language' },
  { code: 'cs.AI', name: 'Artificial Intelligence', key: 'artificialIntelligence' },
  { code: 'cs.RO', name: 'Robotics', key: 'robotics' },
  { code: 'cs.IR', name: 'Information Retrieval', key: 'informationRetrieval' },
  { code: 'cs.NE', name: 'Neural and Evolutionary Computing', key: 'neuralComputing' }
]

const categoryByAlias = new Map(
  PAPER_CATEGORY_DEFINITIONS.flatMap((category) => [
    [category.code, category],
    [category.name, category]
  ])
)

export const getPaperCategoryName = (name) => {
  return categoryByAlias.get(name)?.name ?? name
}

export const getPaperCategoryTranslation = (name, translate) => {
  const category = categoryByAlias.get(name)
  return category ? translate(`home.categories.${category.key}`) : name
}

export const normalizePaperCategories = (categories) => {
  const apiCategories = Array.isArray(categories) ? categories : []

  return apiCategories.map((category) => {
    const categoryName = category.name ?? category.category_name ?? category.title
    const definition = categoryByAlias.get(categoryName)
    const code = category.code ?? category.category_code ?? definition?.code

    return {
      ...category,
      id: category.id ?? category.category_id ?? code ?? categoryName,
      code,
      name: definition?.name ?? categoryName
    }
  })
}

export const getDefaultPaperCategories = () => {
  return PAPER_CATEGORY_DEFINITIONS.map((category) => ({
    ...category,
    id: category.code
  }))
}
