<template>
  <div class="lobby-page">
    <div v-if="currentView === 'list'" class="room-list">
      <n-card v-for="(room, index) in rooms" :key="index" class="room-item" :class="getRoomType(room.name)" @click="switchView('room', room.name)" hoverable>
        <h3 class="room-name">{{ room.name }}</h3>
        <p class="room-info">Players: {{ Object.keys(room.players).length }} / {{ room.max_players }}</p>
        <p class="room-info">Game State: {{ room.game_state }}</p>
        <template v-if="meInRoom(room.name)">
          <template v-if="props.rooms[room.name].players[props.username].specie">
            <p class="room-info">Playing <span class="specie" :style="{ color: getSpecieColor(props.rooms[room.name].players[props.username].specie) }">{{ props.rooms[room.name].players[props.username].specie }}</span></p>
          </template>
          <template v-else>
            <p class="room-info">No specie selected</p>
          </template>
        </template>
      </n-card>
      <n-space vertical class="create-room-section">
        <h3>Create Room</h3>
        <n-input v-model:value="newRoomName" placeholder="Enter room name" @keyup.enter="createRoom(newRoomName)" />
        <n-button @click="createRoom(newRoomName)">Create Room</n-button>
      </n-space>
    </div>

    <div v-if="currentView === 'room'" class="room-view">
      <h3 class="room-title">{{ currentRoom }} ({{ Object.keys(props.rooms[currentRoom].players).length }} / {{ props.rooms[currentRoom].max_players }})</h3>
      <div class="room-content">
        <div v-for="(info, name) in props.rooms[currentRoom].players" :key="name" class="player-info">
          <p>{{ name }} - <span class="specie" :style="{ color: getSpecieColor(info.specie) }">{{ info.specie ? info.specie : 'No specie chosen' }}</span>
            <template v-if="info.agreed">
              <span style="color: green; font-weight: bold;"> - √</span>
            </template>
            <template v-else>
              <span style="color: red; font-weight: bold"> - ×</span>
            </template>
          </p>
        </div>
        <div class="room-actions">
          <n-button class="enter-room-btn" @click="enterRoom" v-if="!meInRoom(currentRoom) && !roomIsFull(currentRoom)">Enter Room</n-button>
          <template v-if="meInRoom(currentRoom)">
            <n-button class="leave-room-btn" @click="leaveRoom">Leave Room</n-button>
            <template v-if="isAgreed(currentRoom)">
              <n-button class="agree-start-btn" @click="disagreeToStart">Disagree to Start Game</n-button>
            </template>
            <template v-else>
              <n-button class="agree-start-btn" @click="agreeToStart" v-if="specieChosen(currentRoom)">Agree to Start Game</n-button>
              <n-select v-model:value="chosenSpecie" :options="getSpecieSelectOptions()" placeholder="Choose a specie" />
              <n-button class="submit-specie-btn" @click="submitSpecieChoice">Submit specie Choice</n-button>
            </template> 
          </template>
          <n-button class="back-list-btn" @click="switchView('list', '')">Back to List</n-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NSpace, NSelect, NInput, NCard, type SelectGroupOption, type SelectOption } from 'naive-ui';
import type { RoomList } from '../interfaces/RoomState';
import { socket } from '@/utils/connect';
import { getSpecieColor, species } from '@/interfaces/GameConfig';
const props = defineProps<{
  rooms: RoomList;
  username: string;
  switchPage: (page: string) => void;
}>();

const currentView = ref('list');
const currentRoom = ref('');
const chosenSpecie = ref('');
const newRoomName = ref('');

const roomIsFull = (room_name: string) => {
  return Object.keys(props.rooms[room_name].players).length >= props.rooms[room_name].max_players;
};

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
  currentRoom.value = room_name;
  if (props.rooms[room_name].players[props.username].specie) {
    chosenSpecie.value = props.rooms[room_name].players[props.username].specie;
  }
  if (meInRoom(room_name) && view === 'room' && props.rooms[room_name].game_state === 'playing') {
    socket.emit('get-game-state', { username: props.username, room_name: room_name });
    props.switchPage('game');
  }
};

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
  socket.emit('enter-room', { username: props.username, room_name: currentRoom.value });
};

const leaveRoom = () => {
  socket.emit('leave-room', { username: props.username, room_name: currentRoom.value });
};

const agreeToStart = () => {
  socket.emit('agree-to-start', { username: props.username, room_name: currentRoom.value });
};

const disagreeToStart = () => {
  socket.emit('disagree-to-start', { username: props.username, room_name: currentRoom.value });
};

const submitSpecieChoice = () => {
  socket.emit('choose-specie', { username: props.username, room_name: currentRoom.value, specie: chosenSpecie.value });
};

const getSpecieSelectOptions = () => {
  const res: Array<SelectOption | SelectGroupOption> = [];
  for (const specie of species) {
    res.push( { label: specie, value: specie, style: { color: getSpecieColor(specie) } });
  }
  return res;
};

</script>

<style scoped>
.lobby-page {
  padding: 20px;
}

.room-list {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 20px;
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
  border: 1px solid #ddd;
  border-radius: 5px;
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
</style>
