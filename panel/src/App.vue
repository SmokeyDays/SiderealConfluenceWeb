<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import { NButton, NSpace } from 'naive-ui';
import HomePage from '@/pages/HomePage.vue';
import GamePage, { type GameProps } from '@/pages/GamePage.vue';
import LobbyPage from '@/pages/LobbyPage.vue';
import AlertList from '@/components/AlertList.vue';
import { socket } from '@/utils/connect';
import type { GameState } from './interfaces/GameState';
import type { RoomList } from './interfaces/RoomState';
import Logo from '@/components/Logo.vue';
import { isProduction } from './utils/config';
const rooms = ref<RoomList>({});
const displayPage = ref('home');
const username = ref(isProduction? '': 'Alice');

const switchPage = (page: string) => {
  displayPage.value = page;
};

const gameProps = ref({
  scaleFactor: 100,
  offsetX: 0,
  offsetY: 0,
});

const gameState = ref<GameState>({
  players: [],
  current_round: 0,
  stage: '',
  room_name: '',
  research_bid_cards: [],
  colony_bid_cards: [],
  current_pick: {
    type: '',
    player: ''
  },
  current_discard_colony_player: ''
});

socket.on('game-state', (data: {state: GameState}) => {
  gameState.value = data.state;
  console.log(data);
});

socket.on('room-list', (data: {rooms: RoomList}) => {
  rooms.value = data.rooms;
  console.log(data);
});

function checkUsername(newUsername: string) {
  if (newUsername.trim() === '') {
    return false;
  }
  // length must be between 3 and 16
  if (newUsername.length < 3 || newUsername.length > 16) {
    return false;
  }
  return true;
}

const updateGameProps = (newProps: GameProps) => {
  gameProps.value = newProps;
};

const submitUsername = (newUsername: string) => {
  if (checkUsername(newUsername)) {
    socket.emit('login',{username: newUsername, oldname: username.value});
  } else {
    PubSub.publish('alert-pubsub-message', {
      title: '错误！',
      str: '用户名格式不正确！',
      type: 'error',
      dur: 2,
      visible: true,
    });
  }
};

socket.on('login-success', (data: any) => {
  username.value = data['username'];
  PubSub.publish('alert-pubsub-message', {
    title: '登录成功！',
    str: '欢迎！ ' + username.value,
    type: 'success',
    dur: 2,
    visible: true,
  });
  switchPage('lobby');
});

onMounted(() => {
  PubSub.publish('alert-pubsub-message', {
    title: '欢迎！',
    str: '客户端启动成功！',
    type: 'success',
    dur: 2,
    visible: true,
  });
  socket.emit('get-room-list');
})

onUnmounted(() => {
  if (username.value !== '') {
    socket.emit('logout', {username: username.value});
  }
})
</script>

<template>
  <div class="app">
    <template v-if="displayPage === 'home'">
      <HomePage :submitUsername="submitUsername" />
    </template>
    <template v-else-if="displayPage === 'game'">
      <GamePage :gameProps="gameProps" :updateGameProps="updateGameProps" :username="username" :gameState="gameState" :switchPage="switchPage"/>
    </template>
    <template v-else-if="displayPage === 'lobby'">
      <LobbyPage :rooms="rooms" :username="username" :switchPage="switchPage" />
    </template>
    <AlertList/>
  </div>
</template>

<style scoped>
.app {
  font-family: Arial, sans-serif;
}

</style>