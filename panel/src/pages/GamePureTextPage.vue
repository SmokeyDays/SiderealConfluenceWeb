<template>
  <div class="scifi-page">
    
    <div class="top-command-bar">
      <div 
        class="bar-deco interactive" 
        @click="isLogOpen = !isLogOpen"
        :class="{ active: isLogOpen }"
      >
        <n-icon size="18" :component="IconMenu" />
      </div>

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

    <div class="content-wrapper">
      
      <div class="left-log-panel" :class="{ collapsed: !isLogOpen }">
        <div class="panel-inner">
          <div class="panel-header">
            <span class="panel-title">SYSTEM_LOGS</span>
            <span class="log-count">[{{ callingHistoryList.length }}]</span>
          </div>
          <div class="log-list custom-scrollbar">
            <div v-if="callingHistoryList.length === 0" class="no-logs">
              NO SIGNALS DETECTED
            </div>
            <div 
              v-else
              v-for="(log, index) in callingHistoryList" 
              :key="index" 
              class="log-item"
            >
              <div class="log-meta">
                <span class="log-time">{{ formatTime(log.timestamp) }}</span>
                <span class="log-bot">{{ log.bot_id }}</span>
              </div>
              <div class="log-event">
                <span class="event-indicator">></span> {{ log.event_type }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="terminal-viewport">
        <div class="terminal-frame">
          <div class="terminal-header">
             <span class="header-title">>> CURRENT_PROMPT // {{ activePlayerId }}</span>
             <div class="header-status">
               <span class="status-dot" :class="{ loading: loading }"></span>
               {{ loading ? '加载中...' : '加载完毕' }}
             </div>
          </div>
          
          <div class="terminal-screen custom-scrollbar">
             <div v-if="loading" class="loading-overlay">
               <n-spin size="large" stroke="var(--scifi-primary)">
                 <template #description>
                   <span class="loading-text">LOADING...</span>
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

    </div> <div class="right-command-dock">
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

      <n-tooltip trigger="hover" placement="left" v-if="isBot.get(activePlayerId)">
        <template #trigger>
          <button class="scifi-btn primary" @click="handleStep">
            <n-icon size="24"><IconPlay /></n-icon>
            <span class="btn-label">STEP</span>
          </button>
        </template>
        单步执行
      </n-tooltip>
      
      <n-tooltip trigger="hover" placement="left">
        <template #trigger>
          <button 
            class="scifi-btn" 
            :class="isAutoReact ? 'success' : 'inactive'" 
            @click="handleToggleBot"
          >
            <n-icon size="24">
              <IconToggleOn v-if="isAutoReact" />
              <IconToggleOff v-else />
            </n-icon>
            <span class="btn-label">AUTO</span>
          </button>
        </template>
        {{ isAutoReact ? '停止 AI 自动响应' : '开启 AI 自动响应' }}
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
import { onMounted, ref, reactive, onUpdated, computed } from 'vue';
import { 
  NTabs, NTabPane, NIcon, NSpin, NTooltip 
} from 'naive-ui';
import type { GameState, ResponseItem } from '@/interfaces/GameState';
import { socket } from '@/utils/connect';
// Icons
import IconRenew from '@/components/icons/IconRenew.vue';
import IconPlay from '@/components/icons/IconPlay.vue';
import IconHistory from '@/components/icons/IconHistory.vue';
import IconToggleOn from '@/components/icons/IconToggleOn.vue';
import IconToggleOff from '@/components/icons/IconToggleOff.vue';
import IconResize from '@/components/icons/IconResize.vue';
import IconMenu from '@/components/icons/IconMenu.vue';

import ResponseHistoryPanel from '@/components/panels/ResponseHistoryPanel.vue'; 
import { pubMsg } from '@/utils/general';
import type { RoomList, TaskRecord } from '@/interfaces/RoomState';

const props = defineProps<{
  gameState: GameState;
  rooms: RoomList;
  username: string;
}>();

const activePlayerId = ref<string>(props.username);
const pureText = ref("");
const loading = ref(false);
const showHistoryPanel = ref(false);

// NEW: 左侧日志栏状态
const isLogOpen = ref(false); 
const callingHistoryList = ref<TaskRecord[]>([]);

const promptCache = reactive(new Map<string, string>());
const recentResponsesCache = reactive(new Map<string, ResponseItem[]>());
const isBot = reactive(new Map<string, boolean>());

const currentHistory = computed(() => {
  return recentResponsesCache.get(activePlayerId.value) || [];
});

const isAutoReact = computed(() => {
  const room = props.rooms[props.gameState.room_name];
  return room ? room.bots_auto_react : false;
});

// Helper: 格式化时间戳
const formatTime = (ts: string) => {
    // 假设 ts 是 ISO 字符串或者类似格式，截取时间部分
    // 如果是 unix timestamp 需要 new Date(ts)
    try {
        return ts.split('T')[1].split('.')[0]; 
    } catch (e) {
        return ts; 
    }
}

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
  fetchCallingHistory();
};

