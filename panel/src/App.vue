<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import { NButton, NSpace, NFloatButton, NIcon, NBadge } from 'naive-ui';
import HomePage from '@/pages/HomePage.vue';
import GamePage, { type GameProps } from '@/pages/GamePage.vue';
import GamePureTextPage from '@/pages/GamePureTextPage.vue';
import LobbyPage from '@/pages/LobbyPage.vue';
import AlertList from '@/components/AlertList.vue';
import { socket } from '@/utils/connect';
import type { GameState } from './interfaces/GameState';
import type { RoomList } from './interfaces/RoomState';
import Logo from '@/components/Logo.vue';
import { isProduction } from './utils/config';
import { messageEqual, type Message } from './interfaces/ChatState';
import ChatPanel from '@/components/panels/ChatPanel.vue';
import RulesPanel from '@/components/panels/RulesPanel.vue';
import { checkUsername, type Achievement } from './interfaces/UserState';
import AchievementPanel from './components/panels/AchievementPanel.vue';
import UtilsPanel from './components/panels/UtilsPanel.vue';

import IconChat from '@/components/icons/IconChat.vue';
import IconRules from '@/components/icons/IconRules.vue';
import Achievement3 from './components/icons/alerts/Achievement3.vue';
import IconUtils from './components/icons/IconUtils.vue';
import IconRobot from './components/icons/IconRobot.vue';
import { pubMsg } from './utils/general';

const rooms = ref<RoomList>({});
const displayPage = ref('home');
const username = ref(isProduction? '': 'Alice');
const messages = ref<Message[]>([]);
const currentRoom = ref('');
const displayPureText = ref(false);
const pureText = ref('');

const switchPage = (page: string) => {
  displayPage.value = page;
};

const switchPureTextMode = () => {
  displayPureText.value = !displayPureText.value;
};

const gameProps = ref({
  scaleFactor: 100,
  offsetX: 0,
  offsetY: 0,
});

const gameState = ref<GameState>({
  players: [],
  current_round: 0,
  end_round: 5,
  stage: '',
  room_name: '',
  research_bid_cards: [],
  colony_bid_cards: [],
  current_pick: {
    type: '',
    player: '',
    bid: 0
  },
  current_discard_colony_player: '',
  proposals: {},
  research_bid_priority: [],
  colony_bid_priority: [],
  Kajsjavikalimm_choose_split: null,
  favor_buff_in_game: false,
  faderan_relic_world_deck_size: 0
});

const setCurrentRoom = (room: string) => {
  currentRoom.value = room;
};

socket.on('game-state', (data: {state: GameState}) => {
  gameState.value = data.state;
  if (displayPureText.value) {
    socket.emit('query-prompt', {room_name: currentRoom.value, username: username.value});
  }
  console.log(data);
});

socket.on('room-list', (data: {rooms: RoomList}) => {
  rooms.value = data.rooms;
  console.log(data);
});


const updateGameProps = (newProps: GameProps) => {
  gameProps.value = newProps;
};

const submitUsername = (newUsername: string) => {
  if (checkUsername(newUsername)) {
    socket.emit('login',{username: newUsername, oldname: username.value});
  } else {
    pubMsg('错误！', '用户名格式不正确！','error', 2);
  }
};

const login = (newUsername: string) => {
  username.value = newUsername;
  localStorage.setItem('username', username.value);
}

socket.on('login-success', (data: any) => {
  login(data['username']);
  pubMsg('登录成功！', '欢迎！ ' + username.value, 'success', 2);
  switchPage('lobby');
});

const logout = () => {
  socket.emit('logout', {username: username.value});
  username.value = '';
  localStorage.removeItem('username');
}

const sendAdminCommand = (code: string) => {
  if (!code) return;
  console.log(`[Admin] Sending command: ${code}`);
  // 发送信号
  socket.emit('admin-command', code);
};

onMounted(() => {
  pubMsg('欢迎！', '客户端启动成功！', 'success', 2);
  socket.emit('get-room-list');

  (window as any).admin = sendAdminCommand;
  console.log('✅ Admin console command loaded. Use admin("code") to execute.');
})

onUnmounted(() => {
  if (username.value !== '') {
    socket.emit('logout', {username: username.value});
  }
})

const addMessage = (message: Message) => {
  messages.value.sort((a, b) => {
    const aDate = new Date(a.date);
    const bDate = new Date(b.date);
    return aDate.getTime() - bDate.getTime();
  });
  if (messages.value.length > 0 && messageEqual(messages.value[messages.value.length - 1], message)) {
    return;
  }
  pubMsg('新消息！', message.sender + ": " + message.msg, 'info', 2);
  messages.value.push(message);
}

const sendMessage = (msg: string, room: string | null, user: string | null) => {
  const newMessage: Message = {
    sender: username.value,
    msg: msg,
    date: new Date().toISOString(),
    room: room,
    user: user,
  };
  addMessage(newMessage);
  socket.emit('send-message', newMessage);
};

