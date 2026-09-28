<template>
  <div class="paper-item" @click="goToDetail">
    <div class="paper-content">
      <h3 class="paper-title">{{ paper.title }}</h3>
      <p class="paper-abstract">{{ paper.abstract }}</p>
      <div class="paper-info">
        <span v-if="paper.author">{{ paper.author }}</span>
        <span v-if="paper.publishTime">{{ paper.publishTime }}</span>
        <span v-if="paper.categoryName">{{ paper.categoryName }}</span>
      </div>
    </div>
    <div class="pdf-badge" aria-label="PDF">
      <van-icon name="description" />
      <span>PDF</span>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  paper: {
    type: Object,
    required: true
  }
})

const router = useRouter()

const goToDetail = () => {
  router.push(`/paper/detail/${encodeURIComponent(props.paper.id)}`)
}
</script>

<style scoped>
.paper-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid #f2f2f2;
  background-color: #fff;
  cursor: pointer;
}

.paper-content {
  flex: 1;
  min-width: 0;
  margin-right: 12px;
}

.paper-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.paper-abstract {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.paper-info {
  font-size: 12px;
  color: #999;
  display: flex;
  flex-wrap: wrap;
  gap: 4px 10px;
}

.pdf-badge {
  width: 58px;
  height: 68px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  border-radius: 6px;
  color: #d93025;
  background: #fff3f2;
  font-size: 12px;
  font-weight: 600;
}

.pdf-badge :deep(.van-icon) {
  font-size: 24px;
}
</style>
