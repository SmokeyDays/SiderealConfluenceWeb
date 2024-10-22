<script setup lang="ts">
import { ref } from 'vue';
import { NSpace, NInput, NButton } from 'naive-ui';
import Food from '../components/icons/Food.vue';
import Culture from '../components/icons/Culture.vue';
import Industry from '@/components/icons/Industry.vue';
const username = ref('');

const props = defineProps<{
  submitUsername: (username: string) => void
}>();

const handleSubmit = () => {
  if (username.value.trim()) {
    props.submitUsername(username.value.trim());
  }
};
</script>

<template>
  <div class="homepage">
    <n-space vertical align="center" justify="center" class="content">
      <div class="logo">
        <Industry />
      </div>
      <n-input v-model:value="username" placeholder="Enter your username" @keyup.enter="handleSubmit" />
      <n-button type="primary" @click="handleSubmit" :disabled="!username.trim()">
        Submit
      </n-button>
    </n-space>
  </div>
</template>

<style scoped>
.homepage {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.content {
  text-align: center;
}

.logo {
  width: 200px;
  height: 200px;
  background-color: #f0f0f0; /* Placeholder color */
  margin-bottom: 20px;
}
</style>
