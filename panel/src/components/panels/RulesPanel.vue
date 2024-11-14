<template>
  <div class="rules-panel">
    <img :src="rulesImages[currentImageIndex]" alt="Rules" class="rules-image" />
    <div class="navigation-buttons">
      <n-button type="primary" @click="prevImage" :disabled="currentImageIndex === 0">上一页</n-button>
      <span class="page-indicator">{{ currentImageIndex + 1 }} / {{ rulesImages.length }}</span>
      <n-button type="primary" @click="nextImage" :disabled="currentImageIndex === rulesImages.length - 1">下一页</n-button>
      <n-button type="error" @click="closeRulesPanel">关闭</n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { defineProps } from 'vue';
import { NButton } from 'naive-ui';

const props = defineProps<{
  closeRulesPanel: () => void;
}>();

const rulesImages = [
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_1.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_2.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_3.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_4.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_5.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_6.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_7.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_8.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_9.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_10.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_11.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_12.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_13.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_14.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_15.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_16.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_17.webp',
  'https://raw.githubusercontent.com/SmokeyDays/SiderealConfluenceWeb/refs/heads/main/other_assets/rules/rule_zh_18.webp',
];

const currentImageIndex = ref(0);

const prevImage = () => {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--;
  }
};

const nextImage = () => {
  if (currentImageIndex.value < rulesImages.length - 1) {
    currentImageIndex.value++;
  }
};
</script>

<style scoped>
.rules-panel {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: white;
  padding: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  text-align: center;
  z-index: 1000;
  max-width: 80%;
}

.rules-image {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
  margin-bottom: 10px;
}

.navigation-buttons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin: 10px 0;
}

.page-indicator {
  font-weight: bold;
}
</style>