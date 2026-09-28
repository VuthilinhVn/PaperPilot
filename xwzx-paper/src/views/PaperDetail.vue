<template>
    <div class="paper-detail">
        <van-nav-bar
            title="论文详情"
            left-text="返回"
            left-arrow
            @click-left="onClickLeft"
            fixed
        />

        <div v-if="papersStore.paperDetail.id != null" class="detail-content">
            <div class="title-container">
                <h1 class="title">{{ papersStore.paperDetail.title }}</h1>
                <van-button
                    class="favorite-btn"
                    :icon="isFavorite ? 'star' : 'star-o'"
                    :class="{ 'is-favorite': isFavorite }"
                    @click="toggleFavorite"
                />
            </div>

            <div class="info">
                <span v-if="papersStore.paperDetail.author">{{
                    papersStore.paperDetail.author
                }}</span>
                <span v-if="papersStore.paperDetail.publishTime">{{
                    papersStore.paperDetail.publishTime
                }}</span>
                <span v-if="categoryLabel">{{ categoryLabel }}</span>
            </div>

            <section class="abstract-section">
                <h2>摘要</h2>
                <p>{{ papersStore.paperDetail.abstract || "暂无摘要" }}</p>
            </section>

            <section class="pdf-section">
                <div class="pdf-heading">
                    <h2>论文 PDF</h2>
                    <a
                        v-if="pdfUrl"
                        :href="pdfUrl"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="open-pdf"
                    >
                        在新窗口打开
                    </a>
                </div>
                <iframe
                    v-if="pdfUrl"
                    class="pdf-viewer"
                    :src="pdfUrl"
                    :title="`${papersStore.paperDetail.title} PDF`"
                />
                <van-empty v-else description="该论文暂未提供可用的 PDF 地址" />
                <a
                    v-if="papersStore.paperDetail.arxivUrl"
                    class="arxiv-link"
                    :href="papersStore.paperDetail.arxivUrl"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    查看 arXiv 页面
                </a>
            </section>
            <section v-if="relatedPapers.length" class="related-section">
                <h2>相关论文</h2>
                <button
                    v-for="paper in relatedPapers"
                    :key="paper.id"
                    type="button"
                    class="related-paper"
                    @click="openRelatedPaper(paper.id)"
                >
                    {{ paper.title }}
                </button>
            </section>
        </div>

        <van-empty
            v-else-if="papersStore.detailLoading"
            description="正在加载论文..."
        />
        <van-empty
            v-else
            :description="papersStore.detailError || '未找到论文'"
        />
    </div>
</template>

