<script setup lang="ts">
import { computed, ref, type CSSProperties } from 'vue';
import { NButton, NSelect, NCard, NInputNumber, NSwitch, NTabs, NTabPane } from 'naive-ui';
import { arbitraryBigSource, arbitrarySmallSource, arbitraryWorldSource, getItemOption, getItemZhNameDesc, getSpecieColor, items, wildBigTarget, wildSmallTarget } from '@/interfaces/GameConfig';
import type { Factory, GameState, Player } from '@/interfaces/GameState';
import ItemEntryDiv from '@/components/ItemEntryDiv.vue';
import PanelTemplate from '@/components/panels/PanelTemplate.vue';

const props = defineProps<{
  submitExchange: (colonies: string[], arbitraryItems: { [key: string]: number }, wildItems: { [key: string]: number }) => void;
  closeExchangePanel: () => void;
  username: string;
  gameState: GameState;
  getMe: () => Player | null;
  arbitraryItems: { [key: string]: number };
  updateArbitraryItems: (items: { [key: string]: number }) => void;
  wildItems: { [key: string]: number };
  updateWildItems: (items: { [key: string]: number }) => void;
}>();
const selectedColonies = ref<string[]>([]);
const exchangeType = ref<string>("wild");
const dealingArbitrary = computed(() => exchangeType.value === "arbitrary");

const newArbitraryItem = ref<string>("");
const newArbitraryItemCount = ref<number>(1);

