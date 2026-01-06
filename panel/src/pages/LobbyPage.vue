<template>
  <div class="lobby-page">
    <header class="lobby-navbar scifi-panel bottom-border-only">
      <div class="nav-left">
        <div class="deco-block"></div>
        <h3 class="app-title">游戏大厅</h3>
      </div>
      <div class="nav-right">
        <span class="welcome-text">
          玩家: <span class="highlight">{{ props.username }}</span>
        </span>
        <div class="v-sep"></div>
        <n-button size="small" secondary type="error" @click="logout" class="logout-btn">
          <template #icon><n-icon><LogoutOutlined /></n-icon></template>
          退出登录
        </n-button>
      </div>
    </header>

    <main class="view-content">
      <transition name="fade" mode="out-in">
        
        <div v-if="currentView === 'list'" class="view-container list-view" key="list">
          
          <div class="scifi-panel action-bar">
             <div class="action-title">
               <span class="icon">>></span> 房间列表
             </div>
             <n-input-group class="create-room-group">
                <n-input 
                  v-model:value="newRoomName" 
                  placeholder="新房间 ID..." 
                  @keyup.enter="createRoom(newRoomName)" 
                />
                <n-button type="primary" secondary @click="createRoom(newRoomName)">
                  新建房间
                </n-button>
             </n-input-group>
          </div>

          <div class="room-grid-wrapper custom-scrollbar">
             <div v-if="Object.keys(rooms).length === 0" class="empty-state">
               <div class="scan-line"></div>
               <div class="empty-text">NO SIGNAL DETECTED<br/><span class="sub">Initialize new sector to proceed</span></div>
             </div>
             
             <div class="room-grid" v-else>
                <div 
                  v-for="(room, index) in rooms" 
                  :key="index" 
                  class="room-card-container"
                  :class="getRoomType(room.name)" 
                  @click="switchView('room', room.name)" 
                >
                  <div class="room-card-inner">
                    <div class="status-strip"></div>
                    <div class="card-content">
                      <div class="card-header">
                        <span class="room-id">{{ room.name }}</span>
                        <div class="status-indicator">
                           <div class="led" :class="getRoomStatusType(room)"></div>
                        </div>
                      </div>
                      
                      <div class="card-body">
                         <div class="data-row">
                           <span class="label">玩家数</span>
                           <span class="value">{{ Object.keys(room.players).length }} / {{ room.max_players }}</span>
                         </div>
                         <div class="data-row">
                           <span class="label">最大轮数</span>
                           <span class="value">{{ room.end_round }}</span>
                         </div>
                         <div class="data-row role-row" v-if="meInRoom(room.name)">
                            <span class="label">种族</span>
                            <SpecieZhDiv 
                              v-if="props.rooms[room.name].players[props.username].specie" 
                              :specie="props.rooms[room.name].players[props.username].specie" 
                              :is-me="false" 
                              is-span 
                            />
                            <span v-else class="text-dim">PENDING...</span>
                         </div>
                      </div>

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
                    </div>
                  </div>
                </div>
             </div>
          </div>
        </div>

        <div v-else class="view-container room-view" key="room">
          <div class="scifi-panel room-header">
             <n-button text @click="switchView('list', '')" class="back-btn">
                &lt; 返回大厅
             </n-button>
             <div class="v-sep"></div>
             <span class="room-title">房间: {{ props.currentRoom }}</span>
             <span class="room-subtitle"> // 人数限制: {{ Object.keys(props.rooms[props.currentRoom].players).length }}/{{ props.rooms[props.currentRoom].max_players }}</span>
          </div>

          <div class="room-content-split">
             <div class="left-panel scifi-panel">
                <div class="panel-header">
                  <div class="deco-square"></div>
                  玩家列表
                </div>
                <div class="player-list-scroll custom-scrollbar">
                   <div 
                      v-for="(info, name) in props.rooms[props.currentRoom].players" 
                      :key="name" 
                      class="player-item"
                      :class="{ 'bot-item': isBot(name), 'me-item': name === props.username }"
                    >
                      <div class="corner-mark"></div>
                      
                      <div class="p-main">
                        <div class="p-id">
                          {{ name }}
                          <span v-if="isBot(name)" class="tag bot">AI</span>
                          <span v-if="name === props.username" class="tag me">YOU</span>
                        </div>
                        <div class="p-specie">
                           种族: 
                           <span :style="{ color: info.specie ? getSpecieColor(info.specie) : 'var(--scifi-text-dim)' }">
                             {{ info.specie ? getSpecieZhName(info.specie) : 'NULL' }}
                           </span>
                        </div>
                      </div>
                      
                      <div class="p-status">
                         <div class="status-box" :class="info.agreed ? 'ready' : 'pending'">
                           {{ info.agreed ? '准备开始' : '等待中...' }}
                         </div>
                         <n-popconfirm v-if="isBot(name)" @positive-click="removeBot(name)">
                            <template #trigger>
                              <n-button size="tiny" type="error" secondary class="del-bot-btn">移除 Bot</n-button>
                            </template>
                            Terminate AI Unit?
                         </n-popconfirm>
                      </div>
                   </div>
                </div>
             </div>

             <div class="right-panel scifi-panel">
                <div class="panel-header">
                  <div class="deco-square warning"></div>
                  控制面板
                </div>
                <div class="controls-wrapper custom-scrollbar">
                   
                   <div v-if="!meInRoom(props.currentRoom)" class="join-box">
                      <n-button type="primary" block size="large" secondary
                        @click="enterRoom" 
                        :disabled="roomIsFull(props.currentRoom) || props.rooms[props.currentRoom].game_state === 'playing'">
                        加入房间
                      </n-button>
                   </div>

                   <template v-else>
                      <div class="control-group">
                         <div class="group-label">种族选择</div>
                         <n-input-group>
                           <n-select 
                             v-model:value="chosenSpecie" 
                             :options="getSpecieSelectOptions()" 
                             placeholder="选择..." 
                             :disabled="isAgreed(props.currentRoom)"
                           />
                           <n-button type="primary" ghost @click="submitSpecieChoice" :disabled="isAgreed(props.currentRoom)">确定</n-button>
                         </n-input-group>
                      </div>

                      <div class="control-group main-btn-group">
                         <n-button 
                           v-if="isAgreed(props.currentRoom)" 
                           type="warning" block size="large" secondary dashed
                           @click="disagreeToStart"
                         >
                           CANCEL READY
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
                      
                      <div class="h-sep"></div>

                      <div class="control-group">
                         <div class="group-label"> 游戏轮数 <span class="text-dim"> [当前: {{ props.rooms[props.currentRoom].end_round }}]</span></div>
                         <n-input-group size="small">
                            <n-input-number v-model:value="endRoundInput" :min="1" style="flex:1"/>
                            <n-button ghost @click="setEndRound">设置</n-button>
                         </n-input-group>
                      </div>

                      <div class="control-group" v-if="Object.keys(props.rooms[props.currentRoom].players).length < props.rooms[props.currentRoom].max_players">
                         <div class="group-label">添加 BOT</div>
                         <n-space vertical size="small">
                            <n-input v-model:value="botId" placeholder="BOT ID" size="small"/>
                            <n-select v-model:value="botSpecie" :options="getSpecieSelectOptions()" placeholder="种族" size="small"/>
                            <n-button dashed block size="small" type="info" @click="addBot">添加</n-button>
                         </n-space>
                      </div>

                      <div class="spacer"></div>
                      
                      <n-button type="error" ghost block @click="leaveRoom" class="leave-btn">
                        退出房间
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
import { ref } from 'vue';
import { 
  NButton, NSpace, NSelect, NInput, NInputNumber, NIcon, NInputGroup, NPopconfirm,
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

// --- Helpers ---
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
    if (room.game_state === 'playing') return 'active'; // CSS class
    if (Object.keys(room.players).length >= room.max_players) return 'full';
    return 'open';
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
/* 引入全局科幻变量 (假设 main.css 已定义) */

.lobby-page {
  position: relative;
  height: 100vh;
  width: 100vw;
  /* 移除图片背景，透出 App.vue 的网格背景 */
  background: transparent;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* === Scifi Panel System === */
.scifi-panel {
  background: var(--scifi-card-bg);
  border: 1px solid var(--scifi-border);
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
  /* 去圆角，硬朗风格 */
  border-radius: 0; 
}
.scifi-panel.bottom-border-only {
  background: rgba(5, 10, 20, 0.9);
  border: none;
  border-bottom: 2px solid var(--scifi-primary);
}

/* === Navbar === */
.lobby-navbar {
  height: 60px;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 10;
}
.deco-block {
  width: 10px;
  height: 20px;
  background: var(--scifi-primary);
  margin-right: 10px;
  display: inline-block;
}
.app-title {
  display: inline-block;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 2px;
  font-size: 1.2rem;
  color: var(--scifi-text);
  margin: 0;
}
.nav-right {
  display: flex;
  align-items: center;
  gap: 15px;
  font-family: 'Share Tech Mono', monospace;
}
.highlight {
  color: var(--scifi-primary);
  text-shadow: 0 0 5px var(--scifi-primary);
}
.v-sep {
  width: 1px;
  height: 20px;
  background: var(--scifi-border);
}

/* === Content === */
.view-content {
  flex: 1;
  padding: 20px;
  overflow: hidden;
  position: relative;
}
.view-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* === List View === */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  margin-bottom: 20px;
  /* 装饰切角 */
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%);
}
.action-title {
  font-family: 'Orbitron', sans-serif;
  color: var(--scifi-text);
  font-size: 1.1rem;
}
.action-title .icon {
  color: var(--scifi-primary);
  margin-right: 5px;
}
.create-room-group { width: 320px; }

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 300px;
  border: 1px dashed var(--scifi-border);
  color: var(--scifi-text-dim, #777);
  background: rgba(0,0,0,0.2);
}
.scan-line {
  width: 100%;
  height: 2px;
  background: var(--scifi-primary);
  animation: scan 2s infinite linear;
  opacity: 0.5;
  margin-bottom: 20px;
}
@keyframes scan { 0% { transform: translateY(-20px); opacity: 0; } 50% { opacity: 1; } 100% { transform: translateY(20px); opacity: 0; } }
.empty-text { text-align: center; font-family: 'Share Tech Mono', monospace; font-size: 1.2rem; }
.empty-text .sub { font-size: 0.8rem; color: #555; }

/* Room Grid */
.room-grid-wrapper {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
}
.room-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding-bottom: 20px;
}

