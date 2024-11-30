<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NPopover, NInputNumber, NCard, NTooltip, NButtonGroup } from 'naive-ui';
import type { GameState, Player, Factory } from '@/interfaces/GameState';
import type { FactoryConfig } from '@/components/FactoryDisplayer.vue';
import FactoryDisplayer from '@/components/FactoryDisplayer.vue';
import FactoryDisplayerAsync from '@/components/FactoryDisplayerAsync.vue';
import PanelTemplate from '@/components/panels/PanelTemplate.vue';
import { getSpecieColor, getSpecieZhName } from '@/interfaces/GameConfig';

const props = defineProps<{
  submitBid: (colonyBid: number, researchBid: number) => void;
  submitPick: (type: string, id: number) => void;
  closeBidPanel: () => void;
  getFactoryConfig: (me: Player, factory: Factory, x: number, y: number) => FactoryConfig;
  getMe: () => Player | null;
  getPlayer: (playerId: string) => Player | null;
  username: string;
  roomName: string;
  gameState: GameState;
  submitKajsjavikalimmChooseSplit: (chooseSplit: boolean) => void;
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
    let bidNum = props.gameState.current_pick?.bid;
    return type === props.gameState.current_pick?.type && price <= bidNum;
  }
  return false;
}

const submitPick = () => {
  props.submitPick(props.gameState.current_pick.type, pick.value);
  submitClose();
}

const submitKajsjavikalimmChooseSplit = (chooseSplit: boolean) => {
  props.submitKajsjavikalimmChooseSplit(chooseSplit);
}

const getCurrentPickPriority = () => {
  if (props.gameState.current_pick.type === "colony") {
    return props.gameState.colony_bid_priority;
  }
  return props.gameState.research_bid_priority;
}

const getIsPortrait = () => {
  return window.innerWidth < window.innerHeight;
}
</script>

<template>
  <PanelTemplate>
    <n-card hoverable class="bid-panel standard-panel">
    <div class="bid-info" v-if="props.gameState.stage !== 'bid' && props.gameState.stage !== 'pick'">
      预览本轮的拍卖
    </div>
    <div class="bid-info" v-if="props.gameState.stage === 'bid'">
      选择你的出价
    </div>
    <div class="bid-info" v-if="props.gameState.stage === 'bid' && props.getMe()?.specie === 'Caylion'">
      作为凯利安，你的出价将折半
    </div>
    <div class="pick-info" v-if="props.gameState.stage === 'pick' && props.gameState.Kajsjavikalimm_choose_split !== null">
      由{{ getSpecieZhName(props.getPlayer(props.gameState.current_pick.player)?.specie || 'None') }}选择{{ props.gameState.current_pick.type === "colony" ? "殖民地" : "科研团队" }}
    </div>
    <div class="pick-info" v-if="props.gameState.stage === 'pick' && props.gameState.Kajsjavikalimm_choose_split === null">
      贾斯可以选择是否将殖民地出价分成尽可能相等的两部分参加竞拍
    </div>
    <div class="bid-cards">
      <div class="colony-bid-cards">
        <div class="bid-title">
          殖民地拍卖
        </div>
        <div v-for="id in Object.keys(props.gameState.colony_bid_cards).map(Number)" :key="id">
          <n-popover :placement="getIsPortrait() ? 'top' : 'left'">
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
            <template v-if="props.gameState.colony_bid_cards[id].item">
              <FactoryDisplayerAsync 
                :room-name="props.roomName" 
                :me="props.getMe()!" 
                :factory="props.gameState.colony_bid_cards[id].item!.name" 
                :get-factory-config="getFactoryConfig" 
              />
            </template>
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
          <n-popover :placement="getIsPortrait() ? 'top' : 'left'">
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
            <template v-if="props.gameState.research_bid_cards[id].item">
              <FactoryDisplayerAsync 
                :room-name="props.roomName" 
                :me="props.getMe()!" 
                :factory="props.gameState.research_bid_cards[id].item!.name" 
                :get-factory-config="getFactoryConfig" 
              />
            </template>
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
    <div class="bid-details" v-if="props.gameState.stage === 'pick'">
      <div class="bid-details-title">{{ props.gameState.current_pick.type === "colony" ? "殖民地" : "科研团队" }}的出价</div>
      <div class="bid-details-content">
        <template v-for="item in getCurrentPickPriority()" :key="item.player">
          <div class="bid-details-item" :style="{ color: getSpecieColor(props.getPlayer(item.player)?.specie || 'None') }">
            <div class="bid-details-item-player">{{ getSpecieZhName(props.getPlayer(item.player)?.specie || 'None') }}出价</div>
            <n-tooltip>
              <template #trigger>
                <div class="bid-details-item-bid">{{ -item.bid[0] }}</div>
              </template>
              <div>第一关键字：出价高的优先</div>
            </n-tooltip>
            <div class="bid-details-item-extra">
              <n-tooltip>
                <template #trigger> 
                  <div class="bid-details-item-num">{{ item.bid[1] }}</div>
                </template>
                <div>第二关键字：已拥有的数量少的优先</div>
              </n-tooltip>
              <n-tooltip>
                <template #trigger>
                  <div class="bid-details-item-tiebreaker">{{ -item.bid[2] }}</div>
                </template>
                <div>第三关键字：平手决胜高的优先</div>
              </n-tooltip>
            </div>
          </div>
        </template>
      </div>
    </div>
    <template v-if="props.gameState.stage === 'pick' && props.getMe()?.specie === 'Kjasjavikalimm' && props.gameState.Kajsjavikalimm_choose_split === null">
        <n-button @click="submitKajsjavikalimmChooseSplit(true)" type="primary" class="kajsjavikalimm-choose-split-button-yes">拆分</n-button>
        <n-button @click="submitKajsjavikalimmChooseSplit(false)" type="error" class="kajsjavikalimm-choose-split-button-no">不拆分</n-button>
    </template>
    </n-card>
  </PanelTemplate>
</template>

<style>
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
.kajsjavikalimm-choose-split-button-yes {
  position: absolute;
  bottom: 40px;
  left: 40px;
}
.kajsjavikalimm-choose-split-button-no {
  position: absolute;
  bottom: 40px;
  left: 120px;
}
.bid-details-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  /* border: 1px solid #000000; */
  border-radius: 10px;
  background-color: #eeeeee;
  box-shadow: 0 0 10px 0 rgba(246, 255, 0, 0.5);
  margin: 5px;
  padding: 5px;
}
.bid-details-title {
  font-size: 1.2rem;
  font-weight: bold;
  margin: 10px;
}
.bid-details-item-player {
  font-size: 0.9rem;
  font-weight: bold;
}
.bid-details-content {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}
.bid-details-item-bid {
  font-size: 2rem;
  font-weight: bold;
  margin: -10px;
}
.bid-details-item-extra {
  margin: -5px;
  width: 80%;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
</style>
