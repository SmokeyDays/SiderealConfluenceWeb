<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NSelect, NCard } from 'naive-ui';
import { getSpecieColor, items } from '@/interfaces/GameConfig';
import type { Factory, GameState, Player } from '@/interfaces/GameState';

const props = defineProps<{
  submitExchange: (colonies: string[]) => void;
  closeExchangePanel: () => void;
  username: string;
  gameState: GameState;
  getMe: () => Player | null;
}>();
const selectedColonies = ref<string[]>([]);

const submitExchange = () => {
  props.submitExchange(selectedColonies.value);
  submitClose();
};

const submitClose = () => {
  selectedColonies.value = [];
  props.closeExchangePanel();
};

const getColonies = () => {
  const res = [];
  for (const factory of Object.values(props.getMe()!.factories)) {
    if (factory.feature["type"] === "Colony") {
      res.push(factory);
    }
  }
  return res;
}

const getColonyOptions = () => {
  return getColonies().map(colony => ({ label: colony.name, value: colony.name }));
}
</script>

<template>
  <n-card hoverable class="exchange-panel">
    <div class="exchange-colony-title">将殖民地转换为物品以用于升级</div>
    <div class="exchange-colony-description">注意：殖民地转换为物品后，殖民地将不复存在！这项交换产生的物品仅用于运行殖民地作为投入的转换器！</div>
    <div class="exchange-colony-input"> 
      <n-select v-model:value="selectedColonies" :options="getColonyOptions()" placeholder="Choose colonies" multiple/>
      <n-button class="submit-exchange-button" @click="submitExchange" type="primary" :disabled="selectedColonies.length === 0">确认</n-button>
      <n-button class="close-exchange-button" @click="submitClose" type="error">取消</n-button>
    </div>
  </n-card>
</template>

<style>
.exchange-panel {
  width: 40vw;
  height: 75vh;
}
.exchange-colony-input {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}
.close-exchange-button {
  position: absolute;
  bottom: 40px;
  right: 40px;
}
.submit-exchange-button {
  position: absolute;
  bottom: 40px;
  right: 120px;
}
.exchange-colony-title {
  font-size: 1.2rem;
  font-weight: bold;
}
.exchange-colony-description {
  font-size: 0.8rem;
  color: #ff0000;
}
</style>
