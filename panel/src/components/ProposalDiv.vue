<script lang="ts" setup>
import type { TradeProposal } from '@/interfaces/GameState';
import { NCard, NTag, NButton } from 'naive-ui';
import { getItemsValue } from '@/interfaces/GameConfig';
import ItemEntryDiv from '@/components/ItemEntryDiv.vue';

const props = defineProps<{
  proposal: TradeProposal;
  declineProposal?: () => void;
  acceptProposal?: () => void;
}>();

const getReceivers = () => {
  return props.proposal.to_players.join(", ");
}
</script>


<template>
  <n-card hoverable class="proposal-card">
    <div class="proposal-title">{{ props.proposal.from_player }} 向 {{ getReceivers() }} 发起以下提议：</div>
    <div class="proposal-content">
      <div class="proposal-send">
        <div class="proposal-items">
          <template v-for="(count, item) in props.proposal.send_gift.items" :key="item">
            <ItemEntryDiv :item="item as string" :count="count" :iconWidth="40" :iconHeight="40" />
          </template>
        </div>
        <div class="proposal-factories">
          <template v-for="factory in props.proposal.send_gift.factories" :key="factory">
              <n-tag class="proposal-factory-tag">{{ factory }}</n-tag>
          </template>
        </div>
        <div class="proposal-techs">
          <template v-for="tech in props.proposal.send_gift.techs" :key="tech">
            <n-tag type="info" class="proposal-tech-tag">{{ tech }}的授权</n-tag>
          </template>
        </div>
      </div>
      <div class="proposal-arrow">交换</div>
      <div class="proposal-receive">
        <div class="proposal-items">
          <template v-for="(count, item) in props.proposal.receive_gift.items" :key="item">
            <ItemEntryDiv :item="item as string" :count="count" :iconWidth="40" :iconHeight="40" />
          </template>
        </div>
        <div class="proposal-factories">
          <template v-for="factory in props.proposal.receive_gift.factories" :key="factory">
              <n-tag class="proposal-factory-tag">{{ factory }}</n-tag>
          </template>
        </div>
        <div class="proposal-techs">
          <template v-for="tech in props.proposal.receive_gift.techs" :key="tech">
            <n-tag type="info" class="proposal-tech-tag">{{ tech }}的授权</n-tag>
          </template>
        </div>
      </div>
    </div>
    <template v-if="props.declineProposal">
      <n-button @click="props.declineProposal" class="decline-proposal-button" type="error">撤回提议</n-button>
    </template>
    <template v-if="props.acceptProposal">
      <n-button @click="props.acceptProposal" class="accept-proposal-button" type="success">接受提议</n-button>
    </template>
  </n-card>
</template>

<style scoped>
.proposal-card {
  position: relative;
  width: auto;
  padding-bottom: 25px;
}
.proposal-title {
  font-size: 1rem;
  font-weight: bold;
}
.proposal-content {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
.proposal-send, .proposal-receive {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.proposal-items, .proposal-factories, .proposal-techs {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}
.decline-proposal-button, .accept-proposal-button {
  position: absolute;
  bottom: 5px;
  right: 5px;
}
</style>