socket.on('new-message', (data: {msg: Message}) => {
  addMessage(data.msg);
});
socket.on('sync-chat', (data: {msgs: Message[]}) => {
  console.log(data);
  messages.value = data.msgs;
  pubMsg('聊天同步', '聊天同步成功！同步了' + data.msgs.length + '条消息！', 'success', 2);
});
socket.on('add-achievement', (data: {achievement: Achievement, username: string}) => {
  pubMsg(data.achievement.name, data.achievement.description, 'warning', 30);
});

const displayMessagePanel = ref(false);

const getDisplayMessagePanel = () => {
  return displayMessagePanel.value && username.value !== '';
}

const viewedCount = ref(0);

const openMessagePanel = () => {
  displayMessagePanel.value = true;
}

const closeMessagePanel = () => {
  displayMessagePanel.value = false;
}

const readMessage = (msg: Message) => {
  viewedCount.value = messages.value.length;
}

const displayRulesPanel = ref(false);

const openRulesPanel = () => {
  displayRulesPanel.value = true;
};

const closeRulesPanel = () => {
  displayRulesPanel.value = false;
};

const displayAchievementPanel = ref(false);
const getDisplayAchievementPanel = () => {
  return displayAchievementPanel.value && username.value !== '';
};
const closeAchievementPanel = () => {
  displayAchievementPanel.value = false;
};

const openAchievementPanel = () => {
  displayAchievementPanel.value = true;
  socket.emit('query-achievement', {username: username.value});
};

const displayUtilsPanel = ref(false);

const openUtilsPanel = () => {
  displayUtilsPanel.value = true;
}

const closeUtilsPanel = () => {
  displayUtilsPanel.value = false;
}

const achievements = ref<Achievement[]>([]);
socket.on('sync-achievements', (data: {achievements: Record<string, Achievement>}) => {
  console.log(data);
  achievements.value = Object.values(data.achievements);
});

onMounted(() => {
  const savedUsername = localStorage.getItem('username');
  if (savedUsername) {
    submitUsername(savedUsername);
  }
})
</script>

<template>
  <div class="app">
    <template v-if="displayPage === 'home'">
      <HomePage :submitUsername="submitUsername" />
    </template>
    <template v-else-if="displayPage === 'game'">
      <template v-if="displayPureText">
        <GamePureTextPage :username="username" :gameState="gameState" :rooms="rooms"/>
      </template>
      <template v-else>
        <GamePage :gameProps="gameProps" :updateGameProps="updateGameProps" :username="username" :gameState="gameState" :switchPage="switchPage"/>
      </template>
    </template>
    <template v-else-if="displayPage === 'lobby'">
      <LobbyPage 
        :rooms="rooms" 
        :username="username" 
        :switchPage="switchPage" 
        :currentRoom="currentRoom" 
        :setCurrentRoom="setCurrentRoom" 
        :logout="logout"
      />
    </template>
    <AlertList/>
    <ChatPanel
      v-if="getDisplayMessagePanel()"
      :sendMessage="sendMessage"
      :messages="messages"
      :rooms="rooms"
      :username="username"
      :currentRoom="currentRoom"
      :closeMessagePanel="closeMessagePanel"
      :readMessage="readMessage"
    />
    <AchievementPanel 
      v-if="getDisplayAchievementPanel()" 
      :closeAchievementPanel="closeAchievementPanel" 
      :achievements="achievements" 
    />
    <UtilsPanel v-if="displayUtilsPanel" :closeUtilsPanel="closeUtilsPanel" />
    <RulesPanel v-if="displayRulesPanel" :closeRulesPanel="closeRulesPanel" />
    <n-float-button @click="openMessagePanel" :bottom="10" :left="10" v-if="username !== ''" class="chat-float-button" type="primary">
      <n-badge :value="messages.length - viewedCount" :max="99" :offset="[6, -8]">
        <n-icon>
          <IconChat />
        </n-icon>
      </n-badge>
    </n-float-button>
    <n-float-button @click="openRulesPanel" :bottom="10" :left="70" v-if="username !== ''" class="rules-float-button" type="primary">
      <n-icon>
        <IconRules />
      </n-icon>
    </n-float-button>
    <n-float-button @click="openAchievementPanel" :bottom="10" :left="130" v-if="username !== ''" class="achievement-float-button" type="primary">
      <n-icon>
        <Achievement3 />
      </n-icon>
    </n-float-button>
    <n-float-button @click="openUtilsPanel" :bottom="10" :left="190" v-if="username !== '' && displayPage === 'game'" class="utils-float-button" type="primary">
      <n-icon>
        <IconUtils />
      </n-icon>
    </n-float-button>
    <n-float-button @click="switchPureTextMode" :bottom="10" :left="250" v-if="username !== '' && displayPage === 'game'" class="pure-text-float-button" type="primary">
      <n-icon>
        <IconRobot />
      </n-icon>
    </n-float-button>
  </div>
</template>

<style scoped>
.app {
  width: 100vw;
  margin: 0 auto;
  font-weight: normal;
  font-family: Arial, sans-serif;
}

.chat-float-button {
  z-index: 1000;
}

.rules-float-button {
  z-index: 1000;
}

.achievement-float-button {
  z-index: 1000;
}
</style>