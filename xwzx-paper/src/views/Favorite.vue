<template>
  <div class="favorite-container">
    <van-nav-bar
      title="我的收藏"
      left-text="返回"
      left-arrow
      @click-left="onClickLeft"
      right-text="清空"
      @click-right="onClickClear"
      fixed
    />
    
    <div class="favorite-list" v-if="favoriteStore.getFavorites.length">
      <div class="favorite-item" v-for="item in favoriteStore.getFavorites" :key="item.id">
        <van-cell @click="goToPaperDetail(item.id)" :border="false">
          <template #title>
            <div class="paper-item">
              <div class="paper-icon">
                <van-icon name="description" />
              </div>
              <div class="paper-info">
                <div class="paper-title">{{ item.title }}</div>
                <div class="paper-meta">
                  <span>{{ item.author }}</span>
                  <span>{{ item.publishTime }}</span>
                  <span>收藏时间: {{ item.favoriteTime }}</span>
                </div>
              </div>
            </div>
          </template>
        </van-cell>
        <van-button 
          class="delete-btn" 
          type="danger" 
          size="mini" 
          icon="cross"
          @click="confirmDelete(item.id)"
        ></van-button>
      </div>
    </div>
    
    <van-empty v-else description="暂无收藏内容" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useFavoriteStore } from '../store/modules/favorite';
import { showDialog } from 'vant';

const router = useRouter();
const favoriteStore = useFavoriteStore();

// 返回上一页
const onClickLeft = () => {
  router.back();
};

// 跳转到论文详情
const goToPaperDetail = (id) => {
  router.push(`/paper/detail/${encodeURIComponent(id)}`);
};

// 删除单条收藏
const removeFavorite = async (id) => {
  const result = await favoriteStore.removeFavoriteApi(id);
  if (result.success) {
    // API请求成功后，更新本地收藏列表
    favoriteStore.removeFavorite(id);
  }
};

// 确认删除
const confirmDelete = (id) => {
  showDialog({
    title: '提示',
    message: '确定要删除这条收藏吗？',
    showCancelButton: true,
  }).then((action) => {
    if (action === 'confirm') {
      removeFavorite(id);
    }
  });
};

// 清空收藏
const onClickClear = async () => {
  showDialog({
    title: '提示',
    message: '确定要清空所有收藏吗？',
    showCancelButton: true,
  }).then(async (action) => {
    if (action === 'confirm') {
      const result = await favoriteStore.clearFavoritesApi();
      if (!result || !result.success) {
        // 如果API请求失败，回退到本地清空
        // favoriteStore.clearFavorites();
        console.log('清空收藏列表');
      }
    }
  });
};

// 组件挂载时加载收藏数据
onMounted(async () => {
  // 使用API请求获取收藏列表
  try {

    const result = await favoriteStore.getFavoriteListApi();
    if (!result || !result.success) {
      favoriteStore.loadFavorites();
    }
  } catch (error) {
    favoriteStore.loadFavorites();
  }
});
</script>

<style scoped>
.favorite-container {
  padding-top: 46px;
  padding-bottom: 20px;
  background-color: #f7f8fa;
  min-height: 100vh;
}

.favorite-list {
  padding: 10px;
}

.paper-item {
  display: flex;
  padding: 10px 0;
}

.paper-icon {
  width: 48px;
  height: 56px;
  margin-right: 12px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  color: #d93025;
  background: #fff3f2;
  font-size: 26px;
}

.paper-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.paper-title {
  font-size: 16px;
  font-weight: bold;
  line-height: 1.4;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.paper-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  flex-wrap: wrap;
}

.paper-meta span {
  margin-right: 10px;
}

.favorite-item {
  position: relative;
  margin-bottom: 10px;
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.delete-btn {
  position: absolute;
  top: 50%;
  right: 10px;
  transform: translateY(-50%);
  z-index: 10;
  width: 24px;
  height: 24px;
  padding: 0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>