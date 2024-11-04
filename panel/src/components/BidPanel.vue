<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NPopover, NInputNumber, NCard } from 'naive-ui';
import type { GameState, Player, Factory } from '@/interfaces/GameState';
import type { FactoryConfig } from '@/components/FactoryDisplayer.vue';
import FactoryDisplayer from '@/components/FactoryDisplayer.vue';
import { getSpecieZhName } from '@/interfaces/GameConfig';

const props = defineProps<{
  submitBid: (colonyBid: number, researchBid: number) => void;
  submitPick: (type: string, id: number) => void;
  closeBidPanel: () => void;
  getFactoryConfig: (me: Player, factory: Factory, x: number, y: number) => FactoryConfig;
  getMe: () => Player | null;
  getPlayer: (playerId: string) => Player | null;
  username: string;
  gameState: GameState;
}>();

const colonyBid = ref(0);
const researchBid = ref(0);
const pick = ref(-1);

const submitBid = () => {
  props.submitBid(colonyBid.value, researchBid.value);
  submitClose();
};

const submitClose = () => {
  colonyBid.value = 0;
  researchBid.value = 0;
  pick.value = -1;
  // props.closeBidPanel();
};

const getBidMax = () => {
  const me = props.getMe();
  if (!me) return 0;
  return me.storage["Ship"];
}

const getResearchBidMax = () => {
  return getBidMax() - colonyBid.value;
}

const getColonyBidMax = () => {
  return getBidMax() - researchBid.value;
}

const bidLegal = () => {
  const affordable = colonyBid.value + researchBid.value <= getBidMax();
  return affordable;
}

const bidNotSubmitted = () => {
  return props.gameState.stage === 'bid' && !props.gameState.players.find(player => player.user_id === props.username)?.agreed;
}
const isCurrentPick = () => {
  return props.gameState.current_pick?.player === props.username && props.gameState.stage === "pick";
}

const maySelect = (type: string, price: number) => {
  if (isCurrentPick()) {
    const me = props.getMe();
    if (!me) return false;
    const bidNum = type === "colony" ? me.colony_bid : me.research_bid;
    return type === props.gameState.current_pick?.type && price <= bidNum;
  }
  return false;
}

const submitPick = () => {
  props.submitPick(props.gameState.current_pick.type, pick.value);
  submitClose();
}

</script>

<template>
  <n-card hoverable class="bid-panel">
    <div class="bid-info" v-if="props.gameState.stage === 'bid'">
      选择你的出价
    </div>
    <div class="bid-info" v-if="props.gameState.stage === 'bid' && props.getMe()?.specie === 'Caylion'">
      作为凯利安，你的出价将折半
    </div>
    <div class="pick-info" v-if="props.gameState.stage === 'pick'">
      由{{ getSpecieZhName(props.getPlayer(props.gameState.current_pick.player)?.specie || 'None') }}选择{{ props.gameState.current_pick.type === "colony" ? "殖民地" : "科研团队" }}
    </div>
    <div class="bid-cards">
      <div class="colony-bid-cards">
        <div class="bid-title">
          殖民地拍卖
        </div>
        <div v-for="id in Object.keys(props.gameState.colony_bid_cards).map(Number)" :key="id">
          <n-popover placement="left">
            <template #trigger>
              <n-button-group>
                <n-button 
                  class="bid-entry" 
                  v-if="props.gameState.colony_bid_cards[id].item" 
                  :disabled="!maySelect('colony', props.gameState.colony_bid_cards[id].price)"
                  :type="(pick === id && maySelect('colony', props.gameState.colony_bid_cards[id].price)) ? 'primary' : 'default'"
                  @click="pick === id ? pick = -1 : pick = id"
                >{{ props.gameState.colony_bid_cards[id].item?.name }}</n-button>
                <n-button quaternary class="bid-entry">{{ props.gameState.colony_bid_cards[id].price }}</n-button>
              </n-button-group>
            </template>
            <v-stage :config="{ width: 300, height: 200 }">
              <v-layer>
                <FactoryDisplayer v-if="props.gameState.colony_bid_cards[id].item" :="getFactoryConfig(props.getMe()!, props.gameState.colony_bid_cards[id].item!, 0, 0)" />
              </v-layer>
            </v-stage>
          </n-popover>
        </div>
        <n-input-number v-model:value="colonyBid" placeholder="Colony Bid" :min="0" :max="getColonyBidMax()" v-if="bidNotSubmitted()" />
      </div>
      <div class="bid-divider"></div>
      <div class="research-bid-cards">
        <div class="bid-title">
          科研团队拍卖
        </div>
        <div v-for="id in Object.keys(props.gameState.research_bid_cards).map(Number)" :key="id">
          <n-popover placement="right">
            <template #trigger>
              <n-button-group>  
                <n-button quaternary class="bid-entry">{{ props.gameState.research_bid_cards[id].price }}</n-button>
                <n-button 
                  class="bid-entry" 
                  v-if="props.gameState.research_bid_cards[id].item" 
                  :disabled="!maySelect('research', props.gameState.research_bid_cards[id].price)"
                  :type="(pick === id && maySelect('research', props.gameState.research_bid_cards[id].price)) ? 'primary' : 'default'"
                  @click="pick === id ? pick = -1 : pick = id"
                >{{ props.gameState.research_bid_cards[id].item?.name }}</n-button>
              </n-button-group>
            </template>
            <v-stage :config="{ width: 300, height: 200 }"> 
              <v-layer>
                <FactoryDisplayer v-if="props.gameState.research_bid_cards[id].item" :="getFactoryConfig(props.getMe()!, props.gameState.research_bid_cards[id].item!, 0, 0)" />
              </v-layer>
            </v-stage>
          </n-popover>
        </div>
        <n-input-number v-model:value="researchBid" placeholder="Research Bid" :min="0" :max="getResearchBidMax()" v-if="bidNotSubmitted()" />
      </div>
    </div>
    <div class="bid-inputs">
      <n-button class="submit-bid-button" 
        @click="submitBid" 
        type="primary" 
        v-if="bidNotSubmitted()" 
        :disabled="!bidLegal()"
      >Submit Bid</n-button>
      <n-button class="submit-pick-button" 
        @click="submitPick" 
        type="primary" 
        v-if="isCurrentPick()" 
      >Submit Pick</n-button>
      <n-button class="close-bid-button" @click="props.closeBidPanel" type="error">Close</n-button>
    </div>
  </n-card>
</template>

<style>
.bid-panel {
  width: 60vw;
  height: 75vh;
}
.bid-info {
  font-size: 1.2rem;
  font-style: italic;
  margin: 10px;
}
.pick-info {
  font-size: 1.2rem;
  font-style: italic;
  margin: 10px;
}
.bid-cards {
  width: 100%;
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
  width: calc(50% - 2px);
}
.research-bid-cards {
  display: flex;
  align-items: flex-start;
  flex-direction: column;
  width: calc(50% - 2px);
}
.bid-divider {
  width: 2px;
  background-color: #604c4c;
}
.bid-title {
  font-size: 1.1rem;
  font-weight: bold;
  margin: 10px;
}
.close-bid-button {
  position: absolute;
  bottom: 40px;
  right: 40px;
}
.submit-pick-button {
  position: absolute;
  bottom: 40px;
  right: 120px;
}
.submit-bid-button {
  position: absolute;
  bottom: 40px;
  right: 120px;
}
</style>
