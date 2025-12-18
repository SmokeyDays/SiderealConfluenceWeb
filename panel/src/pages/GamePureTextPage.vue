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
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, reactive, onUpdated } from 'vue';
import { 
  NTabs, NTabPane, NCard, NButton, NIcon, NSpace, NTooltip, NTag, NSpin 
} from 'naive-ui';
import type { GameState } from '@/interfaces/GameState';
import { socket } from '@/utils/connect';
import IconRenew from '@/components/icons/IconRenew.vue';
import IconPlay from '@/components/icons/IconPlay.vue';
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

const promptCache = reactive(new Map<string, string>());
const isBot = reactive(new Map<string, boolean>());

/**
 * 请求 Prompt 数据
 * @param targetUser 需要获取 Prompt 的用户 ID
 * @param forceRefresh 是否强制刷新（忽略缓存）
 */
const fetchPrompt = (targetUser: string, forceRefresh = false) => {
  // 如果不是强制刷新，且缓存中有数据，直接使用缓存
  if (!forceRefresh && promptCache.has(targetUser)) {
    pureText.value = promptCache.get(targetUser) || "";
    return;
  }

  // 否则发起网络请求
  loading.value = true;
  pureText.value = ""; // 清空当前显示，避免显示上一个人的残留
  socket.emit('query-prompt', {
    room_name: props.gameState.room_name, 
    username: targetUser
  });
};

/**
 * 切换 Tab 时触发
 */
const handleTabChange = (value: string) => {
  fetchPrompt(value);
};

const handleStep = () => {
  socket.emit('force-step-bot', {
    room_name: props.gameState.room_name,
    username: activePlayerId.value 
  });
  pubMsg('提示', `已发送 Step 信号 (${activePlayerId.value})`, 'info', 2);
};

const handleRenew = () => {
  pubMsg('提示', `已发送 Renew 信号 (${activePlayerId.value})`, 'info', 2);
  fetchPrompt(activePlayerId.value, true);
};

socket.on('prompt', (data: { prompt: string }) => {
  loading.value = false;
  pureText.value = data.prompt;
  
  if (activePlayerId.value) {
    promptCache.set(activePlayerId.value, data.prompt);
  }
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
  promptCache.clear();
  console.log("GameState updated, refreshing prompt...");
  fetchPrompt(activePlayerId.value, true);
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

/* 垂直居中 Tab 里的文字和 Tag */
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
  position: relative; /* 为 loading 居中做准备 */
}

.pure-text {
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 15px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* Loading 状态样式 */
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