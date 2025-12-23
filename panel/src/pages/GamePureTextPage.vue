<template>
  <div class="game-dashboard">
    <div class="header-bar">
      <n-tabs 
        v-model:value="activePlayerId" 
        type="segment" 
        animated
        @update:value="handleTabChange"
      >
        <n-tab-pane 
          v-for="player in props.gameState.players" 
          :key="player.user_id" 
          :name="player.user_id"
        >
          <template #tab>
            <span class="tab-label">
              {{ player.user_id }}
              <n-tag 
                v-if="player.user_id === props.username" 
                type="success" 
                size="small" 
                round 
                :bordered="false"
                style="margin-left: 6px; transform: scale(0.85);"
              >
                YOU
              </n-tag>
              <n-tag 
                v-if="isBot.get(player.user_id)" 
                type="info" 
                size="small" 
                round 
                :bordered="false"
                style="margin-left: 6px; transform: scale(0.85);"
              >
                Bot
              </n-tag>
            </span>
          </template>
        </n-tab-pane>
      </n-tabs>
    </div>

    <div class="content-area">
      <n-card :title="`${activePlayerId} 的 Prompt`" class="prompt-card" content-style="padding: 0;">
        <div class="pure-text-container">
          <div v-if="loading" class="loading-state">
            <n-spin size="medium" />
            <span style="margin-left: 10px; color: #999;">Fetching prompt...</span>
          </div>
          <div v-else class="pure-text">
            {{ pureText || 'No prompt data available.' }}
          </div>
        </div>
      </n-card>
    </div>

    <div class="floating-actions">
      <n-space vertical>
        <n-tooltip trigger="hover" placement="left">
          <template #trigger>
            <n-button 
              circle 
              secondary 
              type="info" 
              size="large" 
              @click="handleViewHistory"
              class="action-btn"
            >
              <template #icon>
                <n-icon><IconHistory /></n-icon>
              </template>
            </n-button>
          </template>
          View Response History
        </n-tooltip>

        <n-tooltip trigger="hover" placement="left">
          <template #trigger>
            <n-button 
              circle 
              secondary 
              type="warning" 
              size="large" 
              @click="handleRenew"
              class="action-btn"
              :disabled="loading"
            >
              <template #icon>
                <n-icon><IconRenew /></n-icon>
              </template>
            </n-button>
          </template>
          Renew / Regenerate
        </n-tooltip>

        <n-tooltip trigger="hover" placement="left">
          <template #trigger>
            <n-button 
              circle 
              type="primary" 
              size="large" 
              @click="handleStep"
              class="action-btn"
            >
              <template #icon>
                <n-icon><IconPlay /></n-icon>
              </template>
            </n-button>
          </template>
          Step / Play
        </n-tooltip>
      </n-space>
    </div>
    <ResponseHistoryPanel 
      v-if="showHistoryPanel"
      :close-panel="() => showHistoryPanel = false"
      :username="activePlayerId"
      :history="currentHistory"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, reactive, onUpdated, computed } from 'vue';
import { 
  NTabs, NTabPane, NCard, NButton, NIcon, NSpace, NTooltip, NTag, NSpin 
} from 'naive-ui';
import type { GameState, ResponseItem } from '@/interfaces/GameState';
import { socket } from '@/utils/connect';
// 请确保引入路径正确
import IconRenew from '@/components/icons/IconRenew.vue';
import IconPlay from '@/components/icons/IconPlay.vue';
import IconHistory from '@/components/icons/IconHistory.vue'; // 需自行创建或引入通用 Icon
import ResponseHistoryPanel from '@/components/panels/ResponseHistoryPanel.vue'; // 刚才创建的组件

import { pubMsg } from '@/utils/general';
import type { RoomList } from '@/interfaces/RoomState';

const props = defineProps<{
  gameState: GameState;
  rooms: RoomList;
  username: string;
}>();

const activePlayerId = ref<string>(props.username);
const pureText = ref("");
const loading = ref(false);
const showHistoryPanel = ref(false); // 控制 History Panel 显示

