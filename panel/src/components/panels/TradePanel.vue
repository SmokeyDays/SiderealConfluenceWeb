<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NInputNumber, NSelect, NCard, NTabs, NTabPane, NTooltip, NInput } from 'naive-ui';
import { getItemOption, getSpecieColor, getSpecieZhName, items } from '@/interfaces/GameConfig';
import ItemEntryDiv from '@/components/ItemEntryDiv.vue';
import { Gift, TradeProposal, type GameState } from '@/interfaces/GameState';
import PanelTemplate from '@/components/panels/PanelTemplate.vue';
import ProposalDiv from '@/components/ProposalDiv.vue';

const props = defineProps<{
  submitGift: (gift: Gift, toWhom: string) => void;
  submitProposal: (sendGift: Gift, receiveGift: Gift, receivers: string[], message: string) => void;
  closeTradePanel: () => void;
  declineProposal: (proposal_id: number) => void;
  acceptProposal: (proposal_id: number) => void;
  username: string;
  gameState: GameState;
}>();
const defaultItem = "Food";
const defaultItemCount = 1;
const newItem = ref(defaultItem);
const newItemCount = ref(defaultItemCount);
const sendGift = ref(new Gift({}, [], []));
const receiveGift = ref(new Gift({}, [], []));
const toWhom = ref("Choose a player");
const proposalMessage = ref("");
const receivers = ref<string[]>([]);
const tab = ref("market");
const gift_type = ref("send");

const getGift = () => {
  if (gift_type.value === "send") {
    return sendGift.value;
  }
  return receiveGift.value;
}

const updateGift = (gift: Gift) => {
  if (gift_type.value === "send") {
    sendGift.value = gift;
  } else {
    receiveGift.value = gift;
  }
}

const addItem = () => {
  if (newItem.value !== "" && newItemCount.value > 0) {
    const gift = getGift();
    if (gift.items[newItem.value] === undefined) {
      gift.items[newItem.value] = newItemCount.value;
    } else {
      gift.items[newItem.value] += newItemCount.value;
    }
    updateGift(gift);
  }
};

const submitGift = () => {
  props.submitGift(getGift(), toWhom.value);
  submitClose();
};

const submitProposal = () => {
  props.submitProposal(sendGift.value, receiveGift.value, receivers.value, proposalMessage.value);
  submitClose();
};

const getCurrentProposal = () => {
  const proposal = new TradeProposal(0, props.username, receivers.value, sendGift.value, receiveGift.value, proposalMessage.value);
  return proposal;
}

const submitClose = () => {
  newItem.value = defaultItem;
  newItemCount.value = defaultItemCount;
  props.closeTradePanel();
};

const getItemRestriction = (item: string) => {
  if (item === "Score") {
    return 0;
  }
  if (gift_type.value === "receive") {
    return 1000000;
  }
  const myStorage = props.gameState.players.find(player => player.user_id === props.username)?.storage;
  if (myStorage === undefined) {
    return 0;
  }
  let myStorageItem = myStorage[item] || 0;
  return myStorageItem - (getGift().items[item] || 0);
}

