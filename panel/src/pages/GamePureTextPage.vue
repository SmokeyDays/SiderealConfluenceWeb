<template>
  <div class="scifi-page">
    
    <div class="top-command-bar">
      <div class="bar-deco"></div>
      <div class="tabs-container">
        <n-tabs 
          v-model:value="activePlayerId" 
          type="card" 
          animated
          @update:value="handleTabChange"
          class="scifi-tabs"
        >
          <n-tab-pane 
            v-for="player in props.gameState.players" 
            :key="player.user_id" 
            :name="player.user_id"
          >
            <template #tab>
              <div class="tab-label-content">
                <span class="tab-text">{{ player.user_id }}</span>
                <div class="tab-indicators">
                   <span v-if="player.user_id === props.username" class="indicator me">ME</span>
                   <span v-if="isBot.get(player.user_id)" class="indicator bot">AI</span>
                </div>
              </div>
            </template>
          </n-tab-pane>
        </n-tabs>
      </div>
      <div class="bar-deco right"></div>
    </div>

    <div class="terminal-viewport">
      <div class="terminal-frame">
        <div class="terminal-header">
           <span class="header-title">>> PROMPT_LOG // {{ activePlayerId }}</span>
           <div class="header-status">
              <span class="status-dot" :class="{ loading: loading }"></span>
              {{ loading ? '加载中...' : '加载完毕' }}
           </div>
        </div>
        
        <div class="terminal-screen custom-scrollbar">
           <div v-if="loading" class="loading-overlay">
              <n-spin size="large" stroke="var(--scifi-primary)">
                <template #description>
                  <span class="loading-text">DECRYPTING STREAM...</span>
                </template>
              </n-spin>
           </div>
           
           <div v-else class="code-content">
             <div v-if="!pureText" class="no-data">
               [NULL] NO DATA RECEIVED FROM CORE.
             </div>
             <div v-else class="prompt-text">
               {{ pureText }}
             </div>
           </div>
        </div>
      </div>
    </div>

    <div class="right-command-dock">
      <div class="dock-header">CMDS</div>
      
      <n-tooltip trigger="hover" placement="left">
        <template #trigger>
          <button class="scifi-btn info" @click="handleViewHistory">
            <n-icon size="24"><IconHistory /></n-icon>
            <span class="btn-label">LOGS</span>
          </button>
        </template>
        查看历史回复
      </n-tooltip>

      <div class="dock-separator"></div>

      <n-tooltip trigger="hover" placement="left">
        <template #trigger>
          <button class="scifi-btn warning" @click="handleRenew" :disabled="loading">
            <n-icon size="24"><IconRenew /></n-icon>
            <span class="btn-label">RENEW</span>
          </button>
        </template>
        重新加载
      </n-tooltip>

      <n-tooltip trigger="hover" placement="left">
        <template #trigger>
          <button class="scifi-btn primary" @click="handleStep">
            <n-icon size="24"><IconPlay /></n-icon>
            <span class="btn-label">STEP</span>
          </button>
        </template>
        单步执行
      </n-tooltip>
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
// 逻辑部分保持不变
import { onMounted, ref, reactive, onUpdated, computed } from 'vue';
import { 
  NTabs, NTabPane, NIcon, NSpin, NTooltip 
} from 'naive-ui';
import type { GameState, ResponseItem } from '@/interfaces/GameState';
import { socket } from '@/utils/connect';
import IconRenew from '@/components/icons/IconRenew.vue';
import IconPlay from '@/components/icons/IconPlay.vue';
import IconHistory from '@/components/icons/IconHistory.vue';
import ResponseHistoryPanel from '@/components/panels/ResponseHistoryPanel.vue'; 
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
const showHistoryPanel = ref(false);

const promptCache = reactive(new Map<string, string>());
const recentResponsesCache = reactive(new Map<string, ResponseItem[]>());
const isBot = reactive(new Map<string, boolean>());