const promptCache = reactive(new Map<string, string>());
const recentResponsesCache = reactive(new Map<string, ResponseItem[]>());
const isBot = reactive(new Map<string, boolean>());

// 计算当前选中玩家的历史记录
const currentHistory = computed(() => {
  return recentResponsesCache.get(activePlayerId.value) || [];
});

/**
 * 请求 Prompt 数据
 */
const fetchPrompt = (targetUser: string, forceRefresh = false) => {
  if (!forceRefresh && promptCache.has(targetUser)) {
    pureText.value = promptCache.get(targetUser) || "";
    return;
  }

  loading.value = true;
  pureText.value = ""; 
  socket.emit('query-prompt', {
    room_name: props.gameState.room_name, 
    username: targetUser
  });
};

const handleTabChange = (value: string) => {
  fetchPrompt(value);
  if (showHistoryPanel.value) {
    showHistoryPanel.value = false;
  }
};

const handleStep = () => {
  socket.emit('force-step-bot', {
    room_name: props.gameState.room_name,
    bot_id: activePlayerId.value 
  });
  pubMsg('提示', `已发送 Step 信号 (${activePlayerId.value})`, 'info', 2);
};

const handleRenew = () => {
  pubMsg('提示', `已发送 Renew 信号 (${activePlayerId.value})`, 'info', 2);
  fetchPrompt(activePlayerId.value, true);
};

// 新增：点击 History 按钮的处理函数
const handleViewHistory = () => {
  // 发送 socket 请求
  socket.emit('query-recent-response', {
    room_name: props.gameState.room_name,
    username: activePlayerId.value
  });
  console.log(`Querying recent responses for ${activePlayerId.value}...`);
  // 打开面板
  showHistoryPanel.value = true;
};

socket.on('prompt', (data: { username: string, prompt: string }) => {
  loading.value = false;
  pureText.value = data.prompt;
  
  if (activePlayerId.value) {
    promptCache.set(activePlayerId.value, data.prompt);
  }
});

socket.on('recent-response', (data: { username: string, recent_response: ResponseItem[] }) => {
  recentResponsesCache.set(data.username, data.recent_response);
  console.log(`Received recent responses for ${data.username}:`, data.recent_response);
  // 注意：由于 Vue reactive Map 的特性，Dependency 应该会自动更新，
  // 传递给 HistoryPanel 的 props 也会随之更新。
});

function initializeBotStatus() {
  props.gameState.players.forEach(player => {
    const room = props.rooms[props.gameState.room_name];
    if (room && room.bots.includes(player.user_id)) {
      isBot.set(player.user_id, true);
    } else {
      isBot.set(player.user_id, false);
    }
  });
}

onUpdated(() => {
  // 注意：这里原本的逻辑可能会导致频繁清空 cache，请按需保留
  // promptCache.clear(); 
  // console.log("GameState updated, refreshing prompt...");
  // fetchPrompt(activePlayerId.value, true);
  initializeBotStatus();
});

onMounted(() => {
  fetchPrompt(activePlayerId.value);
  initializeBotStatus();
});
</script>

<style scoped>
.game-dashboard {
  width: 100vw;
  height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header-bar {
  padding: 12px 24px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  z-index: 10;
  display: flex;
  justify-content: center;
}

.tab-label {
  display: flex;
  align-items: center;
}

.content-area {
  flex: 1;
  padding: 24px;
  display: flex;
  justify-content: center;
  overflow: hidden;
}

.prompt-card {
  width: 100%;
  max-width: 1000px;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-radius: 8px;
}

.pure-text-container {
  height: calc(100vh - 160px);
  overflow-y: auto;
  padding: 24px;
  background-color: #fff;
  position: relative;
}

.pure-text {
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 15px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.loading-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: row;
}

.floating-actions {
  position: fixed;
  right: 40px;
  bottom: 40px;
  z-index: 100;
}

.action-btn {
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  width: 56px;
  height: 56px;
  font-size: 24px;
}
</style>