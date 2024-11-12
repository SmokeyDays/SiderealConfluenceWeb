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
import WildSmall from '@/components/icons/items/WildSmall.vue';
import WildBig from '@/components/icons/items/WildBig.vue';
import Score from '@/components/icons/items/Score.vue';
import { isProduction } from '@/utils/config';
import ItemEntry from '@/components/ItemEntry.vue';
import ItemEntryDiv from '@/components/ItemEntryDiv.vue';
const username = ref(isProduction? '': 'Alice');

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
        <ItemEntryDiv item="Culture" :count="1" :icon-width="80" :icon-height="80" />
        <ItemEntryDiv item="Industry" :count="1" :icon-width="80" :icon-height="80" />
        <ItemEntryDiv item="Food" :count="1" :icon-width="80" :icon-height="80" />
        <ItemEntryDiv item="Information" :count="1" :icon-width="80" :icon-height="80" />
        <ItemEntryDiv item="Ship" :count="1" :icon-width="80" :icon-height="80" />
        <ItemEntryDiv item="Biotech" :count="1" :icon-width="80" :icon-height="80" />
        <ItemEntryDiv item="Energy" :count="1" :icon-width="80" :icon-height="80" />
        <ItemEntryDiv item="Hypertech" :count="1" :icon-width="80" :icon-height="80" />
        <ItemEntryDiv item="WildSmall" :count="1" :icon-width="80" :icon-height="80" />
        <ItemEntryDiv item="WildBig" :count="1" :icon-width="80" :icon-height="80" />
        <ItemEntryDiv item="Score" :count="1" :icon-width="80" :icon-height="80" />
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
  /* height: 100vh; */
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
