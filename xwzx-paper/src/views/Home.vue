<template>
  <div class="home">
    <van-nav-bar :title="$t('home.title')" fixed />

    <div class="more-options">
      <div class="more-tab" @click="goToCategory">
        {{ $t('home.more') }} <van-icon name="arrow" />
      </div>
    </div>

    <div class="category-tabs">
      <van-tabs v-model:active="activeTab" sticky swipeable animated>
        <van-tab
          v-for="category in displayCategories"
          :key="category.id"
          :title="getCategoryTranslation(category.name)"
        >
          <van-pull-refresh v-model="papersStore.refreshing" @refresh="onRefresh">
            <van-list
              v-model:loading="papersStore.loading"
              :finished="papersStore.finished"
              :finished-text="$t('home.noMore')"
              @load="onLoad"
            >
              <paper-item
                v-for="paper in papersStore.paperList"
                :key="paper.id"
                :paper="paper"
              />
              <van-empty
                v-if="!papersStore.loading && !papersStore.paperList.length"
                :description="papersStore.listError || $t('home.empty')"
              />
            </van-list>
          </van-pull-refresh>
        </van-tab>
      </van-tabs>
    </div>

    <tab-bar />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { usePapersStore } from '../store/modules/papers'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import PaperItem from '../components/PaperItem.vue'
import TabBar from '../components/TabBar.vue'
import { getPaperCategoryTranslation } from '../utils/paperCategories'

const papersStore = usePapersStore()
const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const activeTab = ref(0)
const tabsTop = ref(0)

const displayCategories = computed(() => papersStore.categories)

const getCategoryTranslation = (name) => getPaperCategoryTranslation(name, t)

const goToCategory = () => {
  router.push('/category')
}

const updateTabsPosition = () => {
  const tabsElement = document.querySelector('.van-tabs__wrap')
  if (tabsElement) tabsTop.value = tabsElement.getBoundingClientRect().top
}

const handleScroll = () => updateTabsPosition()
const onRefresh = () => papersStore.getPaperList(true)
const onLoad = () => papersStore.getPaperList()

watch(activeTab, (index) => {
  const category = displayCategories.value[index]
  if (category && category.id !== papersStore.currentCategory) {
    papersStore.changeCategory(category.id)
  }
})

watch(
  () => route.query.categoryId,
  (categoryId) => {
    if (categoryId == null) return
    const index = displayCategories.value.findIndex(
      (category) => String(category.id) === String(categoryId)
    )
    if (index !== -1) activeTab.value = index
  }
)

onMounted(async () => {
  await papersStore.getCategories()
  if (displayCategories.value.length) {
    const requestedId = route.query.categoryId
    const requestedIndex = displayCategories.value.findIndex(
      (category) => String(category.id) === String(requestedId)
    )
    activeTab.value = requestedIndex === -1 ? 0 : requestedIndex
    const category = displayCategories.value[activeTab.value]
    await papersStore.changeCategory(category.id)
  } else {
    await papersStore.getPaperList(true)
  }

  setTimeout(updateTabsPosition, 300)
  window.addEventListener('scroll', handleScroll)
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.home {
  padding-top: 46px;
  padding-bottom: 50px;
  background-color: #f7f8fa;
  min-height: 100vh;
}

.category-tabs {
  margin-bottom: 10px;
  position: relative;
}

:deep(.van-tabs__wrap) {
  background-color: #fff;
}

:deep(.van-tab) {
  font-size: 14px;
}

:deep(.van-tab--active) {
  font-weight: bold;
  color: #1989fa;
}

.more-options {
  position: fixed;
  right: 0;
  background-color: #fff;
  padding: 0;
  border-radius: 4px 0 0 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  top: v-bind('tabsTop + "px"');
  height: 44px;
  display: flex;
  align-items: center;
}

.more-tab {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #1989fa;
  font-weight: bold;
  height: 100%;
  padding: 0 10px;
}
</style>