const currentHistory = computed(() => {
  return recentResponsesCache.get(activePlayerId.value) || [];
});

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
  pubMsg('SYSTEM', `Step Signal Sent > ${activePlayerId.value}`, 'info', 2);
};

const handleRenew = () => {
  pubMsg('SYSTEM', `Renew Signal Sent > ${activePlayerId.value}`, 'info', 2);
  fetchPrompt(activePlayerId.value, true);
};

const handleViewHistory = () => {
  socket.emit('query-recent-response', {
    room_name: props.gameState.room_name,
    username: activePlayerId.value
  });
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
  initializeBotStatus();
});

onMounted(() => {
  fetchPrompt(activePlayerId.value);
  initializeBotStatus();
});
</script>

<style scoped>
.scifi-page {
  width: 100vw;
  height: 100vh;
  background: transparent; 
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: 'Share Tech Mono', monospace;
  color: var(--scifi-text);
}

/* === 1. Top Command Bar (Tabs) === */
.top-command-bar {
  height: 60px;
  display: flex;
  align-items: center;
  background: rgba(5, 10, 20, 0.8);
  border-bottom: 1px solid var(--scifi-border);
  backdrop-filter: blur(5px);
  padding: 0 10px;
}

.bar-deco {
  width: 20px;
  height: 100%;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 5px,
    rgba(0, 212, 255, 0.1) 5px,
    rgba(0, 212, 255, 0.1) 10px
  );
  border-right: 1px solid var(--scifi-border);
}
.bar-deco.right {
  border-right: none;
  border-left: 1px solid var(--scifi-border);
}

.tabs-container {
  flex: 1;
  overflow-x: auto;
  padding: 0 20px;
  /* 隐藏滚动条 */
  scrollbar-width: none;
}
.tabs-container::-webkit-scrollbar { display: none; }

/* 深度定制 Naive UI Tabs */
:deep(.n-tabs-nav) {
  background: transparent !important;
}
:deep(.n-tabs-tab) {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid transparent !important;
  border-bottom: none !important;
  color: var(--scifi-text-dim) !important;
  font-family: 'Orbitron', sans-serif !important;
  transition: all 0.3s !important;
  clip-path: polygon(10px 0, 100% 0, 100% 100%, 0 100%, 0 10px); /* 切角 Tab */
  margin-right: 5px !important;
}
:deep(.n-tabs-tab--active) {
  background: rgba(0, 212, 255, 0.15) !important;
  border: 1px solid var(--scifi-primary) !important;
  color: var(--scifi-primary) !important;
  box-shadow: 0 -2px 10px rgba(0, 212, 255, 0.2) !important;
}