const handleViewHistory = () => {
  socket.emit('query-recent-response', {
    room_name: props.gameState.room_name,
    username: activePlayerId.value
  });
  showHistoryPanel.value = true;
};

// 废弃未使用的函数，或者在 mount 时调用
const fetchCallingHistory = () => {
  socket.emit('query-calling-history', {
    room_name: props.gameState.room_name
  });
};

const handleToggleBot = () => {
  socket.emit('toggle-bot', {
    room_name: props.gameState.room_name
  });
  const actionText = isAutoReact.value ? 'Disable' : 'Enable';
  pubMsg('SYSTEM', `Signal Sent > ${actionText} Auto-Bot`, 'info', 1);
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

// MODIFIED: 接收并存储 calling history
socket.on('calling-history', (data: { calling_history: TaskRecord[] }) => {
  // console.log('calling-history:', data.calling_history);
  // 倒序排列，最新的在上面
  callingHistoryList.value = [...data.calling_history].reverse();
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
  // 页面加载时请求一次历史记录
  fetchCallingHistory();
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

.top-command-bar {
  height: 60px;
  display: flex;
  align-items: center;
  background: rgba(5, 10, 20, 0.8);
  border-bottom: 1px solid var(--scifi-border);
  backdrop-filter: blur(5px);
  padding: 0 10px;
  flex-shrink: 0; /* 防止被挤压 */
  z-index: 20;
}

.bar-deco {
  width: 40px; /* 加宽以便点击 */
  height: 100%;
  border-right: 1px solid var(--scifi-border);
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--scifi-text-dim);
  transition: all 0.3s;
}

/* NEW: 左侧装饰按钮样式 */
.bar-deco.interactive {
  cursor: pointer;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 5px,
    rgba(0, 212, 255, 0.05) 5px,
    rgba(0, 212, 255, 0.05) 10px
  );
}
.bar-deco.interactive:hover {
  background-color: rgba(0, 212, 255, 0.1);
  color: var(--scifi-primary);
}
.bar-deco.interactive.active {
  color: var(--scifi-primary);
  background-color: rgba(0, 212, 255, 0.15);
  box-shadow: inset 0 0 10px rgba(0, 212, 255, 0.2);
}

.bar-deco.right {
  width: 20px;
  border-right: none;
  border-left: 1px solid var(--scifi-border);
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 5px,
    rgba(0, 212, 255, 0.1) 5px,
    rgba(0, 212, 255, 0.1) 10px
  );
}

.tabs-container {
  flex: 1;
  overflow-x: auto;
  padding: 0 20px;
  scrollbar-width: none;
}
.tabs-container::-webkit-scrollbar { display: none; }

/* ... (Tabs 样式保持不变) ... */
:deep(.n-tabs-nav) { background: transparent !important; }
:deep(.n-tabs-tab) {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid transparent !important;
  border-bottom: none !important;
  color: var(--scifi-text-dim) !important;
  font-family: 'Orbitron', sans-serif !important;
  transition: all 0.3s !important;
  clip-path: polygon(10px 0, 100% 0, 100% 100%, 0 100%, 0 10px);
  margin-right: 5px !important;
}
:deep(.n-tabs-tab--active) {
  background: rgba(0, 212, 255, 0.15) !important;
  border: 1px solid var(--scifi-primary) !important;
  color: var(--scifi-primary) !important;
  box-shadow: 0 -2px 10px rgba(0, 212, 255, 0.2) !important;
}

.tab-label-content { display: flex; align-items: center; gap: 8px; }
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

