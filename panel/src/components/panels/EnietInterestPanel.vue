<script setup lang="ts">
import { ref, watch } from 'vue';
import { NButton, NSelect, NCard, NInputNumber } from 'naive-ui';
import { bigItem, smallItem } from '@/interfaces/GameConfig';
import { getStorage, type Factory, type GameState, type Player } from '@/interfaces/GameState';
import ItemEntryDiv from '@/components/ItemEntryDiv.vue';
import PanelTemplate from '@/components/panels/PanelTemplate.vue';

const props = defineProps<{
  submitEnietInterestSelect: (factoryName: string, properties: {"output_type": string, "input_combination": {[key: string]: number}}) => void
  closeEnietInterestPanel: () => void;
  factory: Factory;
  me: Player;
  gameState: GameState;
}>();
const outputType = ref("");
const wildCount = ref(0);

const getInputCombination = () => {
  const res: {[key: string]: number} = {};
  res[getWildItem()] = wildCount.value;
  res[outputType.value] = getKeyItem().count - wildCount.value;
  return res;
}
const submit = () => {
  props.submitEnietInterestSelect(props.factory.name, {
    "output_type": outputType.value,
    "input_combination": getInputCombination()
  });
  submitClose();
};

const getKeyItem = () => {
  if ((props.factory.converter.input_items instanceof Array)) {
    return {
      type: "Error",
      count: 0
    };
  }
  if (props.factory.converter.input_items["ArbitrarySmall"]) {
    return {
      type: "Small",
      count: props.factory.converter.input_items["ArbitrarySmall"]
    }
  } else if (props.factory.converter.input_items["ArbitraryBig"]) {
    return {
      type: "Big",
      count: props.factory.converter.input_items["ArbitraryBig"]
    }
  } else {
    return {
      type: "Error",
      count: 0
    }
  }
}

const getWildItem = () => {
  return "Wild" + getKeyItem().type;
}

const submitClose = () => {
  outputType.value = "";
  wildCount.value = 0;
  props.closeEnietInterestPanel();
};

const getOutputTypeOptions = () => {
  if ((props.factory.converter.input_items instanceof Array)) {
    return [];
  }
  let legalOutputs = [];
  const keyItem = getKeyItem();

  if (keyItem.type === "Small") {
    legalOutputs = smallItem;
  } else if (keyItem.type === "Big") {
    legalOutputs = bigItem;
  } else {
    return [];
  }
  const res: { label: string, value: string }[] = [];
  for (const item of legalOutputs) {
    if ((props.me.storage[item] || 0) + (props.me.storage[getWildItem()] || 0) >= keyItem.count) {
      res.push({ label: item, value: item})
    }
  }
  return res;
}

const affordCost = () => {
  if (outputType.value === "") {
    return false;
  }
  if (wildCount.value > getStorage(props.me, getWildItem())) {
    return false;
  }
  if (getKeyItem().count - wildCount.value > getStorage(props.me, outputType.value)) {
    return false;
  }
  return true;
}

const getWildItemLimit = (min: boolean, output = outputType.value) => {
  if (min) {
    return Math.max(getKeyItem().count - getStorage(props.me, output), 0);
  } else {
    return Math.min(getStorage(props.me, getWildItem()), getKeyItem().count);
  }
}

const onOutputTypeChange = () => {
  wildCount.value = getWildItemLimit(true);
  console.log(wildCount.value)
}
</script>

<template>
  <PanelTemplate>
    <n-card hoverable class="eniet-interest-panel standard-panel">
      <div class="eniet-interest-cost-title">选择存放的利息类型</div>
    <div class="eniet-interest-cost-input"> 
      <n-select v-model:value="outputType" :options="getOutputTypeOptions()" placeholder="选择存放的利息类型" @update:value="onOutputTypeChange"/>
      <template v-if="outputType != ''">
        <div class="eniet-interest-cost-entry">
          <ItemEntryDiv 
            :item="outputType"
            :count="getKeyItem().count - wildCount"
            :icon-height="60"
            :icon-width="60"
            v-if="getKeyItem().count - wildCount"
          />
          <ItemEntryDiv 
            :item="getWildItem()"
            :count="wildCount"
            :icon-height="60"
            :icon-width="60"
            v-if="wildCount > 0"
          />
        </div>
        <div class="eniet-interest-cost-entry eniet-interest-cost-title">
          使用
          <n-input-number v-model:value="wildCount" class="eniet-interest-input-number" :placeholder="getWildItemLimit(true).toString()" :min="getWildItemLimit(true)" :max="getWildItemLimit(false)"/>
          个 {{ getWildItem() }}
        </div>
    </template>
      <n-button class="submit-eniet-interest-button" @click="submit" type="primary" :disabled="!affordCost()">Submit Research</n-button>
      <n-button class="close-eniet-interest-button" @click="submitClose" type="error">Close</n-button>
      </div>
    </n-card>
  </PanelTemplate>
</template>

<style>
.eniet-interest-cost-input {
  display: flex;
  flex-direction: column;
  align-items: start;
  justify-content: start;
}
.eniet-interest-cost-entry {
  display: flex;
  flex-direction: row;
  align-items: start;
  justify-content: start;
}
.close-eniet-interest-button {
  position: absolute;
  bottom: 40px;
  right: 40px;
}
.submit-eniet-interest-button {
  position: absolute;
  bottom: 40px;
  right: 120px;
}
.eniet-interest-cost-title {
  font-size: 1.2rem;
  font-weight: bold;
}
.eniet-interest-input-number {
  width: 90px;
}
</style>
