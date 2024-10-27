<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { defineProps } from 'vue';
import { type Factory, type GameState, type Player } from '../interfaces/GameState';
import FactoryDisplayer, { type FactoryConfig } from '@/components/FactoryDisplayer.vue';
import StorageDisplayer from '@/components/StorageDisplayer.vue';
import GamePanel from '@/components/GamePanel.vue';
import TradePanel from '@/components/TradePanel.vue';
import BidPanel from '@/components/BidPanel.vue';
import ResearchPanel from '@/components/ResearchPanel.vue';
import { socket } from '@/utils/connect';
import { NFloatButton } from 'naive-ui';

export interface GameProps {
  scaleFactor: number;
  offsetX: number;
  offsetY: number;
}

const props = defineProps<{
  gameProps: GameProps;
  updateGameProps: (props: GameProps) => void;
  gameState: GameState;
  username: string;
}>();

const stageConfig = ref({
  width: window.innerWidth,
  height: window.innerHeight,
});

const handleRightClickDrag = (event: MouseEvent) => {
  if (event.button === 0) {
    // event.preventDefault();
    let startX = event.clientX;
    let startY = event.clientY;

    const onMouseMove = (moveEvent: MouseEvent) => {
      const deltaX = moveEvent.clientX - startX;
      const deltaY = moveEvent.clientY - startY;
      props.updateGameProps({
        ...props.gameProps,
        offsetX: props.gameProps.offsetX + deltaX,
        offsetY: props.gameProps.offsetY + deltaY,
      });
      startX = moveEvent.clientX;
      startY = moveEvent.clientY;
    };

    const onMouseUp = () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  }
};

const handleWheel = (event: WheelEvent) => {
  const scaleDelta = event.deltaY < 0 ? 2: -2;
  props.updateGameProps({
    ...props.gameProps,
    scaleFactor: Math.max(5, Math.min(200, props.gameProps.scaleFactor + scaleDelta)),
  });
};

const handleResize = () => {
  stageConfig.value.width = window.innerWidth;
  stageConfig.value.height = window.innerHeight;
};

window.addEventListener('wheel', handleWheel);
window.addEventListener('mousedown', handleRightClickDrag);
window.addEventListener('resize', handleResize);

onUnmounted(() => {
  window.removeEventListener('wheel', handleWheel);
  window.removeEventListener('mousedown', handleRightClickDrag);
  window.removeEventListener('resize', handleResize);
});

const selectedPlayer = ref(props.username);
const handleSelectPlayer = (playerId: string) => {
  selectedPlayer.value = playerId;
};

watch(() => props.username, (newUsername) => {
  selectedPlayer.value = newUsername;
});

const factoryWidth = 300;
const factoryHeight = 200;

const getMe = (): Player | null => {
  return getPlayer(props.username);
}

const getPlayer = (playerId: string): Player | null => {
  let res = null;
  for (let player in props.gameState.players) {
    if (props.gameState.players[player].user_id === playerId) {
      res = props.gameState.players[player];
    }
  }
  if (res === null) {
    console.log("player", playerId, "not found");
  }
  return res;
}

const checkFactoryAffordability = (player: Player, factory: Factory) => {
  if (player === null) {
    return false;
  }
  if (factory.feature.type === 'Normal') {
    for (let item in factory.input_items) {
      if (player.storage[item] < factory.input_items[item]) {
        return false;
      }
    }
  } else if (factory.feature.type === 'Research') {
    for (let cost of factory.feature.properties['research_cost']) {
      let affordable = true;
      for (let item in cost) {
        if (player.storage[item] < cost[item]) {
          affordable = false;
        }
      }
      if (affordable) {
        return true;
      }
    }
    return false;
  }
  return true;
}

const produce = (factoryName: string) => {
  socket.emit("produce", {
    room_name: props.gameState.room_name,
    username: props.username,
    factory_name: factoryName
  });
}

const research = (factory: Factory) => {
  handleResearchPanel(factory);
}

const getFactoryConfig = (me: Player, factory: string, x: number, y: number): FactoryConfig => {
  return {
    x: x,
    y: y,
    width: factoryWidth * props.gameProps.scaleFactor / 100,
    height: factoryHeight * props.gameProps.scaleFactor / 100,
    scaleFactor: props.gameProps.scaleFactor,
    factory: me.factories[factory],
    owner: me.factories[factory].owner,
    producible: checkFactoryAffordability(me, me.factories[factory]),
    gameState: props.gameState,
    produce: () => produce(factory),
    research: () => research(me.factories[factory])
  }
}

