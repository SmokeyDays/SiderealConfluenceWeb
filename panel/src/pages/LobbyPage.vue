<template>
  <div class="lobby-page">
    <div class="lobby-title">
      <h3>Welcome, {{ props.username }}</h3>
    </div>
    <div v-if="currentView === 'list'" class="room-list">
      <n-card v-for="(room, index) in rooms" :key="index" class="room-item" :class="getRoomType(room.name)" @click="switchView('room', room.name)" hoverable>
        <h3 class="room-name">{{ room.name }}</h3>
        <p class="room-info">Players: {{ Object.keys(room.players).length }} / {{ room.max_players }}</p>
        <p class="room-info">Game State: {{ room.game_state }}</p>
        <n-button v-if="Object.keys(room.players).length === 0" @click.stop="deleteRoom(room.name)" class="delete-room-btn">
          Delete Room
        </n-button>
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

    <div v-if="currentView === 'room'" class="room-view" style="max-width: 400px; margin: 0 auto;">
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
          <n-button class="enter-room-btn" @click="enterRoom" v-if="!meInRoom(currentRoom) && !roomIsFull(currentRoom) && props.rooms[currentRoom].game_state !== 'playing'">Enter Room</n-button>
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
            <div class="end-round-setting">
              <n-input-number v-model:value="endRound" placeholder="Enter end round (e.g., 5)" :min="1" />
              <n-button @click="setEndRound">Set End Round</n-button>
            </div>
          </template>
          <n-button class="back-list-btn" @click="switchView('list', '')">Back to List</n-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NSpace, NSelect, NInput, NInputNumber, NCard, type SelectGroupOption, type SelectOption } from 'naive-ui';
import type { RoomList } from '../interfaces/RoomState';
import { socket } from '@/utils/connect';
import { getSpecieColor, species } from '@/interfaces/GameConfig';
import type { GameState } from '@/interfaces/GameState';
const props = defineProps<{
  rooms: RoomList;
  username: string;
  switchPage: (page: string) => void;
}>();

const currentView = ref('list');
const currentRoom = ref('');
const chosenSpecie = ref('');
const newRoomName = ref('');
const endRound = ref(5);

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
  }
};

const deleteRoom = (roomName: string) => {
  socket.emit('delete-room', { room_name: roomName });
};

socket.on('game-state', (data: {state: GameState}) => {
  if (data.state.room_name === currentRoom.value) {
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

const setEndRound = () => {
  socket.emit('set-end-round', { username: props.username, room_name: currentRoom.value, end_round: endRound.value });
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
