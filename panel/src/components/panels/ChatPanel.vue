<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from 'vue';
import { NButton, NSelect, NCard, NTag, NInput, NList, NListItem, NTooltip, NAvatar } from 'naive-ui';
import PanelTemplate from '@/components/panels/PanelTemplate.vue';
import type { Message } from '@/interfaces/ChatState';
import type { RoomList } from '@/interfaces/RoomState';
import { getAvatarSrc } from '@/utils/icon';
const props = defineProps<{
  sendMessage: (msg: string, room: string | null, user: string | null) => void;
  messages: Message[];
  rooms: RoomList;
  username: string;
  currentRoom: string;
  closeMessagePanel: () => void;
  readMessage: (msg: Message) => void;
}>();

const selectedRoom = ref<string>(props.currentRoom);
const selectedUser = ref<string>("");
const message = ref('');

const submitMessage = () => {
  if (message.value === "") {
    return;
  }
  props.sendMessage(
    message.value, 
    selectedRoom.value === "" ? null : selectedRoom.value, 
    selectedUser.value === "" ? null : selectedUser.value
  );
  message.value = '';
};

const getRoomOptions = () => {
  const roomList = Object.keys(props.rooms).filter(room => props.rooms[room].players[props.username] !== undefined);
  const options: { label: string, value: string }[] = roomList.map(room => ({ label: "[房间] " + room, value: room }));
  options.push({ label: "[大厅]", value: "" });
  return options;
};

const getUserOptions = () => {
  const users: Set<string> = new Set();
  for (const room of Object.values(props.rooms)) {
    for (const user of Object.keys(room.players)) {
      users.add(user);
    }
  }
  const options: { label: string, value: string }[] = [];
  for (const user of Array.from(users)) {
    if (user === props.username) {
      continue;
    }
    if (selectedRoom.value === "") {
      options.push({ label: "[私聊] " + user, value: user });
    } else if (props.rooms[selectedRoom.value].players[user] !== undefined) {
      options.push({ label: "[私聊] " + user, value: user });
    }
  }
  options.push({ label: "[所有人]", value: "" });
  return options;
};

const isSpecialMessage = (msg: Message) => {
  return msg.sender === "OP";
};

const getMessages = () => {
  return props.messages.filter(msg => 
    isSpecialMessage(msg) ||
    (
      ((selectedRoom.value === "" && msg.room === null) || 
        ((msg.room === selectedRoom.value))
      ) &&
      ((selectedUser.value === "" && msg.user === null) ||
        msg.user === selectedUser.value || 
        (msg.sender === selectedUser.value && msg.user !== null))
    )
  );
};

const getMessageInputDisabled = () => {
  return selectedUser.value === props.username || message.value === "";
};

// const getMsgPrefix = (msg: Message) => {
//   return `[${msg.room ? msg.room : "大厅"}] [${msg.user ? "私聊" : "所有人"}]`;
// };

const scrollChatMessages = () => {
  nextTick(() => {
    const chatMessagesDiv = document.querySelector('.chat-messages');
    if (chatMessagesDiv) {
      chatMessagesDiv.scrollTop = chatMessagesDiv.scrollHeight;
    }
    props.readMessage(props.messages[props.messages.length - 1]);
  });
};
watch(message, scrollChatMessages);

onMounted(() => {
  scrollChatMessages();
});
</script>

<template>
  <PanelTemplate>
    <n-card hoverable class="chat-panel standard-panel">
      <div class="chat-selects">
        <n-select v-model:value="selectedRoom" :options="getRoomOptions()" placeholder="Choose a room" class="chat-room-select" />
        <n-select v-model:value="selectedUser" :options="getUserOptions()" placeholder="Choose a user" class="chat-user-select" />
      </div>
      <div class="chat-messages">
        <n-list hoverable :show-divider="false">
          <template v-for="msg in getMessages()" :key="msg.date">
            <n-list-item>
              <template v-if="isSpecialMessage(msg)">
                <div class="chat-message-block-special">
                  <n-tooltip placement="top" trigger="click">
                    <template #trigger>
                      <div class="chat-message-content special-message">{{ msg.msg }}</div>
                    </template>
                    <div>{{ new Date(msg.date).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }) }}</div>
                  </n-tooltip>
                </div>
              </template>
              <template v-else>
                <div class="outer-chat-message-block">
                  <div class="chat-message-avatar" v-if="msg.sender !== username">
                    <n-avatar :src="getAvatarSrc(msg.sender)" round size="small" />
                  </div>
                  <div :class="msg.sender === username ? 'chat-message-block-self' : 'chat-message-block'">
                    <div class="chat-message-sender">
                      {{ msg.sender }}
                    </div>
                    <n-tooltip :placement="msg.sender === username ? 'right' : 'left'" trigger="click">
                      <template #trigger>
                        <div class="chat-message-content">{{ msg.msg }}</div>
                      </template>
                      <div>{{ new Date(msg.date).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }) }}</div>
                    </n-tooltip>
                  </div>
                  <div class="chat-message-avatar" v-if="msg.sender === username">
                    <n-avatar :src="getAvatarSrc(msg.sender)" round size="small" />
                  </div>
                </div>
              </template>
            </n-list-item>
          </template>
        </n-list>
      </div>
      <n-input 
        type="textarea" 
        v-model:value="message" 
        placeholder="Enter your message" 
        :disabled="selectedUser === username" 
        class="chat-message-input" 
        :autosize="{
          minRows: 1,
          maxRows: 4,
        }" 
        @keydown.ctrl.enter="submitMessage"
      />
      <n-tooltip>
        <template #trigger>
          <n-button class="submit-message-button"
            @click="submitMessage" 
            type="primary" 
            :disabled="getMessageInputDisabled()"
          >发送</n-button>
        </template>
        <div>Ctrl + Enter 发送</div>
      </n-tooltip>
      <n-button class="close-message-button" @click="closeMessagePanel" type="error">关闭</n-button>
    </n-card>
  </PanelTemplate>
</template>

<style>
.chat-panel {
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
  width: auto;
  max-height: 40vh;
  overflow-y: auto;
  margin: 20px 0;
}
.chat-message-avatar {
  margin: 0 5px;
}
.outer-chat-message-block {
  display: flex;
  flex-direction: row;
}
.chat-message-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
}
.chat-message-block-self {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  width: 100%;
}
.chat-message-block-special {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}
.chat-message-sender {
  font-size: 0.8rem;
  font-weight: bold;
}
.chat-message-content {
  max-width: 60%;
  background-color: #f0f0f0;
  border-radius: 10px;
  padding: 10px;
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
.special-message {
  font-style: italic;
  font-size: 0.8rem;
}
</style>
