<template>
  <div class="game-pure-text-page">
    <div class="pure-text">
      {{ pureText }}
    </div>
    <n-input 
        type="textarea" 
        v-model:value="command" 
        placeholder="Enter your command" 
        class="command-input" 
        :autosize="{
          minRows: 1,
          maxRows: 4,
        }" 
        @keydown.ctrl.enter="submitCommand"
      />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { NInput } from 'naive-ui';

const props = defineProps<{
  pureText: string
}>();
const command = ref("");
const submitCommand = () => {
  console.log(command.value);
  command.value = "";
}
</script>

<style scoped>
.game-pure-text-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-items: center;
}
.pure-text {
  width: 80vw;
  height: 80vh;
  font-size: 16px;
  color: #333;
  white-space: pre-wrap;
  overflow: auto;
}
.command-input {
  width: 80vw;
  height: 10vh;
}
</style>
