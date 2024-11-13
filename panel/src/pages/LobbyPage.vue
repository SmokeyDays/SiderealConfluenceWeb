<template>
  <div class="lobby-page">
    <div class="lobby-title">
      <h3>欢迎, {{ props.username }}</h3>
      
    </div>
    <div v-if="currentView === 'list'" class="room-list">
      <n-card v-for="(room, index) in rooms" :key="index" class="room-item" :class="getRoomType(room.name)" @click="switchView('room', room.name)" hoverable>
        <h3 class="room-name">{{ room.name }}</h3>
        <p class="room-info">玩家: {{ Object.keys(room.players).length }} / {{ room.max_players }}</p>
        <p class="room-info">游戏状态: {{ room.game_state }}</p>
        <n-button v-if="Object.keys(room.players).length === 0" @click.stop="deleteRoom(room.name)" class="delete-room-btn">
          删除房间
        </n-button>
        <template v-if="meInRoom(room.name)">
          <template v-if="props.rooms[room.name].players[props.username].specie">
            <p class="room-info">进行中 <span class="specie" :style="{ color: getSpecieColor(props.rooms[room.name].players[props.username].specie) }">{{ props.rooms[room.name].players[props.username].specie }}</span></p>
          </template>
          <template v-else>
            <p class="room-info">未选择种族</p>
          </template>
        </template>
      </n-card>
      <n-space vertical class="create-room-section">
        <h3>创建房间</h3>
        <n-input v-model:value="newRoomName" placeholder="输入房间名" @keyup.enter="createRoom(newRoomName)" />
        <n-button @click="createRoom(newRoomName)">创建房间</n-button>
      </n-space>
    </div>

    <div v-if="currentView === 'room'" class="room-view" style="max-width: 400px; margin: 0 auto;">
      <h3 class="room-title">{{ props.currentRoom }} ({{ Object.keys(props.rooms[props.currentRoom].players).length }} / {{ props.rooms[props.currentRoom].max_players }})</h3>
      <div class="room-content">
        <div v-for="(info, name) in props.rooms[props.currentRoom].players" :key="name" class="player-info">
          <p>{{ name }} - <span class="specie" :style="{ color: getSpecieColor(info.specie) }">{{ info.specie ? getSpecieZhName(info.specie) : '未选择种族' }}</span>
            <template v-if="info.agreed">
              <span style="color: green; font-weight: bold;"> - √</span>
            </template>
            <template v-else>
              <span style="color: red; font-weight: bold"> - ×</span>
            </template>
          </p>
        </div>
        <div class="room-actions">
          <n-button class="enter-room-btn" @click="enterRoom" v-if="!meInRoom(props.currentRoom) && !roomIsFull(props.currentRoom) && props.rooms[props.currentRoom].game_state !== 'playing'">进入房间</n-button>
          <template v-if="meInRoom(props.currentRoom)">
            <n-button class="leave-room-btn" @click="leaveRoom">离开房间</n-button>
            <template v-if="isAgreed(props.currentRoom)">
              <n-button class="agree-start-btn" @click="disagreeToStart">取消准备</n-button>
            </template>
            <template v-else>
              <n-button class="agree-start-btn" @click="agreeToStart" v-if="specieChosen(props.currentRoom)">准备</n-button>
              <n-select v-model:value="chosenSpecie" :options="getSpecieSelectOptions()" placeholder="选择一个种族" />
              <n-button class="submit-specie-btn" @click="submitSpecieChoice">提交种族选择</n-button>
            </template> 
            <div class="end-round-setting">
              <n-input-number v-model:value="endRound" placeholder="Enter end round (e.g., 5)" :min="1" />
              <n-button @click="setEndRound">设置结束回合</n-button>
            </div>
          </template>
          <n-button class="back-list-btn" @click="switchView('list', '')">返回房间列表</n-button>
        </div>
      </div>
    </div>
    <n-float-button @click="logout" top="20" right="20" size="large" type="default">
      <n-icon>
        <LogoutOutlined />
      </n-icon>
    </n-float-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NSpace, NSelect, NInput, NInputNumber, NCard, NFloatButton, NIcon, type SelectGroupOption, type SelectOption } from 'naive-ui';
