<template>
  <div class="lobby-page">
    <header class="lobby-navbar glass-panel">
      <div class="nav-left">
        <h3 class="app-title">游戏大厅</h3>
      </div>
      <div class="nav-right">
        <span class="welcome-text">
          当前用户: <b>{{ props.username }}</b>
        </span>
        <n-divider vertical />
        <n-button size="small" quaternary type="error" @click="logout">
          <template #icon><n-icon><LogoutOutlined /></n-icon></template>
          退出
        </n-button>
      </div>
    </header>

    <main class="view-content">
      <transition name="fade" mode="out-in">
        
        <div v-if="currentView === 'list'" class="view-container list-view" key="list">
          <div class="glass-panel action-bar">
             <div class="action-title">房间列表</div>
             <n-input-group class="create-room-group">
                <n-input 
                  v-model:value="newRoomName" 
                  placeholder="输入新房间名称" 
                  @keyup.enter="createRoom(newRoomName)" 
                />
                <n-button type="primary" @click="createRoom(newRoomName)">
                  创建
                </n-button>
             </n-input-group>
          </div>

          <div class="room-grid-wrapper">
             <div v-if="Object.keys(rooms).length === 0" class="empty-state glass-panel">
                暂无房间，创建一个吧！
             </div>
             
             <div class="room-grid" v-else>
                <n-card 
                  v-for="(room, index) in rooms" 
                  :key="index" 
                  class="room-card glass-card" 
                  :class="getRoomType(room.name)" 
                  @click="switchView('room', room.name)" 
                  hoverable
                  size="small"
                  :bordered="false"
                >
                  <template #header>
                    <div class="room-card-header">
                      <span class="room-name-text" :title="room.name">{{ room.name }}</span>
                      <n-tag :type="getRoomStatusType(room)" size="small" round>
                          {{ getRoomStatusText(room) }}
                      </n-tag>
                    </div>
                  </template>
                  
                  <div class="room-details">
                    <div class="detail-item">
                      <span class="label">人数</span>
                      <span class="value">{{ Object.keys(room.players).length }} / {{ room.max_players }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">总轮数</span>
                      <span class="value">{{ room.end_round }}</span>
                    </div>
                    
                    <div v-if="meInRoom(room.name)" class="my-status-mini">
                      <n-divider style="margin: 6px 0" />
                      <div class="role-row">
                        <span>扮演: </span>
                        <SpecieZhDiv v-if="props.rooms[room.name].players[props.username].specie" 
                                     :specie="props.rooms[room.name].players[props.username].specie" 
                                     :is-me="false" is-span />
                        <span v-else class="text-gray">(未选)</span>
                      </div>
                    </div>
                  </div>

                  <template #action>
                    <div class="card-footer">
                      <span class="state-text">{{ room.game_state === 'playing' ? '🔥 进行中' : '💤 等待中' }}</span>
                      <n-button 
                        v-if="Object.keys(room.players).length === 0" 
                        size="tiny" type="error" ghost
                        @click.stop="deleteRoom(room.name)"
                      >
                        删除
                      </n-button>
                    </div>
                  </template>
                </n-card>
             </div>
          </div>
        </div>

        <div v-else class="view-container room-view" key="room">
          <div class="glass-panel room-header">
             <n-button text @click="switchView('list', '')" class="back-btn">
                <span style="font-size: 1.2em; margin-right: 5px">←</span> 返回大厅
             </n-button>
             <n-divider vertical />
             <span class="room-title">{{ props.currentRoom }}</span>
             <span class="room-subtitle">({{ Object.keys(props.rooms[props.currentRoom].players).length }} / {{ props.rooms[props.currentRoom].max_players }}人)</span>
          </div>

          <div class="room-content-split">
             <div class="left-panel glass-panel">
                <div class="panel-title">玩家列表</div>
                <div class="player-list-scroll">
                   <div 
                      v-for="(info, name) in props.rooms[props.currentRoom].players" 
                      :key="name" 
                      class="player-item"
                      :class="{ 'bot-item': isBot(name), 'me-item': name === props.username }"
                    >
                      <div class="p-info">
                        <div class="p-name">
                          {{ name }}
                          <n-tag v-if="isBot(name)" size="tiny" :bordered="false" class="ml-1">BOT</n-tag>
                          <n-tag v-if="name === props.username" type="info" size="tiny" :bordered="false" class="ml-1">我</n-tag>
                        </div>
                        <div class="p-specie">
                           <span :style="{ color: info.specie ? getSpecieColor(info.specie) : '#999' }">
                             {{ info.specie ? getSpecieZhName(info.specie) : '等待选择种族...' }}
                           </span>
                        </div>
                      </div>
                      <div class="p-status">
                         <n-tag v-if="info.agreed" type="success" size="small" round :bordered="false">已准备</n-tag>
                         <n-tag v-else type="warning" size="small" round :bordered="false">未准备</n-tag>
                         <n-popconfirm v-if="isBot(name)" @positive-click="removeBot(name)">
                            <template #trigger>
                              <n-button circle size="tiny" type="error" quaternary class="del-bot-btn">✕</n-button>
                            </template>
                            移除该机器人？
                         </n-popconfirm>
                      </div>
                   </div>
                </div>
             </div>

             <div class="right-panel glass-panel">
                <div class="panel-title">游戏设置</div>
                <div class="controls-wrapper">
                   
                   <div v-if="!meInRoom(props.currentRoom)" class="join-box">
                      <n-button type="primary" block size="large" 
                        @click="enterRoom" 
                        :disabled="roomIsFull(props.currentRoom) || props.rooms[props.currentRoom].game_state === 'playing'">
                        加入房间
                      </n-button>
                   </div>

                   <template v-else>
                      <div class="control-group">
                         <div class="group-label">我的种族</div>
                         <n-input-group>
                           <n-select 
                             v-model:value="chosenSpecie" 
                             :options="getSpecieSelectOptions()" 
                             placeholder="选择种族" 
                             :disabled="isAgreed(props.currentRoom)"
                           />
                           <n-button type="primary" ghost @click="submitSpecieChoice" :disabled="isAgreed(props.currentRoom)">确定</n-button>
                         </n-input-group>
                      </div>

                      <div class="control-group main-btn-group">
                         <n-button 
                           v-if="isAgreed(props.currentRoom)" 
                           type="warning" block size="large" secondary
                           @click="disagreeToStart"
                         >
                           取消准备
                         </n-button>
                         <n-button 
                           v-else 
                           type="success" block size="large" secondary
                           :disabled="!specieChosen(props.currentRoom)"
                           @click="agreeToStart"
                         >
                           准备开始
                         </n-button>
                      </div>
                      
                      <n-divider style="margin: 15px 0" />

                      <div class="control-group">
                         <div class="group-label">结束回合<span class="text-gray">（当前{{ props.rooms[props.currentRoom].end_round }}轮）</span></div>
                         <n-input-group size="small">
                            <n-input-number v-model:value="endRoundInput" :min="1" :placeholder="String(props.rooms[props.currentRoom].end_round)" style="flex:1"/>
                            <n-button ghost @click="setEndRound">修改</n-button>
                         </n-input-group>
                      </div>

                      <div class="control-group" v-if="Object.keys(props.rooms[props.currentRoom].players).length < props.rooms[props.currentRoom].max_players">
                         <div class="group-label">添加电脑玩家</div>
                         <n-space vertical size="small">
                            <n-input v-model:value="botId" placeholder="ID" size="small"/>
                            <n-select v-model:value="botSpecie" :options="getSpecieSelectOptions()" placeholder="种族" size="small"/>
                            <n-button dashed block size="small" @click="addBot">添加 Bot</n-button>
                         </n-space>
                      </div>

                      <div class="spacer"></div>
                      
                      <n-button type="error" quaternary block @click="leaveRoom">
                        <template #icon><n-icon><LogoutOutlined /></n-icon></template>
                        离开房间
                      </n-button>
                   </template>
                </div>
             </div>
          </div>
        </div>

      </transition>
    </main>
  </div>
</template>

<script setup lang="ts">
// (Script 部分保持原样，无需修改逻辑，直接复用原代码即可)
import { ref } from 'vue';
import { 
  NButton, NSpace, NSelect, NInput, NInputNumber, NCard, 
  NIcon, NTag, NInputGroup, NDivider, NPopconfirm,
  type SelectGroupOption, type SelectOption 
} from 'naive-ui';
import type { RoomList } from '../interfaces/RoomState';
import { socket } from '@/utils/connect';
import { getSpecieColor, getSpecieZhName, species } from '@/interfaces/GameConfig';
import type { GameState } from '@/interfaces/GameState';
import LogoutOutlined from '@/components/icons/LogoutOutlined.vue';
import SpecieZhDiv from '@/components/SpecieZhDiv.vue';
import { checkUsername } from '@/interfaces/UserState';
import { pubMsg } from '@/utils/general';

const props = defineProps<{
  rooms: RoomList;
  username: string;
  switchPage: (page: string) => void;
  currentRoom: string;
  setCurrentRoom: (room: string) => void;
  logout: () => void;
}>();

const currentView = ref('list');
const chosenSpecie = ref('');
const newRoomName = ref('');
const endRoundInput = ref(6);
const botId = ref('');
const botSpecie = ref('');

// --- Helper Functions (Logic identical to original) ---
const isBot = (name: string) => {
  const room = props.rooms[props.currentRoom];
  return room.bots && room.bots.includes(name);
};
const removeBot = (botName: string) => socket.emit('remove-bot', { room_name: props.currentRoom, bot_id: botName });
const addBot = () => {
  if (!checkUsername(botId.value)) {
    pubMsg('错误！', '机器人ID必须在3到16个字符之间！', 'error', 2);
    return;
  }
  socket.emit('add-bot', { username: props.username, room_name: props.currentRoom, bot_id: botId.value, specie: botSpecie.value });
  botId.value = ''; botSpecie.value = '';
};
const roomIsFull = (room_name: string) => Object.keys(props.rooms[room_name].players).length >= props.rooms[room_name].max_players;
const logout = () => { props.logout(); props.switchPage('home'); }
const getRoomType = (room_name: string) => {
  if (meInRoom(room_name)) return 'room-joined';
  if (!roomIsFull(room_name)) return 'room-available';
  return 'room-full';
};
const getRoomStatusType = (room: any) => {
    if (room.game_state === 'playing') return 'error';
    if (Object.keys(room.players).length >= room.max_players) return 'warning';
    return 'success';
}
const getRoomStatusText = (room: any) => {
    if (room.game_state === 'playing') return '游戏中';
    if (Object.keys(room.players).length >= room.max_players) return '满员';
    return '可加入';
}
const specieChosen = (room_name: string) => props.rooms[room_name].players[props.username].specie;
const meInRoom = (room_name: string) => props.rooms[room_name].players[props.username] !== undefined;
const isAgreed = (room_name: string) => props.rooms[room_name].players[props.username].agreed;
const switchView = (view: string, room_name: string) => {
  currentView.value = view;
  props.setCurrentRoom(room_name);
  if (props.rooms[room_name].players[props.username].specie) {
    chosenSpecie.value = props.rooms[room_name].players[props.username].specie;
  }
  if (meInRoom(room_name) && view === 'room' && props.rooms[room_name].game_state === 'playing') {
    socket.emit('get-game-state', { username: props.username, room_name: room_name });
  }
};
const deleteRoom = (roomName: string) => socket.emit('delete-room', { room_name: roomName });
socket.on('game-state', (data: {state: GameState}) => {
  if (data.state.room_name === props.currentRoom) props.switchPage('game');
});
const createRoom = (room_name: string) => {
  room_name = room_name.trim();
  if (room_name.length < 3 || room_name.length > 16) {
    pubMsg('错误！', '房间名长度必须在3到16个字符之间', 'error', 2);
    return;
  }
  socket.emit('create-room', { username: props.username, room_name: room_name });
  newRoomName.value = '';
};
const enterRoom = () => socket.emit('enter-room', { username: props.username, room_name: props.currentRoom });
const leaveRoom = () => socket.emit('leave-room', { username: props.username, room_name: props.currentRoom });
const agreeToStart = () => socket.emit('agree-to-start', { username: props.username, room_name: props.currentRoom });
const disagreeToStart = () => socket.emit('disagree-to-start', { username: props.username, room_name: props.currentRoom });
const submitSpecieChoice = () => socket.emit('choose-specie', { username: props.username, room_name: props.currentRoom, specie: chosenSpecie.value });
const setEndRound = () => socket.emit('set-end-round', { username: props.username, room_name: props.currentRoom, end_round: endRoundInput.value });
const getSpecieSelectOptions = () => {
  const res: Array<SelectOption | SelectGroupOption> = [];
  for (const specie of species) {
    let otherPlayerSelected = false;
    for (const player in props.rooms[props.currentRoom].players) {
      if (props.rooms[props.currentRoom].players[player].specie === specie) {
        otherPlayerSelected = true;
        break;
      }
    }
    const myCurrent = props.rooms[props.currentRoom].players[props.username]?.specie;
    if (!otherPlayerSelected || specie === myCurrent) {
      res.push( { label: getSpecieZhName(specie), value: specie, style: { fontWeight: 'bold', color: getSpecieColor(specie) } });
    }
  }
  return res;
};
</script>

<style scoped>
/* === 1. 基础布局 === */
.lobby-page {
  position: relative;
  height: 100vh;
  width: 100vw;
  /* 背景图设置 */
  background-image: url('/images/lobby-bg.webp');
  background-size: cover;
  background-position: center;
  /* Flex布局：顶栏固定，内容撑满 */
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* === 2. 通用 Glassmorphism (毛玻璃) 样式 === */
.glass-panel {
  background: rgba(255, 255, 255, 0.8); /* 半透明白 */
  backdrop-filter: blur(12px); /* 模糊背景 */
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

/* 如果是深色背景图，可以用深色毛玻璃:
.glass-panel.dark {
    background: rgba(30, 30, 30, 0.6);
    color: #fff;
} 
*/

/* 导航栏 */
.lobby-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 60px;
  flex-shrink: 0;
  z-index: 10;
}
.app-title { font-size: 1.25rem; font-weight: 800; color: #333; margin: 0; }
.nav-right { display: flex; align-items: center; gap: 12px; }

/* 内容容器 */
.view-content {
  flex: 1;
  padding: 20px;
  overflow: hidden; /* 防止最外层滚动，让内部滚动 */
  position: relative;
}
.view-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* === 3. 房间列表视图 (List View) === */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}
.action-title { font-weight: bold; font-size: 1.1em; color: #444; }
.create-room-group { width: 300px; }

.room-grid-wrapper {
  flex: 1;
  overflow-y: auto; /* 仅网格区域滚动 */
  padding-right: 5px; /* 滚动条间距 */
}

.room-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding-bottom: 20px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  border-radius: 12px;
  color: #666;
  font-size: 1.1rem;
}

/* 房间卡片样式微调 */
.glass-card {
  background: rgba(255, 255, 255, 0.55); /* 比面板稍微透明一点 */
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 12px;
  transition: transform 0.2s, background 0.2s, box-shadow 0.2s;
}
.glass-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.75);
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}
.room-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.room-name-text { font-weight: bold; font-size: 1.1rem; color: #333; }
.room-details { font-size: 0.9rem; color: #555; }
.detail-item { display: flex; justify-content: space-between; margin-bottom: 4px; }
.card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.state-text { font-size: 0.85rem; color: #888; }
.text-gray { color: #999; }

/* 房间状态边框颜色 (可选增强视觉) */
.room-joined { border-left: 4px solid #2080f0; }
.room-available { border-left: 4px solid #18a058; }
.room-full { border-left: 4px solid #d03050; }

/* === 4. 房间详情视图 (Room View) === */
.room-header {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  border-radius: 12px;
  margin-bottom: 15px;
  flex-shrink: 0;
}
.room-title { font-size: 1.3rem; font-weight: bold; color: #222; margin: 0 10px; }
.room-subtitle { color: #666; }

.room-content-split {
  flex: 1;
  display: flex;
  gap: 20px;
  overflow: hidden; /* 内部面板各自滚动 */
}

/* 左侧面板 */
.left-panel {
  flex: 1; /* 占据剩余宽度 */
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  min-width: 0; /* 防止flex子元素溢出 */
}

/* 右侧面板 */
.right-panel {
  width: 320px; /* 固定宽度 */
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.panel-title {
  padding: 15px 20px;
  font-size: 1.1rem;
  font-weight: bold;
  border-bottom: 1px solid rgba(0,0,0,0.05);
  color: #444;
}

/* 玩家列表滚动区 */
.player-list-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
}

.player-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255,255,255,0.4);
  margin-bottom: 8px;
  padding: 12px 15px;
  border-radius: 8px;
  border: 1px solid transparent;
}
.player-item.me-item { background: rgba(32, 128, 240, 0.1); border-color: rgba(32, 128, 240, 0.2); }
.player-item.bot-item { background: rgba(0,0,0,0.03); border: 1px dashed rgba(0,0,0,0.1); }

.p-info { display: flex; flex-direction: column; }
.p-name { font-weight: bold; font-size: 1rem; color: #333; display: flex; align-items: center; }
.p-specie { font-size: 0.85rem; margin-top: 2px; }
.ml-1 { margin-left: 6px; }

/* 右侧控制区 */
.controls-wrapper {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}
.control-group { margin-bottom: 20px; }
.group-label { font-size: 0.9rem; color: #666; margin-bottom: 6px; }
.spacer { flex: 1; }

/* 动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>