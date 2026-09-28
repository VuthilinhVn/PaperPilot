<template>
  <div class="category">
    <van-nav-bar
      :title="$t('common.allCategories')"
      :left-text="$t('common.back')"
      left-arrow
      @click-left="onClickLeft"
      fixed
    />

    <div class="category-container">
      <van-grid :column-num="3" :border="false">
        <van-grid-item
          v-for="category in papersStore.categories"
          :key="category.id"
          :text="getCategoryName(category)"
          icon="description"
          @click="goToCategoryPapers(category.id)"
        />
      </van-grid>
    </div>

    <tab-bar />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { usePapersStore } from '../store/modules/papers'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import TabBar from '../components/TabBar.vue'
import { getPaperCategoryTranslation } from '../utils/paperCategories'

const papersStore = usePapersStore()
const router = useRouter()
const { t } = useI18n()

const getCategoryName = (category) => getPaperCategoryTranslation(category.name, t)

const onClickLeft = () => router.back()

const goToCategoryPapers = (categoryId) => {
  papersStore.changeCategory(categoryId)
  router.push({
    path: '/home',
    query: { categoryId }
  })
}

onMounted(() => {
  papersStore.getCategories()
})
</script>

<style scoped>
.category {
  padding-top: 46px;
  padding-bottom: 50px;
  background-color: #f7f8fa;
  min-height: 100vh;
}

.category-container {
  padding: 16px;
  background-color: #fff;
  margin-top: 12px;
  border-radius: 8px;
}

:deep(.van-grid-item__content) {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 20px 0;
}

:deep(.van-grid-item__icon) {
  font-size: 28px;
  color: #1989fa;
}

:deep(.van-grid-item__text) {
  margin-top: 8px;
  color: #333;
  font-size: 14px;
}
</style>