import type { RoomList } from '../interfaces/RoomState';
import { socket } from '@/utils/connect';
import { getSpecieColor, getSpecieZhName, species } from '@/interfaces/GameConfig';
import type { GameState } from '@/interfaces/GameState';
import LogoutOutlined from '@/components/icons/LogoutOutlined.vue';

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
const endRound = ref(6);

const roomIsFull = (room_name: string) => {
  return Object.keys(props.rooms[room_name].players).length >= props.rooms[room_name].max_players;
};

const logout = () => {
  props.logout();
  props.switchPage('home');
}

const getRoomType = (room_name: string) => {
  if (meInRoom(room_name)) {
    return 'blue-room';
  }
  if (!roomIsFull(room_name)) {
    return 'green-room';
  }
  return 'red-room';
};

const specieChosen = (room_name: string) => {
  return props.rooms[room_name].players[props.username].specie;
};

const meInRoom = (room_name: string) => {
  return props.rooms[room_name].players[props.username] !== undefined;
};

const isAgreed = (room_name: string) => {
  return props.rooms[room_name].players[props.username].agreed;
};

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

const deleteRoom = (roomName: string) => {
  socket.emit('delete-room', { room_name: roomName });
};

socket.on('game-state', (data: {state: GameState}) => {
  if (data.state.room_name === props.currentRoom) {
    props.switchPage('game');
  }
});

const createRoom = (room_name: string) => {
  room_name = room_name.trim();
  if (room_name.length < 3 || room_name.length > 16) {PubSub.publish('alert-pubsub-message', {
      title: '错误！',
      str: '房间名长度必须在3到16个字符之间',
      type: 'error',
      dur: 2,
      visible: true,
    });
    return;
  }
  socket.emit('create-room', { username: props.username, room_name: room_name });
  newRoomName.value = '';
};

const enterRoom = () => {
  socket.emit('enter-room', { username: props.username, room_name: props.currentRoom });
};

const leaveRoom = () => {
  socket.emit('leave-room', { username: props.username, room_name: props.currentRoom });
};

const agreeToStart = () => {
  socket.emit('agree-to-start', { username: props.username, room_name: props.currentRoom });
};

const disagreeToStart = () => {
  socket.emit('disagree-to-start', { username: props.username, room_name: props.currentRoom });
};

const submitSpecieChoice = () => {
  socket.emit('choose-specie', { username: props.username, room_name: props.currentRoom, specie: chosenSpecie.value });
};

const setEndRound = () => {
  socket.emit('set-end-round', { username: props.username, room_name: props.currentRoom, end_round: endRound.value });
};

const getSpecieSelectOptions = () => {
  const res: Array<SelectOption | SelectGroupOption> = [];
  for (const specie of species) {
    res.push( { label: getSpecieZhName(specie), value: specie, style: { fontWeight: 'bold', color: getSpecieColor(specie) } });
  }
  return res;
};

</script>

<style scoped>
.lobby-title {
  margin-bottom: 20px;
  text-align: center;
}

.lobby-title h3 {
  color: #fff;
  font-size: 2rem;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
  background-color: rgba(0, 0, 0, 0.5);
  padding: 10px 20px;
  border-radius: 8px;
  display: inline-block;
}

.lobby-page {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  background-image: url('/images/lobby-bg.webp');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  min-height: 100vh;
  width: 100vw;
  margin: 0;
}

body, html {
  margin: 0;
  padding: 0;
  width: 100vw;
  overflow-x: hidden;
}

.room-list {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
}

.room-item {
  width: 200px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  cursor: pointer;
}

.room-name {
  font-size: 20px;
  font-weight: bold;
}

.room-info {
  margin-bottom: 10px;
}

.create-room-section {
  width: 200px;
  padding: 10px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
}

.room-view {
  padding: 20px;
  background-color: #fff;
  border-radius: 5px;
}

.room-content {
}

.room-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
}

.player-info {
  margin-bottom: 10px;
}

.enter-room-btn,
.leave-room-btn,
.agree-start-btn,
.submit-specie-btn,
.back-list-btn {
  margin-top: 10px;
  margin-right: 10px;
}

.blue-room {
  border-color: blue;
}

.green-room {
  border-color: green;
}

.red-room {
  border-color: red;
}

.specie {
  font-weight: bold;
}

.delete-room-btn {
  margin-top: 10px;
  color: #ff4d4f;
  border-color: #ff4d4f;
}

</style>
