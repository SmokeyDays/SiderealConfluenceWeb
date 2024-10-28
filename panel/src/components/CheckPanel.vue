<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NSelect, NCard } from 'naive-ui';
import { getSpecieColor, items } from '@/interfaces/GameConfig';
import type { Factory, GameState } from '@/interfaces/GameState';

const props = defineProps<{
  checkMessage: string;
  checkCallback: () => void;
  closeCallback: () => void;
}>();

const closeCheckPanel = () => {
  props.closeCallback();
}

const submitCheck = () => {
  props.checkCallback();
  closeCheckPanel();
}
</script>

<template>
  <n-card hoverable class="research-panel">
    <div class="research-cost-title">{{ props.checkMessage }}</div>
      <div class="research-cost-input"> 
      <n-button class="submit-research-button" @click="submitCheck" type="primary">确定</n-button>
      <n-button class="close-research-button" @click="closeCheckPanel" type="error">取消</n-button>
    </div>
  </n-card>
</template>

<style>
.research-panel {
  width: 40vw;
  height: 40vh;
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
