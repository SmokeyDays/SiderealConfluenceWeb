<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NSelect, NCard } from 'naive-ui';
import { getItemZhDesc, getSpecieColor, items } from '@/interfaces/GameConfig';
import { getFavorCost, isOnFavorBuff, type Factory, type GameState } from '@/interfaces/GameState';
import PanelTemplate from '@/components/panels/PanelTemplate.vue';

const props = defineProps<{
  submitResearch: (factoryName: string, costType: number) => void;
  closeResearchPanel: () => void;
  factory: Factory;
  username: string;
  gameState: GameState;
}>();
const costType = ref(0);

const submitResearch = () => {
  props.submitResearch(props.factory.name, costType.value);
  submitClose();
};

const submitClose = () => {
  costType.value = 0;
  props.closeResearchPanel();
};

const getCostTypeOptions = () => {
  if (!(props.factory.converters[0].input_items instanceof Array)) {
    return [];
  }
  const res: { label: string, value: number }[] = [];
  for (const cost of Object.keys(props.factory.converters[0].input_items).map(Number)) {
    let description = "";
    for (const item in props.factory.converters[0].input_items[cost]) {
      let num = props.factory.converters[0].input_items[cost][item];
      num = getFavorCost(props.gameState, props.username, item, num);
      description += `${getItemZhDesc(item)}: ${num} `;
    }
    res.push({ label: description, value: cost });
  }
  return res;
}

const affordCost = () => {
  if (!(props.factory.converters[0].input_items instanceof Array)) {
    return false;
  }
  const player = props.gameState.players.find(player => player.user_id === props.username);
  if (player === undefined) {
    return false;
  }
  for (const item in props.factory.converters[0].input_items[costType.value]) {
    let cost = props.factory.converters[0].input_items[costType.value][item];
    cost = getFavorCost(props.gameState, props.username, item, cost);
    if (player.storage[item] < cost) {
      return false;
    }
  }
  return true;
}
</script>

<template>
  <PanelTemplate>
    <n-card hoverable class="research-panel standard-panel">
      <div class="research-cost-title">Choose a cost type:</div>
    <div class="research-cost-input"> 
      <n-select v-model:value="costType" :options="getCostTypeOptions()" placeholder="Choose a cost type" />
      <n-button class="submit-research-button" @click="submitResearch" type="primary" :disabled="!affordCost()">Submit Research</n-button>
      <n-button class="close-research-button" @click="submitClose" type="error">Close</n-button>
      </div>
    </n-card>
  </PanelTemplate>
</template>

<style>
.research-cost-input {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}
.close-research-button {
  position: absolute;
  bottom: 40px;
  right: 40px;
}
.submit-research-button {
  position: absolute;
  bottom: 40px;
  right: 120px;
}
.research-cost-title {
  font-size: 1.2rem;
  font-weight: bold;
}
</style>
