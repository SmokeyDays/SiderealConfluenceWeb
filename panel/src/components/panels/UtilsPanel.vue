<template>
  <PanelTemplate>
    <n-card hoverable class="standard-panel" content-class="utils-panel">
      <div class="utils-title">夏普里值计算器</div>
      <div v-for="(playerValue, index) in playerValues" :key="index" class="player-value-item">
        <n-input v-model:value="playerValues[index].id" placeholder="输入参与者ID" class="input-id" />
        <n-input-number v-model:value="playerValues[index].value" placeholder="输入参与者单方价值" type="number" />
        <n-button @click="removePlayerValue(index)" type="error" class="remove-button">x</n-button>
      </div>
      <n-button @click="addPlayerValue" type="primary" color="green" class="utils-add">+</n-button>
      
      <n-input-number v-model:value="grandValue" placeholder="输入全体参与者合作后的最终总价值" type="number" class="utils-totalvalue" />
      <n-button @click="calculateShapleyValues" type="primary" color="purple">计算夏普里值</n-button>
      <div v-if="shapleyResults.size > 0">
        <div class="results-title">计算结果:</div>
        <div v-for="(value, key) in shapleyResults" :key="key">
           {{ value[0] }} 应当分得 {{ value[1] }}
        </div>
      </div>
      <n-button class="close-achievement-button" @click="props.closeUtilsPanel" type="error">关闭</n-button>
    </n-card>
  </PanelTemplate>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { calculateShapleyValuesSimplified } from '@/interfaces/AssistantUtil';
import { NButton, NCard, NEmpty, NIcon, NInput, NInputNumber } from 'naive-ui';
import PanelTemplate from '@/components/panels/PanelTemplate.vue';

const playerValues = ref<{ id: string; value: number }[]>([{ id: '', value: 0 }]); // 初始化为一个对象数组
const grandValue = ref<number | null>(null);
const shapleyResults = ref<Map<string, number>>(new Map());

const props = defineProps<{
  closeUtilsPanel: () => void;
}>();

const closeUtilsPanel = () => {
  props.closeUtilsPanel();
};

const addPlayerValue = () => {
  playerValues.value.push({ id: '', value: 0 }); // 添加一个新的空对象
};

const removePlayerValue = (index: number) => {
  playerValues.value.splice(index, 1); // 删除指定索引的参与者单方价值
};

// 监视 playerValues 的变化，确保其动态更新
watch(playerValues, (newValues) => {
  console.log('参与者值已更新:', newValues);
});

const calculateShapleyValues = () => {
  const valuesMap = new Map<string, number>();
  playerValues.value.forEach(entry => {
    const id = entry.id.trim();
    const value = entry.value;
    if (id && value !== null && !isNaN(value)) {
      valuesMap.set(id, value);
    }
  });
  console.log(valuesMap);

  if (grandValue.value !== null) {
    shapleyResults.value = calculateShapleyValuesSimplified(valuesMap, Number(grandValue.value));
    console.log(shapleyResults.value);  
  }
};
</script>

<style>
.utils-panel {
  overflow-y: auto;
}
.utils-title {
  font-size: 1.2rem;
  font-weight: bold;
}
.results-title {
  margin-top: 10px;
  font-weight: bold;
}
.player-value-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  border: 1px solid #ccc; 
  padding: 10px; 
  width: 80%;
}
.input-id {
  width: 150px;
}
.utils-add {
  width: 80%;
}
.utils-totalvalue {
  margin-top: 1em;
  margin-bottom: 1em;
}
.remove-button {
  border-radius: 50%;
  width: 30px;
  height: 30px;
  text-align: center;
  line-height: 30px;
  font-size: 16px;
  color: white;
  background-color: red;
}
</style>
