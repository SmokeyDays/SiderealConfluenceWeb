<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NButton, NInputNumber, NSelect, NCard, NTabs, NTabPane, NInput, NDivider } from 'naive-ui';
import { getItemOption, items } from '@/interfaces/GameConfig';
import ItemEntryDiv from '@/components/ItemEntryDiv.vue';
import { type GameState } from '@/interfaces/GameState';
import PanelTemplate from '@/components/panels/PanelTemplate.vue';
import { socket } from '@/utils/connect';

const props = defineProps<{
  closePanel: () => void;
  username: string;
  gameState: GameState;
}>();

// 本地状态
const message = ref("");
const seeking = ref<{ [key: string]: number }>({});
const offering = ref<{ [key: string]: number }>({});

// 添加物品的临时状态
const defaultItem = "Food";
const defaultItemCount = 1;
const newItem = ref(defaultItem);
const newItemCount = ref(defaultItemCount);
const activeTab = ref("seeking"); // seeking | offering

// 初始化：从 GameState 中读取当前的公告板内容
onMounted(() => {
  const me = props.gameState.players.find(p => p.user_id === props.username);
  if (me && me.bulletin_board) {
    message.value = me.bulletin_board.message || "";
    // 浅拷贝对象，避免直接修改 store 里的数据
    seeking.value = { ...me.bulletin_board.seeking };
    offering.value = { ...me.bulletin_board.offering };
  }
});

// 获取当前激活的列表 (Seeking 或 Offering)
const getCurrentList = () => {
  return activeTab.value === "seeking" ? seeking.value : offering.value;
};

// 添加物品到当前列表
const addItem = () => {
  if (newItem.value !== "" && newItemCount.value > 0) {
    const list = getCurrentList();
    if (list[newItem.value] === undefined) {
      list[newItem.value] = newItemCount.value;
    } else {
      list[newItem.value] += newItemCount.value;
    }
  }
};

// 从当前列表移除物品
const removeItem = (item: string) => {
  const list = getCurrentList();
  delete list[item];
};

// 获取物品下拉选项
const getItemOptions = () => {
  // 这里可以过滤掉不需要显示的物品，比如 Score
  return items.filter(i => i !== 'Score').map(item => getItemOption(item));
};

// 提交更改
const submitBulletin = () => {
  socket.emit('update-bulletin-board', {
    room_name: props.gameState.room_name,
    username: props.username,
    message: message.value,
    seeking: seeking.value,
    offering: offering.value
  });
  props.closePanel();
};

const onTabChange = (value: string) => {
  activeTab.value = value;
  // 切换 tab 时重置添加器
  newItem.value = defaultItem;
  newItemCount.value = defaultItemCount;
};

</script>

<template>
  <PanelTemplate>
    <n-card hoverable class="bulletin-panel standard-panel" title="编辑交易公告板">
      <div class="bulletin-panel-content">
        
        <div class="section-title">公告留言</div>
        <n-input 
          v-model:value="message" 
          type="textarea" 
          placeholder="输入你想对大家说的话（例如：大量收食物，高价！）" 
          :autosize="{ minRows: 2, maxRows: 3 }" 
          maxlength="100"
          show-count
        />
        
        <!-- <n-divider /> -->

        <n-tabs v-model:value="activeTab" type="segment" animated @update:value="onTabChange">
          <n-tab-pane name="seeking" tab="我想要 (Seeking)">
            <div class="tab-helper-text">添加你希望收购的物品：</div>
          </n-tab-pane>
          <n-tab-pane name="offering" tab="我提供 (Offering)">
            <div class="tab-helper-text">添加你希望出售的物品：</div>
          </n-tab-pane>
        </n-tabs>

        <div class="items-display-container">
          <div class="empty-hint" v-if="Object.keys(getCurrentList()).length === 0">
            (暂无物品，请在下方添加)
          </div>
          <div class="item-entry-wrapper" v-for="(count, item) in getCurrentList()" :key="item">
            <ItemEntryDiv :item="item as string" :count="count" :iconWidth="50" :iconHeight="50" />
            <n-button 
              class="remove-btn" 
              circle 
              type="error" 
              size="tiny" 
              @click="removeItem(item as string)"
            >
              -
            </n-button>
          </div>
        </div>

        <div class="item-adder">
          <n-select 
            v-model:value="newItem" 
            :options="getItemOptions()" 
            placeholder="选择物品" 
            class="item-select"
          />
          <n-input-number 
            v-model:value="newItemCount" 
            :min="1" 
            class="item-count"
          />
          <n-button type="primary" @click="addItem" :disabled="!newItem">添加</n-button>
        </div>

        <div class="action-buttons">
            <n-button type="primary" size="large" @click="submitBulletin">发布公告</n-button>
            <n-button type="default" size="large" @click="props.closePanel">取消</n-button>
        </div>

      </div>
    </n-card>
  </PanelTemplate>
</template>

<style scoped>
.bulletin-panel {
  width: 500px;
  max-width: 90vw;
}

.bulletin-panel-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.section-title {
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 5px;
}

.tab-helper-text {
  margin-bottom: 10px;
  color: #666;
}

.items-display-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  min-height: 80px;
  background-color: #f9f9f9;
  border: 1px solid #eee;
  padding: 10px;
  border-radius: 8px;
  align-items: center;
}

.empty-hint {
  color: #ccc;
  width: 100%;
  text-align: center;
  font-style: italic;
}

.item-entry-wrapper {
  position: relative;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 5px;
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  z-index: 1;
}

.item-adder {
  display: flex;
  gap: 10px;
  align-items: center;
}

.item-select {
  flex: 2;
}

.item-count {
  flex: 1;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 10px;
}
</style>