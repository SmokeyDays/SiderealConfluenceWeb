<template>
  <div class="lobby-page">
    <div v-if="currentView === 'list'" class="room-list">
      <n-card v-for="(room, index) in rooms" :key="index" class="room-item" :class="getRoomType(room.name)" @click="switchView('room', room.name)" hoverable>
        <h3 class="room-name">{{ room.name }}</h3>
        <p class="room-info">Players: {{ Object.keys(room.players).length }} / {{ room.max_players }}</p>
        <p class="room-info">Game State: {{ room.game_state }}</p>
        <template v-if="meInRoom(room.name)">
          <template v-if="props.rooms[room.name].players[props.username].spice">
            <p class="room-info">Playing <span class="spice" :style="{ color: getSpiceColor(props.rooms[room.name].players[props.username].spice) }">{{ props.rooms[room.name].players[props.username].spice }}</span></p>
          </template>
          <template v-else>
            <p class="room-info">No spice selected</p>
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
          <p>{{ name }} - <span class="spice" :style="{ color: getSpiceColor(info.spice) }">{{ info.spice ? info.spice : 'No spice chosen' }}</span></p>
        </div>
        <div class="room-actions">
          <n-button class="enter-room-btn" @click="enterRoom">Enter Room</n-button>
          <template v-if="meInRoom(currentRoom)">
            <n-button class="leave-room-btn" @click="leaveRoom">Leave Room</n-button>
            <n-button class="agree-start-btn" @click="agreeToStart">Agree to Start Game</n-button>
            <n-select v-model:value="chosenSpice" :options="spices" placeholder="Choose a spice" />
            <n-button class="submit-spice-btn" @click="submitSpiceChoice">Submit Spice Choice</n-button>
          </template>
          <n-button class="back-list-btn" @click="switchView('list', '')">Back to List</n-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NSpace, NSelect, NInput, NCard } from 'naive-ui';
import type { RoomList } from '../interfaces/RoomState';
import { socket } from '@/utils/connect';
import { getSpiceColor } from '@/interfaces/SpiceConfig';
const props = defineProps<{
  rooms: RoomList;
  username: string;
}>();

const currentView = ref('list');
const currentRoom = ref('');
const chosenSpice = ref('');
const newRoomName = ref('');

const getRoomType = (room_name: string) => {
  if (meInRoom(room_name)) {
    return 'blue-room';
  }
  if (Object.keys(props.rooms[room_name].players).length < props.rooms[room_name].max_players) {
    return 'green-room';
  }
  return 'red-room';
};

const meInRoom = (room_name: string) => {
  return props.rooms[room_name].players[props.username] !== undefined;
};

const switchView = (view: string, room_name: string) => {
  currentView.value = view;
  currentRoom.value = room_name;
  if (props.rooms[room_name].players[props.username].spice) {
    chosenSpice.value = props.rooms[room_name].players[props.username].spice;
  }
};

const createRoom = (room_name: string) => {
  room_name = room_name.trim();
  if (room_name.length < 3 || room_name.length > 16) {
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

const submitSpiceChoice = () => {
  socket.emit('choose-spice', { username: props.username, room_name: currentRoom.value, spice: chosenSpice.value });
};

const spices = [
  { label: 'Kylion', value: 'Kylion' },
  { label: 'Zeth', value: 'Zeth' },
  { label: 'Icarus', value: 'Icarus' },
];

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
.submit-spice-btn,
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

.spice {
  font-weight: bold;
}
</style>