const getFactoryConfigs = (): {[key: string]: FactoryConfig} => {
  const me = getPlayer(selectedPlayer.value);
  if (me === null) {
    return {};
  }
  const configs: {[key: string]: FactoryConfig} = {};
  let xOffset = 0;
  let xCnt = 0;
  let yOffset = 300 * props.gameProps.scaleFactor / 100;
  for (let factory in me.factories) {
    configs[factory] = getFactoryConfig(me, factory, 
      xOffset + props.gameProps.offsetX, 
      yOffset + props.gameProps.offsetY
    );
    xOffset += (factoryWidth + 50) * props.gameProps.scaleFactor / 100;
    // if (xOffset + (factoryWidth + 50) * props.gameProps.scaleFactor / 100 > stageConfig.value.width) {
    if (xCnt++ >= 2) {
      xCnt = 0;
      xOffset = 0;
      yOffset += (factoryHeight + 50) * props.gameProps.scaleFactor / 100;
    }
  }
  return configs;
}

const getStorage = (): {[key: string]: number} => {
  const me = getMe();
  if (me === null) {
    return {};
  }
  return me.storage;
}


const displayTradePanel = ref(false);
const handleTradePanel = () => {
  if (!displayTradePanel.value) {
    displayTradePanel.value = true;
  } else {
    console.log("trade panel already displayed");
  }
};
const submitTrade = (items: { [key: string]: number }, factories: string[], toWhom: string) => {
  socket.emit("trade-items", {
    room_name: props.gameState.room_name,
    username: props.username,
    items: items,
    to: toWhom
  });
  socket.emit("lend-factories", {
    room_name: props.gameState.room_name,
    username: props.username,
    factories: factories,
    to: toWhom
  });
};

const tradeItems = ref<{ [key: string]: number }>({});
const updateTradeItems = (items: { [key: string]: number }) => {
  tradeItems.value = items;
};

const closeTradePanel = () => {
  displayTradePanel.value = false;
  tradeItems.value = {};
};


const displayResearchPanel = ref(false);
const researchFactory = ref<Factory | null>(null);
const handleResearchPanel = (factory: Factory) => {
  if (!displayResearchPanel.value) {
    displayResearchPanel.value = true;
    researchFactory.value = factory;
  } else {
    console.log("research panel already displayed");
  }
};

const submitResearch = (factoryName: string, costType: number) => {
  socket.emit("produce", {
    room_name: props.gameState.room_name,
    username: props.username,
    factory_name: factoryName,
    extra_properties: {
      cost_type: costType
    }
  });
}

const closeResearchPanel = () => {
  displayResearchPanel.value = false;
  researchFactory.value = null;
}

const displayBidPanel = ref(false);
const openBidPanel = () => {
  displayBidPanel.value = true;
}

watch(() => props.gameState.stage, (newStage) => {
  displayBidPanel.value = (newStage === "Bid");
});
const submitBid = (colonyBid: number, researchBid: number) => {
  socket.emit("bid", {
    room_name: props.gameState.room_name,
    username: props.username,
    colony_bid: colonyBid,
    research_bid: researchBid
  });
}

const closeBidPanel = () => {
  displayBidPanel.value = false;
}

const displayMask = () => {
  return displayTradePanel.value || displayResearchPanel.value || displayBidPanel.value;
};

</script>


<template>
  <GamePanel :game-state="props.gameState" 
    :username="props.username" 
    :handle-trade-panel="handleTradePanel" 
    :selected-player="selectedPlayer"
    :handle-select-player="handleSelectPlayer"
    class="game-panel"/>
  <div class="game-stage">
    <v-stage :config="stageConfig" class="game-stage-canvas">
      <v-layer>
        <v-rect :config="{ x: 0, y: 0, width: stageConfig.width, height: stageConfig.height, fill: 'white' }" />
        <template v-for="factory in getFactoryConfigs()" :key="factory.id">
          <FactoryDisplayer :="factory" />
        </template>
      </v-layer>
    </v-stage>
  </div>
  <div v-if="displayMask()" class="mask">
    <TradePanel :submit-trade="submitTrade" 
      :update-trade-items="updateTradeItems" 
      :trade-items="tradeItems" 
      :close-trade-panel="closeTradePanel" 
      :username="props.username"
      :game-state="props.gameState"
      :selected-player="selectedPlayer"
      :handle-select-player="handleSelectPlayer"
      v-if="displayTradePanel"
    />
    <ResearchPanel :submit-research="submitResearch" 
      :close-research-panel="closeResearchPanel" 
      :username="props.username"
      :factory="researchFactory!"
      :game-state="props.gameState"
      v-if="displayResearchPanel"
    />
    <BidPanel :submit-bid="submitBid" 
      :close-bid-panel="closeBidPanel" 
      :game-state="props.gameState"
      :get-factory-config="getFactoryConfig"
      :username="props.username"
      v-if="displayBidPanel"
    />
  </div>
  <n-float-button 
    @click="openBidPanel" 
    v-if="props.gameState.stage === 'bid'" 
    :top="10"
    :right="10"
    :style="{ zIndex: 101 }"
  >
    <template #description>Bid</template>
  </n-float-button>
</template>

<style scoped>
.game-stage {
  position: absolute;
  top: 0;
  left: 250px;
  width: calc(100vw - 250px);
  height: 100vh;
  overflow: hidden;
  z-index: 10;
}
.game-stage-canvas {
  overflow: hidden;
}

.game-panel {
  height: 100vh;
  z-index: 100;
}
.mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>