<script setup>
import { computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { usePapersStore } from "../store/modules/papers";
import { useHistoryStore } from "../store/modules/history";
import { useFavoriteStore } from "../store/modules/favorite";
import { useUserStore } from "../store/user";
import { apiConfig } from "../config/api";
import { showToast } from "vant";

const route = useRoute();
const router = useRouter();
const papersStore = usePapersStore();
const historyStore = useHistoryStore();
const favoriteStore = useFavoriteStore();
const userStore = useUserStore();

const paperId = computed(() => String(route.params.id || ""));
const isFavorite = computed(() => favoriteStore.isFavorite(paperId.value));
const categoryLabel = computed(() => {
    const detail = papersStore.paperDetail;
    if (detail.categoryName) return detail.categoryName;
    const category = papersStore.categories.find(
        (item) => String(item.id) === String(detail.categoryId),
    );
    return category?.name ?? detail.categoryId;
});
const relatedPapers = computed(() =>
    Array.isArray(papersStore.paperDetail.relatedPapers)
        ? papersStore.paperDetail.relatedPapers
        : [],
);
const pdfUrl = computed(() => {
    const detail = papersStore.paperDetail;
    const storedUrl = detail.pdfUrl;

    if (storedUrl) {
        if (/^https?:\/\//i.test(storedUrl)) return storedUrl;
        if (storedUrl.startsWith("/"))
            return `${apiConfig.baseURL}${storedUrl}`;
    }

    const arxivUrl = detail.arxivUrl;
    if (arxivUrl && /^https?:\/\//i.test(arxivUrl)) {
        if (/\/abs\//.test(arxivUrl)) return arxivUrl.replace("/abs/", "/pdf/");
        if (/\.pdf(?:$|[?#])/i.test(arxivUrl)) return arxivUrl;
    }

    return "";
});

const onClickLeft = () => router.back();
const openRelatedPaper = (id) => {
    if (id != null) router.push(`/paper/detail/${encodeURIComponent(id)}`);
};

const toggleFavorite = async () => {
    if (!userStore.getLoginStatus) {
        showToast({ message: "请先登录后再收藏", position: "bottom" });
        router.push("/login");
        return;
    }

    const status = await favoriteStore.toggleFavorite(papersStore.paperDetail);
    if (status === true) {
        showToast({ message: "已添加到收藏", position: "bottom" });
    } else if (status === false) {
        showToast({ message: "已取消收藏", position: "bottom" });
    } else {
        showToast({ message: "操作失败，请稍后重试", position: "bottom" });
    }
};

watch(
    paperId,
    async (id) => {
        if (!id) return;
        favoriteStore.loadFavorites();
        const paper = await papersStore.getPaperDetail(id);
        if (!paper) return;

        if (userStore.getLoginStatus) {
            const historyResult = await historyStore.addHistoryApi(paper.id);
            if (!historyResult.success) {
                console.error("记录论文浏览历史失败:", historyResult.message);
            }

            const favoriteResult = await favoriteStore.checkFavoriteStatusApi(
                paper.id,
            );
            if (favoriteResult.success && !favoriteResult.isLocal) {
                if (
                    favoriteResult.isFavorite &&
                    !favoriteStore.isFavorite(paper.id)
                ) {
                    favoriteStore.addFavorite(paper);
                } else if (
                    !favoriteResult.isFavorite &&
                    favoriteStore.isFavorite(paper.id)
                ) {
                    favoriteStore.removeFavorite(paper.id);
                }
            }
        }
    },
    { immediate: true },
);
</script>

<style scoped>
.paper-detail {
    padding-top: 46px;
    background-color: #fff;
    min-height: 100vh;
}

.detail-content {
    padding: 16px;
}

.title-container {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 12px;
}

.title {
    font-size: 22px;
    font-weight: bold;
    line-height: 1.4;
    margin: 0;
    flex: 1;
}

.favorite-btn {
    flex-shrink: 0;
    margin-left: 10px;
    padding: 0;
    width: 36px;
    height: 36px;
    border-radius: 50%;
}

.favorite-btn.is-favorite {
    color: #ff9500;
}

.info {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 12px;
    font-size: 12px;
    color: #999;
    margin-bottom: 20px;
}

.abstract-section {
    margin-bottom: 24px;
}

.related-section {
    margin-bottom: 24px;
}

.abstract-section h2,
.related-section h2,
.pdf-heading h2 {
    font-size: 18px;
    margin: 0 0 10px;
}

.related-paper {
    display: block;
    width: 100%;
    padding: 10px 0;
    border: 0;
    border-bottom: 1px solid #eee;
    background: transparent;
    color: #1989fa;
    font: inherit;
    text-align: left;
    cursor: pointer;
}

.abstract-section p {
    font-size: 15px;
    line-height: 1.8;
    color: #444;
    white-space: pre-line;
}

.pdf-section {
    padding-top: 18px;
    border-top: 1px solid #eee;
}

.pdf-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.open-pdf,
.arxiv-link {
    color: #1989fa;
    font-size: 14px;
    text-decoration: none;
}

.pdf-viewer {
    width: 100%;
    height: min(78vh, 1000px);
    min-height: 600px;
    border: 1px solid #e5e5e5;
    border-radius: 4px;
}

.arxiv-link {
    display: inline-block;
    margin-top: 12px;
}

@media screen and (max-width: 600px) {
    .pdf-viewer {
        height: 70vh;
        min-height: 480px;
    }
}
</style>
