<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NInputNumber, NSelect, NCard } from 'naive-ui';
import { getSpecieColor, items } from '@/interfaces/GameConfig';
import ItemEntryDiv from '@/components/ItemEntryDiv.vue';
import { socket } from '@/utils/connect';
import type { GameState } from '@/interfaces/GameState';

const props = defineProps<{
  submitTrade: (items: { [key: string]: number }, factories: string[], toWhom: string) => void;
  updateTradeItems: (items: { [key: string]: number }) => void;
  closeTradePanel: () => void;
  tradeItems: { [key: string]: number };
  username: string;
  gameState: GameState;
}>();
const defaultItem = "Food";
const defaultItemCount = 1;
const newItem = ref(defaultItem);
const newItemCount = ref(defaultItemCount);
const factories = ref([]);
const toWhom = ref("Choose a player");

const addItem = () => {
  if (newItem.value !== "" && newItemCount.value > 0) {
    if (props.tradeItems[newItem.value] === undefined) {
      props.updateTradeItems({...props.tradeItems, [newItem.value]: newItemCount.value});
    } else {
      props.updateTradeItems({...props.tradeItems, [newItem.value]: props.tradeItems[newItem.value] + newItemCount.value});
    }
  }
};

const submitTrade = () => {
  props.submitTrade(props.tradeItems, factories.value, toWhom.value);
  submitClose();
};

const submitClose = () => {
  newItem.value = defaultItem;
  newItemCount.value = defaultItemCount;
  props.closeTradePanel();
};

const getItemRestriction = (item: string) => {
  const myStorage = props.gameState.players.find(player => player.user_id === props.username)?.storage;
  if (myStorage === undefined) {
    return 0;
  }
  const myDonation = props.gameState.players.find(player => player.user_id === props.username)?.donation_items;
  if (myDonation === undefined) {
    return myStorage[item] - (props.tradeItems[item] || 0);
  }
  return (myStorage[item] || 0) + (myDonation[item] || 0) - (props.tradeItems[item] || 0);
}

const getItemOptions = () => {
  const res: { label: string, value: string }[] = [];
  items.forEach(item => {
    console.log(item, getItemRestriction(item));
    if (getItemRestriction(item) > 0) {
      res.push({ label: item, value: item });
    }
  });
  return res;
}

const getPlayerOptions = () => {
  const res: { label: string, value: string, style: { color: string } }[] = [];
  props.gameState.players.forEach(player => {
    if (player.user_id !== props.username) {
    res.push({ 
      label: player.specie + " (" + player.user_id + ")",
        value: player.user_id, 
        style: { color: getSpecieColor(player.specie) } 
      });
    }
  });
  return res;
}

const getFactoryOptions = () => {
  const res: { label: string, value: string }[] = [];
  const myFactories = props.gameState.players.find(player => player.user_id === props.username)?.factories;
  if (myFactories === undefined) {
    return res;
  }
  for (const factory of Object.values(myFactories)) {
    res.push({ label: factory.name, value: factory.name });
  }
  return res;
}

const removeItem = (item: string) => {
  props.updateTradeItems({...props.tradeItems, [item]: 0});
}
</script>

<template>
  <n-card hoverable class="trade-panel">
    <div class="trade-item-title">Trade those items:</div>
    <div class="trade-item-container" v-if="Object.values(tradeItems).some(count => count > 0)">
      <template v-for="(count, item) in tradeItems" :key="item">
        <div class="trade-item-entry" v-if="count > 0">
          <ItemEntryDiv :item="item as string" :count="count" :iconWidth="60" :iconHeight="60" />
          <n-button @click="removeItem(item as string)" circle type="error" size="tiny" class="remove-item-button">-</n-button>
        </div>
      </template>
    </div>
    <div class="trade-item-input"> 
      <n-select v-model:value="newItem" :options="getItemOptions()" placeholder="Choose an item" />
      <n-input-number v-model:value="newItemCount" :min="1" :max="getItemRestriction(newItem)" />
      <n-button @click="addItem" :disabled="getItemRestriction(newItem) < newItemCount">Add Item</n-button>
    </div>
    <div class="trade-item-title">And lend those factories</div>
    <n-select v-model:value="factories" :options="getFactoryOptions()" multiple placeholder="Choose a factory" />

    <n-button class="submit-trade-button" @click="submitTrade" type="primary" :disabled="toWhom === 'Choose a player'">Submit Trade</n-button>
    <n-button class="close-trade-button" @click="submitClose" type="error">Close</n-button>
    <div class="to-whom-container">
      <p style="font-size: 1.2rem; font-weight: bold;">To:</p>
      <n-select v-model:value="toWhom" :options="getPlayerOptions()" placeholder="Choose a player" />
    </div>
  </n-card>
</template>

<style>
.trade-panel {
  width: 40vw;
  height: 75vh;
}
.trade-item-container {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  border: 1px solid #cccccc;
  padding: 10px;
  border-radius: 10px;
  background-color: #f0f0f0;
}
.trade-item-entry {
  position: relative;
  display: flex;
  flex-direction: row;
  align-items: center;
  margin: 5px;
  border: 1px solid #cccccc;
  border-radius: 5px;
  background-color: #ffffff;
}
.remove-item-button {
  position: absolute;
  top: -5px;
  right: -5px;
}
.close-trade-button {
  position: absolute;
  bottom: 40px;
  right: 40px;
}
.submit-trade-button {
  position: absolute;
  bottom: 40px;
  right: 120px;
}
.trade-item-input {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}
.to-whom-container {
  position: absolute;
  bottom: 40px;
  left: 40px;
}
.trade-item-title {
  /* position: absolute;
  top: 40px;
  left: 40px; */
  font-size: 1.2rem;
  font-weight: bold;
}
</style>
