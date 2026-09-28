import { defineStore } from 'pinia'
import axios from 'axios'
import { apiConfig } from '../../config/api'
import { normalizePaper } from '../../utils/papers'
import {
  getDefaultPaperCategories,
  normalizePaperCategories
} from '../../utils/paperCategories'

const responseList = (data) => {
  if (Array.isArray(data)) return data
  return Array.isArray(data?.list) ? data.list : []
}

export const usePapersStore = defineStore('papers', {
  state: () => ({
    paperList: [],
    paperDetail: {},
    categories: [],
    currentCategory: null,
    loading: false,
    refreshing: false,
    finished: false,
    listError: '',
    categoriesLoading: false,
    detailLoading: false,
    detailError: ''
  }),

  actions: {
    async getCategories() {
      if (this.categoriesLoading) return
      this.categoriesLoading = true

      try {
        const response = await axios.get(`${apiConfig.baseURL}/api/papers/categories`)
        if (response.data?.code === 200) {
          this.categories = normalizePaperCategories(responseList(response.data.data))
          if (this.currentCategory == null && this.categories.length) {
            this.currentCategory = this.categories[0].id
          }
        } else {
          throw new Error(response.data?.msg || response.data?.message || '获取论文分类失败')
        }
      } catch (error) {
        console.error('获取论文分类失败:', error)
        this.categories = getDefaultPaperCategories()
      } finally {
        this.categoriesLoading = false
      }
    },

    async changeCategory(categoryId) {
      if (this.currentCategory === categoryId && this.paperList.length) return
      this.currentCategory = categoryId
      this.paperList = []
      this.finished = false
      await this.getPaperList(true)
    },

    async getPaperList(isRefresh = false) {
      if (this.loading && !isRefresh) return
      if (isRefresh) {
        this.refreshing = true
        this.paperList = []
        this.finished = false
      }

      this.loading = true
      this.listError = ''
      const pageSize = 10

      try {
        const category = this.categories.find(
          (item) => String(item.id) === String(this.currentCategory)
        )
        const categoryId = Number(this.currentCategory)
        const params = {
          page: isRefresh ? 1 : Math.floor(this.paperList.length / pageSize) + 1,
          pageSize
        }

        if (category && Number.isInteger(categoryId)) {
          params.categoryId = categoryId
        } else if (category?.code) {
          params.categoryCode = category.code
        }

        const response = await axios.get(`${apiConfig.baseURL}/api/papers/list`, { params })
        if (response.data?.code !== 200) {
          throw new Error(response.data?.msg || response.data?.message || '获取论文列表失败')
        }

        const papers = responseList(response.data.data).map(normalizePaper)
        this.paperList = isRefresh ? papers : [...this.paperList, ...papers]
        this.finished = papers.length < pageSize
      } catch (error) {
        console.error('获取论文列表失败:', error)
        this.listError = error.message || '获取论文列表失败'
        this.finished = true
      } finally {
        this.loading = false
        this.refreshing = false
      }
    },

    async getPaperDetail(id) {
      this.paperDetail = {}
      this.detailError = ''
      this.detailLoading = true

      try {
        const response = await axios.get(`${apiConfig.baseURL}/api/papers/detail`, {
          params: { id }
        })
        if (response.data?.code !== 200 || !response.data.data) {
          throw new Error(response.data?.msg || response.data?.message || '获取论文详情失败')
        }

        this.paperDetail = normalizePaper(response.data.data)
        return this.paperDetail
      } catch (error) {
        this.detailError = error.message || '获取论文详情失败'
        console.error('获取论文详情失败:', error)
        return null
      } finally {
        this.detailLoading = false
      }
    }
  }
})