/* === Sci-Fi Room Card === */
.room-card-container {
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}
.room-card-container:hover {
  transform: translateY(-2px);
}
.room-card-container:hover .room-card-inner {
  border-color: var(--scifi-primary);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.15);
}

/* Card Body */
.room-card-inner {
  background: rgba(10, 20, 30, 0.8);
  border: 1px solid var(--scifi-border);
  height: 100%;
  display: flex;
  /* 切角设计 */
  clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
}

/* Status Strip (Left Bar) */
.status-strip {
  left: 0; top: 0; bottom: 0;
  width: 6px;
  background: #333;
  margin-right: 10px;
  transition: background 0.3s;
}
.room-joined .status-strip { 
  background: var(--scifi-primary); 
  box-shadow: 0 0 10px var(--scifi-primary); 
}
.room-available .status-strip { background: var(--scifi-success); }
.room-full .status-strip { background: var(--scifi-error); }

.card-content {
  flex: 1;
  padding: 12px 15px 12px 0;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  padding-bottom: 8px;
  margin-bottom: 8px;
}
.room-id {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.1rem;
  color: #fff;
}
/* LED Status Light */
.led { width: 8px; height: 8px; border-radius: 50%; background: #333; }
.led.active { background: var(--scifi-error); box-shadow: 0 0 5px var(--scifi-error); animation: blink 1s infinite; }
.led.full { background: var(--scifi-warning); }
.led.open { background: var(--scifi-success); box-shadow: 0 0 5px var(--scifi-success); }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

.card-body { flex: 1; font-size: 0.85rem; }
.data-row { display: flex; justify-content: space-between; margin-bottom: 4px; font-family: 'Share Tech Mono', monospace; }
.label { color: var(--scifi-text-dim, #666); }
.value { color: var(--scifi-text); }
.text-dim { color: #555; font-style: italic; }

.card-footer {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: var(--scifi-text-dim, #777);
  border-top: 1px dashed rgba(255,255,255,0.1);
  padding-top: 6px;
}

/* === Room View === */
.room-header {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  margin-bottom: 20px;
  font-family: 'Orbitron', sans-serif;
}
.back-btn { font-family: 'Share Tech Mono', monospace; font-weight: bold; }
.room-title { margin-left: 10px; font-size: 1.2rem; color: var(--scifi-primary); }
.room-subtitle { font-family: 'Share Tech Mono', monospace; font-size: 0.9rem; color: var(--scifi-text-dim); }

.room-content-split { flex: 1; display: flex; gap: 20px; overflow: hidden; }

/* Panels */
.panel-header {
  padding: 10px 15px;
  background: rgba(0, 212, 255, 0.05);
  border-bottom: 1px solid var(--scifi-border);
  font-family: 'Orbitron', sans-serif;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  color: var(--scifi-primary);
}
.deco-square { width: 8px; height: 8px; background: var(--scifi-primary); margin-right: 8px; }
.deco-square.warning { background: var(--scifi-warning); }

.left-panel { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.right-panel { width: 340px; display: flex; flex-direction: column; flex-shrink: 0; }

.player-list-scroll { flex: 1; overflow-y: auto; padding: 10px; }
.controls-wrapper { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; }

/* Player Item */
.player-item {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 5px;
  padding: 10px 15px;
}
.player-item.me-item {
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid var(--scifi-primary);
}
.player-item.bot-item {
  border-style: dashed;
  opacity: 0.8;
}
.corner-mark {
  position: absolute;
  top: 0; left: 0;
  width: 0; height: 0;
  border-top: 6px solid var(--scifi-border);
  border-right: 6px solid transparent;
}
.me-item .corner-mark { border-top-color: var(--scifi-primary); }

.p-id { font-family: 'Share Tech Mono', monospace; font-size: 1.1rem; color: #fff; display: flex; align-items: center; gap: 5px; }
.p-specie { font-size: 0.8rem; color: var(--scifi-text-dim); }

.tag { font-size: 0.6rem; padding: 1px 4px; background: #333; border-radius: 2px; }
.tag.bot { background: #1431d6; color: #e0e0e0; }
.tag.me { background: var(--scifi-primary); color: #9d3030; font-weight: bold; }

.status-box {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.7rem;
  padding: 2px 8px;
  border: 1px solid #444;
  color: #666;
}
.status-box.ready {
  border-color: var(--scifi-success);
  color: var(--scifi-success);
  box-shadow: 0 0 5px rgba(0, 255, 157, 0.2);
}
.status-box.pending {
  border-color: var(--scifi-warning);
  color: var(--scifi-warning);
}
.del-bot-btn { margin-left: 10px; }

/* Right Controls */
.control-group { margin-bottom: 20px; }
.group-label { font-family: 'Orbitron', sans-serif; font-size: 0.8rem; margin-bottom: 5px; color: var(--scifi-text); }
.h-sep { height: 1px; background: var(--scifi-border); margin: 20px 0; opacity: 0.5; }
.spacer { flex: 1; }

.join-box { margin-top: auto; margin-bottom: auto; }

/* Transition */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>