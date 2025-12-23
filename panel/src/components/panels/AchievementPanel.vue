<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NCard, NEmpty, NIcon, NTooltip } from 'naive-ui';
import { getItemZhDesc, getSpecieColor, items } from '@/interfaces/GameConfig';
import type { Factory, GameState } from '@/interfaces/GameState';
import PanelTemplate from '@/components/panels/PanelTemplate.vue';
import type { Achievement } from '@/interfaces/UserState';
import ItemIcon from '@/components/ItemIcon.vue';
const props = defineProps<{
  closeAchievementPanel: () => void;
  achievements: Achievement[];
}>();
</script>

<template>
  <PanelTemplate>
    <n-card hoverable class="standard-panel" content-class="achievement-panel">
      <div class="achievement-title">成就</div>
        <n-button class="close-achievement-button" @click="props.closeAchievementPanel" type="error">关闭</n-button>
        <template v-if="props.achievements.length > 0">
          <div class="achievement-list">
            <template v-for="achievement in props.achievements" :key="achievement.id">
              <n-tooltip trigger="click">
                <template #trigger>
                  <div class="achievement-item" :class="'achievement-item-' + achievement.difficulty + (achievement.unlocked ? ' achievement-item-unlocked' : ' achievement-item-locked')">
                    <n-icon :size="40">
                      <ItemIcon :item="'Achievement' + achievement.difficulty" />
                    </n-icon>
                    <div class="achievement-desc">
                      <div class="achievement-item-title">{{ achievement.name }}</div>
                      <template v-if="achievement.unlocked">
                        <div class="achievement-item-description">{{ achievement.description }}</div>
                      </template>
                    </div>
                  </div>
                </template>
                <div class="achievement-item-hint">{{ achievement.hint ? achievement.hint : '？？？' }}</div>
              </n-tooltip>
            </template>
          </div>
        </template>
        <template v-else>
          <n-empty description="成就加载中..." />
        </template>
    </n-card>
  </PanelTemplate>
</template>

<style>
.achievement-panel {
  overflow-y: auto;
}
.achievement-list {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: wrap;
}
.achievement-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  width: 250px;
  padding: 10px;
  margin: 5px;
  border-radius: 10px;
  border: 1px solid var(--n-border-color);
  box-shadow: 0 0 5px 0 rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease;
  /* background-color: #eeeeee; */
}
.achievement-item-0:hover {
  color: #eeeeee;
  background-color: #302c2c;
}
.achievement-item-1:hover {
  background-color: #fd7b01;
}
.achievement-item-2:hover {
  background-color: #7b7676;
}
.achievement-item-3:hover {
  background-color: #91ab29;
}
.achievement-desc {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;

}
.achievement-item-title {
  font-weight: bold;
}
.achievement-item-hint {
  font-style: italic;
}
.close-achievement-button {
  position: absolute;
  bottom: 40px;
  right: 40px;
}
.achievement-title {
  font-size: 1.2rem;
  font-weight: bold;
}
</style>
