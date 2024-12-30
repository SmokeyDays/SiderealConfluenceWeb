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
import IconChat from '@/components/icons/IconChat.vue';
import IconRules from '@/components/icons/IconRules.vue';
import ChatPanel from '@/components/panels/ChatPanel.vue';
import RulesPanel from '@/components/panels/RulesPanel.vue';
import type { Achievement } from './interfaces/UserState';
import AchievementPanel from './components/panels/AchievementPanel.vue';
import Achievement3 from './components/icons/alerts/Achievement3.vue';

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
  if (displayPureText.value) {
    socket.emit('query-prompt', {room_name: currentRoom.value, username: username.value});
  }
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

socket.on('prompt', (data: {prompt: string}) => {
  pureText.value = data.prompt;
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

const login = (newUsername: string) => {
  username.value = newUsername;
  localStorage.setItem('username', username.value);
}

socket.on('login-success', (data: any) => {
  login(data['username']);
  PubSub.publish('alert-pubsub-message', {
    title: '登录成功！',
    str: '欢迎！ ' + username.value,
    type: 'success',
    dur: 2,
    visible: true,
  });
  switchPage('lobby');
});

const logout = () => {
  socket.emit('logout', {username: username.value});
  username.value = '';
  localStorage.removeItem('username');
}

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

const addMessage = (message: Message) => {
  messages.value.sort((a, b) => {
    const aDate = new Date(a.date);
    const bDate = new Date(b.date);
    return aDate.getTime() - bDate.getTime();
  });
  if (messages.value.length > 0 && messageEqual(messages.value[messages.value.length - 1], message)) {
    return;
  }
  PubSub.publish('alert-pubsub-message', {
    title: '新消息：' + message.sender + "->" + (message.user? message.user : "All") + " in  " + (message.room? message.room : "All"),
    str: message.msg,
    type: 'info',
    dur: 2,
    visible: true,
  });
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
  PubSub.publish('alert-pubsub-message', {
    title: '聊天同步',
    str: '聊天同步成功！同步了' + data.msgs.length + '条消息！',
    type: 'success',
    dur: 2,
    visible: true,
  });
});
socket.on('add-achievement', (data: {achievement: Achievement, username: string}) => {
  PubSub.publish('alert-pubsub-message', {
    title: data.achievement.name,
    str: data.achievement.description,
    type: 'warning',
    dur: 30,
    visible: true,
    icon: 'Achievement' + data.achievement.difficulty,
  });
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
        <GamePureTextPage :pureText="pureText" />
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
    <n-float-button @click="switchPureTextMode" :bottom="10" :left="190" v-if="username !== ''" class="pure-text-float-button" type="primary">

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