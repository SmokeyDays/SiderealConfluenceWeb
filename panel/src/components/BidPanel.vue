<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NPopover, NInputNumber, NCard } from 'naive-ui';
import type { Factory, GameState, Player } from '@/interfaces/GameState';
import type { FactoryConfig } from './FactoryDisplayer.vue';

const props = defineProps<{
  submitBid: (colonyBid: number, researchBid: number) => void;
  closeBidPanel: () => void;
  getFactoryConfig: (me: Player, factory: string, x: number, y: number) => FactoryConfig;
  username: string;
  gameState: GameState;
}>();

const colonyBid = ref(0);
const researchBid = ref(0);

const submitBid = () => {
  props.submitBid(colonyBid.value, researchBid.value);
  submitClose();
};

const submitClose = () => {
  colonyBid.value = 0;
  researchBid.value = 0;
  props.closeBidPanel();
};


</script>

<template>
  <n-card hoverable class="bid-panel">
    <div class="bid-cards">
      <div class="colony-bid-cards">
        <div v-for="card in props.gameState.colony_bid_cards" :key="card.price">
          <n-popover>
            <template #trigger>
              <n-button-group>
                <n-button class="bid-entry">{{ card.item?.name }}</n-button>
                <n-button quaternary class="bid-entry">{{ card.price }}</n-button>
              </n-button-group>
            </template>
            <v-stage :config="{ width: 200, height: 200 }">
              <v-layer>
                <v-rect :config="{ x: 20, y: 20, width: 160, height: 160, fill: 'blue' }" />
              </v-layer>
            </v-stage>
          </n-popover>
        </div>
        <n-input-number v-model:value="colonyBid" placeholder="Colony Bid" />
      </div>
      <div class="bid-divider"></div>
      <div class="research-bid-cards">
        <div v-for="card in props.gameState.research_bid_cards" :key="card.price">
          <n-popover>
            <template #trigger>
              <n-button-group>  
                <n-button quaternary class="bid-entry">{{ card.price }}</n-button>
                <n-button class="bid-entry">{{ card.item?.name }}</n-button>
              </n-button-group>
            </template>
            <Stage :config="{ width: 200, height: 200 }">
              <Layer>
                <Rect :config="{ x: 20, y: 20, width: 160, height: 160, fill: 'red' }" />
              </Layer>
            </Stage>
          </n-popover>
        </div>
        <n-input-number v-model:value="researchBid" placeholder="Research Bid" />
      </div>
    </div>
    <div class="bid-inputs">
      <n-button class="submit-bid-button" @click="submitBid" type="primary">Submit Bid</n-button>
      <n-button class="close-bid-button" @click="submitClose" type="error">Close</n-button>
    </div>
  </n-card>
</template>

<style>
.bid-panel {
  width: 40vw;
  height: 75vh;
}
.bid-cards {
  display: flex;
  justify-content: space-between;
}
.bid-inputs {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}
.colony-bid-cards {
  display: flex;
  align-items: flex-end;
  flex-direction: column;
  width: calc(50% - 2px)
}
.bid-divider {
  width: 2px;
  background-color: #604c4c;
}
.research-bid-cards {
  display: flex;
  align-items: flex-start;
  flex-direction: column;
  width: calc(50% - 2px)
}
.close-bid-button {
  position: absolute;
  bottom: 40px;
  right: 40px;
}
.submit-bid-button {
  position: absolute;
  bottom: 40px;
  right: 120px;
}
</style>
