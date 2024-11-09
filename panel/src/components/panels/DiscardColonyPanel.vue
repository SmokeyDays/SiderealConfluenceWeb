<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NSelect, NCard } from 'naive-ui';
import { getSpecieColor, items } from '@/interfaces/GameConfig';
import type { Factory, GameState, Player } from '@/interfaces/GameState';
import PanelTemplate from '@/components/panels/PanelTemplate.vue';

const props = defineProps<{
  submitDiscardColony: (colonies: string[]) => void;
  closeDiscardColonyPanel: () => void;
  getMe: () => Player;
  username: string;
  gameState: GameState;
  discardNum: number;
}>();
const colonies = ref([]);
const submitDiscardColony = () => {
  props.submitDiscardColony(colonies.value);
  submitClose();
};

const submitClose = () => {
  props.closeDiscardColonyPanel();
};

const getColonyOptions = () => {
  const res: { label: string, value: string }[] = [];
  for (const factory of Object.keys(props.getMe().factories)) {
    if (props.getMe().factories[factory].feature["type"] === "Colony") {
      const colony_name = props.getMe().factories[factory].name;
      res.push({ label: colony_name, value: colony_name });
    }
  }
  return res;
}

const checkValid = () => {
  return colonies.value.length === props.discardNum;
}
</script>

<template>
  <PanelTemplate>
    <n-card hoverable class="research-panel">
      <div class="research-cost-title">你必须弃置{{ discardNum }}个殖民地</div>
    <div class="research-cost-input"> 
      <n-select v-model:value="colonies" :options="getColonyOptions()" placeholder="选择殖民地" multiple/>
      <n-button class="submit-research-button" @click="submitDiscardColony" type="primary" :disabled="!checkValid()">确定</n-button>
      <n-button class="close-research-button" @click="submitClose" type="error">关闭</n-button>
      </div>
    </n-card>
  </PanelTemplate>
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
