<script setup lang="ts">
import { ref } from 'vue';
import { NSpace, NInput, NButton } from 'naive-ui';
import Culture from '@/components/icons/items/Culture.vue';
import Industry from '@/components/icons/items/Industry.vue';
import Food from '@/components/icons/items/Food.vue';
import Information from '@/components/icons/items/Information.vue';
import Ship from '@/components/icons/items/Ship.vue';
import Biotech from '@/components/icons/items/Biotech.vue';
import Energy from '@/components/icons/items/Energy.vue';
import Hypertech from '@/components/icons/items/Hypertech.vue';
import AnySmall from '@/components/icons/items/AnySmall.vue';
import AnyBig from '@/components/icons/items/AnyBig.vue';
import Score from '@/components/icons/items/Score.vue';
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
      <div class="title">
        <h1>Sidereal Confluence Web</h1>
        <h4>A game of trading and diplomacy in a sci-fi universe</h4>
      </div>
      <div class="icon-display">
        <Culture />
        <Industry />
        <Food />
        <Information />
        <Ship />
        <Biotech />
        <Energy />
        <Hypertech />
        <AnySmall />
        <AnyBig />
        <Score />
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

.icon-display {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  margin-bottom: 20px;
}

.icon-display > * {
  width: 100px;
  height: 100px;
}
</style>
