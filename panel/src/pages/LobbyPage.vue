<template>
  <div class="lobby-page">
    <div v-if="currentView === 'list'" class="room-list">
      <n-card v-for="(room, index) in rooms" :key="index" class="room-item" @click="switchView('room', room.name)" hoverable>
        <h3 class="room-name">{{ room.name }}</h3>
        <p class="room-info">Players: {{ Object.keys(room.players).length }}</p>
        <p class="room-info">Game State: {{ room.game_state }}</p>
      </n-card>
      <n-space vertical class="create-room-section">
        <h3>Create Room</h3>
        <n-input v-model:value="newRoomName" placeholder="Enter room name" @keyup.enter="createRoom(newRoomName)" />
        <n-button @click="createRoom(newRoomName)">Create Room</n-button>
      </n-space>
    </div>

    <div v-if="currentView === 'room'" class="room-view">
      <h3 class="room-title">{{ currentRoom }}</h3>
      <div class="room-content">
        <div v-for="(info, name) in props.rooms[currentRoom].players" :key="name" class="player-info">
          <p>{{ name }} - {{ info.spice ? info.spice : 'No spice chosen' }}</p>
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

const props = defineProps<{
  rooms: RoomList;
  username: string;
}>();

const currentView = ref('list');
const currentRoom = ref('');
const chosenSpice = ref('');
const newRoomName = ref('');

const meInRoom = (room_name: string) => {
  return props.rooms[room_name].players[props.username] !== undefined;
};

const switchView = (view: string, room_name: string) => {
  currentView.value = view;
  currentRoom.value = room_name;
};

const createRoom = (room_name: string) => {
  room_name = room_name.trim();
  if (room_name.length < 3 || room_name.length > 16) {
    return;
  }
  socket.emit('create-room', { username: props.username, room_name: room_name });
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
</style>