/* === NEW: Content Wrapper === */
.content-wrapper {
  flex: 1;
  display: flex;
  overflow: hidden; /* 防止子元素溢出 */
  position: relative;
}

/* === NEW: Left Log Panel === */
.left-log-panel {
  width: 280px; /* 展开宽度 */
  background: rgba(0, 5, 10, 0.8);
  border-right: 1px solid var(--scifi-border);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.left-log-panel.collapsed {
  width: 0;
  border-right: none;
}

.panel-inner {
  min-width: 280px; /* 防止内容挤压 */
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-header {
  height: 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 15px;
  background: rgba(0, 212, 255, 0.05);
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  font-family: 'Orbitron', sans-serif;
  font-size: 0.8rem;
  letter-spacing: 1px;
  color: var(--scifi-primary);
}
.log-count { color: var(--scifi-text-dim); }

.log-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.no-logs {
  padding: 20px;
  text-align: center;
  color: var(--scifi-text-dim);
  font-size: 0.8rem;
  font-style: italic;
  opacity: 0.5;
}

.log-item {
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  animation: slideIn 0.3s ease-out;
}
@keyframes slideIn { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }

.log-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: var(--scifi-text-dim);
  margin-bottom: 4px;
}
.log-bot { color: var(--scifi-warning, #f2c94c); font-weight: bold; }

.log-event {
  font-size: 0.8rem;
  color: #aaddff;
  line-height: 1.2;
}
.event-indicator { color: var(--scifi-success, #00ff9d); margin-right: 4px; }


/* === 2. Terminal Viewport (Modified) === */
.terminal-viewport {
  flex: 1;
  height: 100%; /* 填满高度 */
  padding: 20px;
  padding-right: 90px; /* 给右侧Dock留空 */
  display: flex;
  justify-content: center;
  align-items: center;
  min-width: 0; /* Flexbox 溢出修复 */
}

/* ... (Terminal Frame & Header & Screen 样式保持不变) ... */

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

.prompt-text {
  font-family: 'Share Tech Mono', 'Menlo', monospace;
  font-size: 15px;
  line-height: 1.6;
  color: #aaddff;
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

/* ... (Right Command Dock & Button Styles 保持不变) ... */

.right-command-dock {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 15px;
  z-index: 100;
  background: rgba(5, 10, 20, 0.8);
  border: 1px solid var(--scifi-border);
  padding: 15px 10px;
  border-radius: 0; 
  backdrop-filter: blur(4px);
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
.scifi-btn:active { transform: scale(0.95); }
.scifi-btn .btn-label {
  font-size: 0.6rem;
  font-family: 'Orbitron', sans-serif;
  margin-top: 4px;
  letter-spacing: 1px;
}
.scifi-btn.warning { color: var(--scifi-warning, #f2c94c); border-color: var(--scifi-warning, #f2c94c); }
.scifi-btn.warning:hover { background: rgba(242, 201, 76, 0.15); box-shadow: 0 0 15px rgba(242, 201, 76, 0.3); }
.scifi-btn.info { color: var(--scifi-info, #70c0e8); }
.scifi-btn.primary { color: var(--scifi-primary, #00d4ff); font-weight: bold; }
.scifi-btn.success { color: var(--scifi-success, #00ff9d); border-color: var(--scifi-success, #00ff9d); box-shadow: 0 0 5px rgba(0, 255, 157, 0.2); }
.scifi-btn.success:hover { background: rgba(0, 255, 157, 0.15); box-shadow: 0 0 15px rgba(0, 255, 157, 0.4); }
.scifi-btn.inactive { color: var(--scifi-text-dim, #666); border-color: var(--scifi-border); opacity: 0.8; }
.scifi-btn.inactive:hover { color: var(--scifi-text); border-color: var(--scifi-text); background: rgba(255, 255, 255, 0.05); }

@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

/* Scrollbar Fixes */
.custom-scrollbar { scrollbar-width: thin; scrollbar-color: var(--scifi-primary) rgba(0, 0, 0, 0.2); }
.custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.2); border-radius: 3px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(0, 212, 255, 0.3); border-radius: 3px; transition: all 0.3s; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(0, 212, 255, 0.8); box-shadow: 0 0 8px var(--scifi-primary); cursor: pointer; }
</style>