.tab-label-content {
  display: flex;
  align-items: center;
  gap: 8px;
}
.tab-text { font-weight: bold; }
.tab-indicators { display: flex; gap: 4px; }
.indicator {
  font-size: 0.6rem;
  padding: 0 4px;
  border-radius: 2px;
  font-weight: bold;
  color: #000;
}
.indicator.me { background: var(--scifi-success, #00ff9d); }
.indicator.bot { background: var(--scifi-text-dim, #888); color: #fff; }

/* === 2. Terminal Viewport === */
.terminal-viewport {
  flex: 1;
  height: 0;
  padding: 20px;
  padding-right: 90px; 
  display: flex;
  justify-content: center;
  align-items: center;
}

.terminal-frame {
  width: 100%;
  height: 100%;
  max-width: 1200px;
  background: rgba(0, 10, 15, 0.9);
  border: 1px solid var(--scifi-border);
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  clip-path: polygon(
    20px 0, 100% 0, 
    100% calc(100% - 20px), calc(100% - 20px) 100%, 
    0 100%, 0 20px
  );
}

.terminal-header {
  height: 40px;
  background: rgba(0, 212, 255, 0.1);
  border-bottom: 1px solid var(--scifi-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.9rem;
}
.header-title { color: var(--scifi-primary); letter-spacing: 1px; }
.header-status { font-size: 0.8rem; color: var(--scifi-text-dim); display: flex; align-items: center; gap: 8px; }
.status-dot { width: 8px; height: 8px; background: var(--scifi-success, #00ff9d); border-radius: 50%; box-shadow: 0 0 5px var(--scifi-success); }
.status-dot.loading { background: var(--scifi-warning, #f2c94c); animation: blink 0.5s infinite; }

.terminal-screen {
  flex: 1;
  height: 0;
  position: relative;
  overflow-y: auto;
  padding: 20px;
  background: radial-gradient(circle at center, rgba(0, 20, 0, 0.2), transparent);
}

/* 文本样式 */
.prompt-text {
  font-family: 'Share Tech Mono', 'Menlo', monospace; /* 使用科幻等宽字体 */
  font-size: 15px;
  line-height: 1.6;
  color: #aaddff; /* 终端亮蓝/青色 */
  white-space: pre-wrap;
  word-wrap: break-word;
  text-shadow: 0 0 2px rgba(0, 212, 255, 0.3);
  padding-bottom: 100px;
}

.no-data {
  color: var(--scifi-text-dim);
  font-style: italic;
  margin-top: 20px;
  text-align: center;
}

/* Loading Overlay */
.loading-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 5;
}
.loading-text {
  font-family: 'Orbitron', sans-serif;
  color: var(--scifi-primary);
  margin-top: 10px;
  letter-spacing: 2px;
}

/* === 3. Right Command Dock === */
.right-command-dock {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 15px;
  z-index: 100;
  
  /* Dock 容器样式 */
  background: rgba(5, 10, 20, 0.8);
  border: 1px solid var(--scifi-border);
  padding: 15px 10px;
  border-radius: 0; /* 硬朗 */
  backdrop-filter: blur(4px);
  /* 梯形外观 */
  clip-path: polygon(0 10px, 100% 0, 100% 100%, 0 calc(100% - 10px));
}

.dock-header {
  text-align: center;
  font-size: 0.7rem;
  color: var(--scifi-text-dim);
  letter-spacing: 2px;
  margin-bottom: 5px;
  font-weight: bold;
}

.dock-separator {
  height: 1px;
  background: var(--scifi-border);
  opacity: 0.5;
  margin: 5px 0;
}

/* 自定义科幻按钮 (HTML Button) */
.scifi-btn {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--scifi-border);
  color: var(--scifi-primary);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}

.scifi-btn:hover {
  background: rgba(0, 212, 255, 0.15);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
  transform: scale(1.05);
}

.scifi-btn:active {
  transform: scale(0.95);
}

.scifi-btn .btn-label {
  font-size: 0.6rem;
  font-family: 'Orbitron', sans-serif;
  margin-top: 4px;
  letter-spacing: 1px;
}

/* 不同类型的按钮颜色 */
.scifi-btn.warning { color: var(--scifi-warning, #f2c94c); border-color: var(--scifi-warning, #f2c94c); }
.scifi-btn.warning:hover { background: rgba(242, 201, 76, 0.15); box-shadow: 0 0 15px rgba(242, 201, 76, 0.3); }

.scifi-btn.info { color: var(--scifi-info, #70c0e8); }

.scifi-btn.primary { color: var(--scifi-primary, #00d4ff); font-weight: bold; }

@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

/* ... 原有的 CSS 代码 ... */

/* === 4. Custom Scrollbar Fix (修复滚动条) === */
.custom-scrollbar {
  /* Firefox 兼容 */
  scrollbar-width: thin;
  scrollbar-color: var(--scifi-primary) rgba(0, 0, 0, 0.2);
}

/* Webkit 浏览器 (Chrome, Safari, Edge) */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px; /* 关键：必须设置宽度，否则不显示 */
  height: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  /* 使用你的主题色，平时半透明 */
  background: rgba(0, 212, 255, 0.3); 
  border-radius: 3px;
  transition: all 0.3s;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  /* 鼠标悬停时高亮 */
  background: rgba(0, 212, 255, 0.8);
  box-shadow: 0 0 8px var(--scifi-primary);
  cursor: pointer;
}
</style>