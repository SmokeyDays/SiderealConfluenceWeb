<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NSelect, NCard, NTag, NInput } from 'naive-ui';
import PanelTemplate from '@/components/panels/PanelTemplate.vue';
import type { Message } from '@/interfaces/ChatState';
import type { RoomList } from '@/interfaces/RoomState';

const props = defineProps<{
  sendMessage: (msg: string, room: string | null, user: string | null) => void;
  messages: Message[];
  rooms: RoomList;
  username: string;
  closeMessagePanel: () => void;
}>();

const selectedRoom = ref<string>("");
const selectedUser = ref<string>("");
const message = ref('');

const submitMessage = () => {
  props.sendMessage(
    message.value, 
    selectedRoom.value === "" ? null : selectedRoom.value, 
    selectedUser.value === "" ? null : selectedUser.value
  );
  message.value = '';
};

const getRoomOptions = () => {
  const options: { label: string, value: string }[] = Object.keys(props.rooms).map(room => ({ label: room, value: room }));
  options.push({ label: "All", value: "" });
  return options;
};

const getUserOptions = () => {
  const users: Set<string> = new Set();
  for (const room of Object.values(props.rooms)) {
    for (const user of Object.keys(room.players)) {
      users.add(user);
    }
  }
  const options: { label: string, value: string }[]   = Array.from(users).map(user => ({ label: user, value: user }));
  options.push({ label: "All", value: "" });
  return options;
};

const getMessages = () => {
  return props.messages.filter(msg => 
    (selectedRoom.value === "" || msg.room === selectedRoom.value) &&
    (selectedUser.value === "" || msg.user === selectedUser.value)
  );
};

const getMessageInputDisabled = () => {
  return selectedUser.value === props.username || message.value === "";
};
</script>

<template>
  <PanelTemplate>
    <n-card hoverable class="chat-panel">
      <div class="chat-selects">
        <n-select v-model:value="selectedRoom" :options="getRoomOptions()" placeholder="Choose a room" class="chat-room-select" />
        <n-select v-model:value="selectedUser" :options="getUserOptions()" placeholder="Choose a user" class="chat-user-select" />
      </div>
      <div class="chat-messages">
        <n-tag v-for="msg in getMessages()" :key="msg.date" closable>{{ msg.sender }}: {{ msg.msg }}</n-tag>
      </div>
      <n-input v-model:value="message" placeholder="Enter your message" :disabled="selectedUser === username" class="chat-message-input" />
      <n-button class="submit-message-button" @click="submitMessage" type="primary" :disabled="getMessageInputDisabled()">Send Message</n-button>
      <n-button class="close-message-button" @click="closeMessagePanel" type="error">Close</n-button>
    </n-card>
  </PanelTemplate>
</template>

<style>
.chat-panel {
  width: 40vw;
  height: 75vh;
  display: flex;
  flex-direction: column;
}
.chat-room-title,
.chat-user-title,
.chat-message-title {
  font-size: 1.2rem;
  font-weight: bold;
}
.submit-message-button {
  position: absolute;
  bottom: 20px;
  right: 100px;
}
.chat-messages {
  position: absolute;
  top: 120px;
  bottom: 80px;
  overflow-y: auto;
}
.close-message-button {
  position: absolute;
  bottom: 20px;
  right: 20px;
}
.chat-room-select,
.chat-user-select,
.chat-message-input {
  margin-bottom: 10px;
}
.chat-selects {
  display: flex;
  justify-content: space-between;
}
</style>
