<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NSelect, NCard } from 'naive-ui';
import { getSpecieColor, items } from '@/interfaces/GameConfig';
import type { Factory, GameState } from '@/interfaces/GameState';

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
  const res: { label: string, value: number }[] = [];
  for (const cost of Object.keys(props.factory.feature.properties['research_cost']).map(Number)) {
    let description = "";
    for (const item in props.factory.feature.properties['research_cost'][cost]) {
      description += `${item}: ${props.factory.feature.properties['research_cost'][cost][item]} `;
    }
    res.push({ label: description, value: cost });
  }
  return res;
}

const affordCost = () => {
  const player = props.gameState.players.find(player => player.user_id === props.username);
  if (player === undefined) {
    return false;
  }
  for (const item in props.factory.feature.properties['research_cost'][costType.value]) {
    if (player.storage[item] < props.factory.feature.properties['research_cost'][costType.value][item]) {
      return false;
    }
  }
  return true;
}
</script>

<template>
  <n-card hoverable class="research-panel">
    <div class="research-cost-title">Choose a cost type:</div>
    <div class="research-cost-input"> 
      <n-select v-model:value="costType" :options="getCostTypeOptions()" placeholder="Choose a cost type" />
      <n-button class="submit-research-button" @click="submitResearch" type="primary" :disabled="!affordCost()">Submit Research</n-button>
      <n-button class="close-research-button" @click="submitClose" type="error">Close</n-button>
    </div>
  </n-card>
</template>

<style>
.research-panel {
  width: 40vw;
  height: 75vh;
}
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
