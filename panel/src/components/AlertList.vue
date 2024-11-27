  <template>
  <div class="alert-container">
    <TransitionGroup name="alert-anime">
      <template v-for="alert, index in alertList" :key="index">
        <AlertMessage :title="alert.title" :content="alert.str" :type="alert.type" :closable="true" :visible="alert.visible" :icon="alert.icon"/>
      </template>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import AlertMessage from '@/components/AlertMessage.vue';
import PubSub from "pubsub-js";
import type { Achievement } from '@/interfaces/UserState';

interface AlertInfo {
  title: string;
  str: string;
  dur: number;
  type: "default" | "error" | "info" | "success" | "warning" | undefined;
  visible: boolean;
  icon?: string;
}

const alertList = ref<AlertInfo[]>([]);

const addMsg = (msg: AlertInfo) => {
  alertList.value.push(msg);
  const index = alertList.value.length - 1;
  setTimeout(() => {
    alertList.value[index].visible = false;
  }, msg.dur * 1000);
}

PubSub.subscribe('alert-pubsub-message', (id: string, msg: {
  title: string;
  str: string;
  type: "default" | "error" | "info" | "success" | "warning" | undefined;
  dur: number;
  icon?: string;
}) => {
  addMsg({
    title: msg.title,
    str: msg.str,
    type: msg.type,
    dur: msg.dur,
    visible: true,
    icon: msg.icon,
  });
});

</script>

<style scoped>

.alert-container {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  z-index: 10000;
}

.alert-container > .n-alert {
  margin-bottom: 12px;
  width: 320px;
}

.alert-anime-move,
.alert-anime-enter-active,
.alert-anime-leave-active {
  transition: all 0.3s ease;
}

/* Why Enter Animate Not Work?!?!?! */
.alert-anime-enter-from,
.alert-anime-leave-to {
  transform: translateX(-50px);
  opacity: 0;
}

/* .alert-anime-leave-active {
  position: absolute;
} */
</style>