const getItemOptions = () => {
  const res: { label: string, value: string }[] = [];
  items.forEach(item => {
    if (getItemRestriction(item) > 0) {
      res.push(getItemOption(item));
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
  if (gift_type.value === "receive") {
    for (const player of props.gameState.players) {
      if (player.user_id === props.username) {  
        continue;
      }
      for (const factory of Object.values(player.factories)) {
        res.push({ label: `[${getSpecieZhName(player.specie)}]` + factory.name, value: factory.name });
      }
    }
  } else if (gift_type.value === "send") {
    const myFactories = props.gameState.players.find(player => player.user_id === props.username)?.factories;
    if (myFactories === undefined) {
      return res;
    }
    for (const factory of Object.values(myFactories)) {
      res.push({ label: factory.name, value: factory.name });
    }
  }
  return res;
}

const removeItem = (item: string) => {
  const gift = getGift();
  gift.items[item] = 0;
  updateGift(gift);
}

const getGrantableTechs = () => {
  const me = props.gameState.players.find(player => player.user_id === props.username);
  if (!me) {
    return [];
  }
  if (gift_type.value === "receive") {
    const techs: string[] = [];
    for (const player of props.gameState.players) {
      if (receivers.value.includes(player.user_id)) {
        techs.push(...player.tech);
      }
    }
    return techs.filter(tech => !me.tech.includes(tech));
  } else if (gift_type.value === "send") {
    const to = props.gameState.players.find(player => player.user_id === toWhom.value);
    if (me && !to) {
      return me.invented_tech;
    } else if (me && to) {
      return me.invented_tech.filter(tech => !to.tech.includes(tech));
    } 
  }
  return [];
}

const getTechOptions = () => {
  return getGrantableTechs().map(tech => ({ label: tech, value: tech }));
}

const checkSubmit = () => {
  const me = props.gameState.players.find(player => player.user_id === props.username);
  if (!me) {
    return false;
  }
  if (tab.value === "trade") {
    if (receivers.value.length === 0) {
      return false;
    }
    return true;
  }
  const to = props.gameState.players.find(player => player.user_id === toWhom.value);
  if (!to) {
    return false;
  }
  const gift = getGift();
  for (const item of Object.keys(gift.items)) {
    if (getItemRestriction(item) < 0) {
      return false;
    }
  }
  for (const tech of gift.techs) {
    if (!me.invented_tech.includes(tech) || to.tech.includes(tech)) {
      return false;
    }
  }
  return true;
}

const onTabChange = (value: string) => {
  if (value === "gift") {
    gift_type.value = "send";
  }
}
</script>

<template>
  <PanelTemplate>
    <n-card hoverable class="trade-panel">
      <div class="trade-panel-content">
        <n-tabs v-model:value="tab" type="line" animated @update:value="onTabChange">
          <n-tab-pane name="market" tab="市场">
            <div class="trade-item-title">市场上的提议：</div>
            <div class="proposal-container">
              <template v-for="player in props.gameState.players" :key="player.user_id">
                <template v-for="proposal in props.gameState.proposals[player.user_id]" :key="proposal.id">
                  <ProposalDiv 
                    :proposal="proposal"
                    :declineProposal="proposal.from_player === props.username ? () => {
                      props.declineProposal(proposal.id);
                    } : undefined"
                    :acceptProposal="proposal.to_players.includes(props.username) ? () => {
                      props.acceptProposal(proposal.id);
                    } : undefined"
                  />
                </template>
              </template>
            </div>
          </n-tab-pane>
          <n-tab-pane name="gift" tab="赠送">
            <div class="trade-item-title">赠送如下物品：</div>
          </n-tab-pane>
          <n-tab-pane name="trade" tab="交易">
            <n-tabs v-model:value="gift_type" type="line" animated>
              <n-tab-pane name="send" tab="希望用……"></n-tab-pane>
              <n-tab-pane name="receive" tab="换取……"></n-tab-pane>
            </n-tabs>
            <div class="trade-item-title">如下物品：</div>
          </n-tab-pane>
        </n-tabs>
        <template v-if="tab === 'gift' || tab === 'trade'">
          <div class="trade-item-container" v-if="Object.values(getGift().items).some(count => count > 0)">
            <template v-for="(count, item) in getGift().items" :key="item">
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
          <div class="trade-item-title">并借出（若绑定种族）或给予如下工厂：</div>
          <n-select v-model:value="getGift().factories" :options="getFactoryOptions()" multiple placeholder="选择一个工厂" />
          <div class="trade-item-title">并授权如下科技的专利：</div>
          <n-select v-model:value="getGift().techs" :options="getTechOptions()" multiple placeholder="选择一个科技" />
        </template>
        <template v-if="tab === 'gift'">
          <n-button class="submit-trade-button" @click="submitGift" type="primary" :disabled="!checkSubmit()">赠送</n-button>
          <div class="to-whom-container">
            <p style="font-size: 1.2rem; font-weight: bold;">赠送给：</p>
            <n-select v-model:value="toWhom" :options="getPlayerOptions()" placeholder="Choose a player" />
          </div>
        </template>
        <template v-if="tab === 'trade'">
          <div class="trade-item-title">并备注信息：</div>
          <n-input v-model:value="proposalMessage" placeholder="输入备注信息" type="textarea" :autosize="{ minRows: 1, maxRows: 2 }"/>
          <n-tooltip>
            <template #trigger>
              <n-button class="submit-trade-button" @click="submitProposal" type="primary" :disabled="!checkSubmit()">提交</n-button>
            </template>
            <ProposalDiv :proposal="getCurrentProposal()"/>
          </n-tooltip>
          <div class="potential-receiver-container">
            <p style="font-size: 1.2rem; font-weight: bold;">向以下玩家提议：</p>
            <n-select v-model:value="receivers" :options="getPlayerOptions()" placeholder="Choose a player" multiple />
          </div>
        </template>
        <n-button class="close-trade-button" @click="submitClose" type="error">关闭</n-button>
      </div>
    </n-card>
  </PanelTemplate>
</template>

<style>
.trade-panel {
  width: 60vw;
}
.trade-panel-content {
  overflow: auto;
  padding-bottom: 100px;
  height: 75vh;
}
.proposal-container {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
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
.potential-receiver-container {
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
