<template>
  <PanelTemplate>
    <n-card class="history-panel" :bordered="false" role="dialog" aria-modal="true">
      <template #header>
        <div class="panel-header-row">
          <span class="panel-title">历史回复记录</span>
          
          <div class="header-actions">
            <n-button-group size="small" style="margin-right: 16px;">
              <n-button secondary type="primary" @click="handleExpandAll">
                <template #icon><n-icon><IconExpand /></n-icon></template>
                展开全部
              </n-button>
              <n-button secondary @click="handleCollapseAll">
                <template #icon><n-icon><IconCollapse /></n-icon></template>
                折叠全部
              </n-button>
            </n-button-group>

            <n-button text @click="props.closePanel" style="font-size: 20px;">
              <n-icon><IconClose /></n-icon>
            </n-button>
          </div>
        </div>
      </template>

      <div class="history-list">
        <n-empty v-if="sortedHistory.length === 0" description="暂无历史记录" />
        
        <n-card 
          v-for="item in sortedHistory" 
          :key="item.timestamp" 
          size="small" 
          class="history-item"
        >
          <template #header>
            <div class="item-header">
              <n-tag type="success" size="small" round bordered>
                Round {{ item.round }}
              </n-tag>
              <n-tag type="warning" size="small" round bordered>
                {{ item.stage }}
              </n-tag>
              <span class="time-label">{{ formatTime(item.timestamp) }}</span>
            </div>
          </template>

          <n-collapse 
            :expanded-names="expandedMap[item.timestamp] || []"
            @update:expanded-names="(names) => handleItemToggle(item.timestamp, names)"
          >
            
            <n-collapse-item title="Agent Response" name="response">
              <template #header-extra>
                <span class="word-count">{{ item.response.length }} chars</span>
              </template>
              <div class="text-block response-block">{{ item.response }}</div>
            </n-collapse-item>

            <n-collapse-item title="Prompt Context Snapshot" name="prompt">
              <div class="prompt-container">
                <div 
                  v-for="(content, section) in item.prompt" 
                  :key="section" 
                  class="prompt-section"
                  :style="getSectionStyle(section as string)"
                >
                  <div class="section-title" :style="{ color: getSectionColor(section as string) }">
                    {{ section }}
                  </div>
                  <div class="section-content">{{ content }}</div>
                </div>
              </div>
            </n-collapse-item>

          </n-collapse>
        </n-card>
      </div>

      <template #action>
        <div class="panel-footer">
          <n-button @click="props.closePanel">关闭</n-button>
        </div>
      </template>
    </n-card>
  </PanelTemplate>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { NCard, NButton, NIcon, NCollapse, NCollapseItem, NEmpty, NTag, NButtonGroup } from 'naive-ui';
import IconClose from "@/components/icons/IconClose.vue";
import IconCollapse from '../icons/IconCollapse.vue';
import IconExpand from '../icons/IconExpand.vue';
import PanelTemplate from '@/components/panels/PanelTemplate.vue';
import type { ResponseItem } from '@/interfaces/GameState';

const props = defineProps<{
  closePanel: () => void;
  username: string;
  history: ResponseItem[];
}>();

// --- 状态管理 ---

// 存储每个 item 的展开状态。Key: timestamp, Value: string[] (['response', 'prompt'] etc)
const expandedMap = ref<Record<string, string[]>>({});

const sortedHistory = computed(() => {
  return [...props.history].sort((a, b) => Number(b.timestamp) - Number(a.timestamp));
});

// 监听数据变化，初始化展开状态
watch(() => props.history, (newVal) => {
  newVal.forEach(item => {
    // 如果这个 item 还没有记录状态，默认展开 'response'
    if (!expandedMap.value[item.timestamp]) {
      expandedMap.value[item.timestamp] = ['response'];
    }
  });
}, { immediate: true, deep: true });

// --- 事件处理 ---

// 单个 Item 切换
const handleItemToggle = (timestamp: string | number, names: string[]) => {
  expandedMap.value[timestamp] = names;
};

// 展开全部：显示 Response 和 Prompt
const handleExpandAll = () => {
  sortedHistory.value.forEach(item => {
    expandedMap.value[item.timestamp] = ['response', 'prompt'];
  });
};

// 折叠全部：全部关闭
const handleCollapseAll = () => {
  sortedHistory.value.forEach(item => {
    expandedMap.value[item.timestamp] = [];
  });
};

// --- 工具函数 (保持不变) ---

const formatTime = (ts: string | number) => {
  const date = new Date(Number(ts) * 1000); 
  if (isNaN(date.getTime())) return ts; 
  return date.toLocaleString('zh-CN', { hour12: false });
};

const colorPalette = [
  '#2080f0', '#f0a020', '#18a058', '#d03050', 
  '#8a2be2', '#2080f0', '#5f9ea0', '#cd5c5c',
];

const getSectionColor = (str: string) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % colorPalette.length;
  return colorPalette[index];
};

const getSectionStyle = (section: string) => {
  const color = getSectionColor(section);
  return {
    borderLeft: `4px solid ${color}`,
    backgroundColor: `${color}0D` 
  };
};
</script>

<style scoped>
.history-panel {
  width: 900px;
  max-width: 95vw;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

/* 覆盖 naive-ui 默认的 header 样式以支持 flex 布局 */
:deep(.n-card-header) {
  padding-bottom: 0;
}

.panel-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.panel-title {
  font-weight: bold;
  font-size: 18px;
}

.header-actions {
  display: flex;
  align-items: center;
}

:deep(.n-card__content) {
  overflow-y: auto;
  padding-right: 12px; 
  padding-top: 12px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  background-color: #fafafc;
  border: 1px solid #eee;
  transition: all 0.2s;
}

.history-item:hover {
  border-color: #d9d9d9;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}

.item-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-label {
  margin-left: auto;
  font-size: 12px;
  color: #999;
  font-family: 'Menlo', monospace;
}

.text-block {
  font-family: 'Menlo', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
}

.response-block {
  background-color: #fff;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #eaeaea;
  color: #333;
}

.word-count {
  font-size: 12px;
  color: #bbb;
}

.prompt-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.prompt-section {
  padding: 8px 12px;
  border-radius: 0 4px 4px 0;
}

.section-title {
  font-weight: 800;
  font-size: 12px;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-content {
  font-family: 'Menlo', 'Monaco', monospace;
  font-size: 12px;
  color: #555;
  white-space: pre-wrap;
}

.panel-footer {
  display: flex;
  justify-content: flex-end;
}
</style>