const submitExchange = () => {
  props.submitExchange(selectedColonies.value, props.arbitraryItems, props.wildItems);
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

const removeItem = (item: string) => {
  updateItem({...getItem(), [item]: 0});
}

const updateItem = (items: { [key: string]: number }) => {
  if (dealingArbitrary.value) {
    props.updateArbitraryItems(items);
  } else {
    props.updateWildItems(items);
  }
}
const getItem = () => {
  if (dealingArbitrary.value) {
    return props.arbitraryItems;
  } else {
    return props.wildItems;
  }
}

const getItemRestriction = (item: string) => {
  if (dealingArbitrary.value) {
    return (props.getMe()!.storage[item] || 0) - (getItem()[item] || 0);
  } else {
    const wildSmallCount = props.getMe()!.storage["WildSmall"] || 0;
    const wildBigCount = props.getMe()!.storage["WildBig"] || 0;
    let smallTarget = 0;
    let bigTarget = 0;
    for (const currentItem of Object.keys(getItem())) {
      if (wildSmallTarget.includes(currentItem)) {
        smallTarget += getItem()[currentItem];
      } else if (wildBigTarget.includes(currentItem)) {
        bigTarget += getItem()[currentItem];
      }
    }
    if (wildSmallTarget.includes(item)) {
      return wildSmallCount - smallTarget;
    } else if (wildBigTarget.includes(item)) {
      return wildBigCount - bigTarget;
    }
    return 0;
  }
}

const getItemOptions = () => {
  const res: { label: string, value: string }[] = [];
  if (dealingArbitrary.value) {
    const arbitrarySource = arbitrarySmallSource.concat(arbitraryBigSource).concat(arbitraryWorldSource);
    arbitrarySource.forEach(item => {
    if (getItemRestriction(item) > 0) {
      res.push(getItemOption(item));
      }
    });
  } else {
    const wildSource = wildSmallTarget.concat(wildBigTarget);
    wildSource.forEach(item => {
      if (getItemRestriction(item) > 0) {
        res.push(getItemOption(item));
      }
    });
  }
  return res;
}

const addItem = () => {
  if (newArbitraryItem.value !== "" && newArbitraryItemCount.value > 0) {
    if (getItem()[newArbitraryItem.value] === undefined) {
      updateItem({...getItem(), [newArbitraryItem.value]: newArbitraryItemCount.value});
    } else {
      updateItem({...getItem(), [newArbitraryItem.value]: getItem()[newArbitraryItem.value] + newArbitraryItemCount.value});
    }
  }
};

const checkSubmit = () => {
  if (dealingArbitrary.value) {
    for (const item of Object.keys(getItem())) {
      if (getItemRestriction(item) < 0) {
        return false;
      }
    }
  } else {
    const wildSmallCount = props.getMe()!.storage["WildSmall"] || 0;
    const wildBigCount = props.getMe()!.storage["WildBig"] || 0;
    let smallTarget = 0;
    let bigTarget = 0;
    for (const item of Object.keys(getItem())) {
      if (wildSmallTarget.includes(item)) {
        smallTarget += getItem()[item];
      } else if (wildBigTarget.includes(item)) {
        bigTarget += getItem()[item];
      }
    }
    if (wildSmallCount < smallTarget || wildBigCount < bigTarget) {
      return false;
    }
  }
  return true;
}

const railStyle = ({
    focused,
    checked
  }: {
    focused: boolean
    checked: boolean
  }) => {
  const style: CSSProperties = {}
  if (checked) {
    style.background = '#d03050'
    if (focused) {
      style.boxShadow = '0 0 0 2px #d0305040'
    }
  }
  else {
    style.background = '#2080f0'
    if (focused) {
      style.boxShadow = '0 0 0 2px #2080f040'
    }
  } 
  return style;
}
</script>

<template>
  <PanelTemplate>
    <n-card hoverable class="exchange-panel standard-panel">
      <div class="exchange-colony-title">将殖民地转换为物品以用于升级</div>
      <div class="exchange-colony-description">注意：殖民地转换为物品后，殖民地将不复存在！这项交换产生的物品仅用于运行殖民地作为投入的转换器！</div>
      <div class="exchange-colony-input"> 
        <n-select v-model:value="selectedColonies" :options="getColonyOptions()" placeholder="Choose colonies" multiple/>
      </div>

      <n-tabs v-model:value="exchangeType" type="line" animated>
        <n-tab-pane name="arbitrary" tab="销毁物品 → 任意投入">
        </n-tab-pane>
        <n-tab-pane name="wild" tab="特化百搭方块 → 特定方块">
        </n-tab-pane>
      </n-tabs>
      <template v-if="dealingArbitrary">
        <div class="exchange-item-description">任意投入指的是一种特殊的彩色方块投入，通常仅用于联合体的特定转换器，请检查你是否真的需要它们！</div>
        <div class="exchange-item-description">注意：任意投入将不再能转换回普通物品！</div>
      </template>
      <template v-else>
        <div class="exchange-item-description">注意：百搭方块转换为特定方块后将不能再转换回百搭方块！</div>
        <div class="exchange-item-description">恩尼艾特的利息转换器不需要预先转换。</div>
      </template>
      <div class="exchange-item-container" v-if="Object.values(getItem()).some(count => count > 0)">
        <template v-for="(count, item) in getItem()" :key="item">
          <div class="exchange-item-entry" v-if="count > 0">
            <ItemEntryDiv :item="item as string" :count="count" :iconWidth="60" :iconHeight="60" />
            <n-button @click="removeItem(item as string)" circle type="error" size="tiny" class="remove-item-button">-</n-button>
          </div>
        </template>
      </div>
      <div class="exchange-item-input"> 
        <n-select v-model:value="newArbitraryItem" :options="getItemOptions()" placeholder="Choose an item" />
        <n-input-number v-model:value="newArbitraryItemCount" :min="1" :max="getItemRestriction(newArbitraryItem)" />
        <n-button @click="addItem" :disabled="getItemRestriction(newArbitraryItem) < newArbitraryItemCount">添加</n-button>
      </div>
      <n-button class="submit-exchange-button" @click="submitExchange" type="primary" :disabled="!checkSubmit()">确认</n-button>
      <n-button class="close-exchange-button" @click="submitClose" type="error">取消</n-button>
    </n-card>
  </PanelTemplate>
</template>

<style>
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
.exchange-item-title {
  font-size: 1.2rem;
  font-weight: bold;
}
.exchange-item-description {
  font-size: 0.8rem;
  color: #ff0000;
}
.exchange-item-container {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  border: 1px solid #cccccc;
  padding: 10px;
  border-radius: 10px;
  background-color: #f0f0f0;
}
.exchange-item-entry {
  position: relative;
  display: flex;
  flex-direction: row;
  align-items: center;
  margin: 5px;
  border: 1px solid #cccccc;
  border-radius: 5px;
  background-color: #ffffff;
}
.exchange-item-input {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}
.remove-item-button {
  position: absolute;
  top: -5px;
  right: -5px;
}
</style>
