<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch , reactive, type Component } from 'vue';
import { defineProps } from 'vue';
import { Gift, isOnFavorBuff, type Factory, type GameState, type Player } from '../interfaces/GameState';
import FactoryDisplayer, { type FactoryConfig } from '@/components/FactoryDisplayer.vue';
import StorageDisplayer from '@/components/StorageDisplayer.vue';
import GameBoard from '@/components/GameBoard.vue';
import TradePanel from '@/components/panels/TradePanel.vue';
import BidPanel from '@/components/panels/BidPanel.vue';
import EndPanel from '@/components/panels/EndPanel.vue';
import ResearchPanel from '@/components/panels/ResearchPanel.vue';
import ExchangePanel from '@/components/panels/ExchangePanel.vue';
import CheckPanel from '@/components/panels/CheckPanel.vue';
import DiscardColonyPanel from '@/components/panels/DiscardColonyPanel.vue';
import EnietInterestPanel from '@/components/panels/EnietInterestPanel.vue';
import { socket } from '@/utils/connect';
import { NFloatButton, NIcon } from 'naive-ui';
import { arbitraryBigSource, arbitrarySmallSource } from '@/interfaces/GameConfig';
import IconMenu from '@/components/icons/IconMenu.vue';
import FactoryDisplayerAsync from '@/components/FactoryDisplayerAsync.vue';

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
  switchPage: (page: string) => void;
}>();

const stageConfig = ref({
  x: 0,
  y: 0,
  width: window.innerWidth,
  height: window.innerHeight,
  image: new Image(),
});

let gameStage: HTMLElement | null = null;

const handleRightClickDrag = (event: MouseEvent | TouchEvent) => {
  let startX = 0;
  let startY = 0;

  if (event instanceof MouseEvent && event.button === 0) {
    startX = event.clientX;
    startY = event.clientY;
  } else if (event instanceof TouchEvent) {
    startX = event.touches[0].clientX;
    startY = event.touches[0].clientY;
  }

  const onMouseMove = (moveEvent: MouseEvent | TouchEvent) => {
    if(moveEvent instanceof TouchEvent && moveEvent.touches.length !== 1) {
      return;
    }
    let clientX = 0;
    let clientY = 0;

    if (moveEvent instanceof MouseEvent) {
      clientX = moveEvent.clientX;
      clientY = moveEvent.clientY;
    } else if (moveEvent instanceof TouchEvent) {
      clientX = moveEvent.touches[0].clientX;
      clientY = moveEvent.touches[0].clientY;
    }

    const deltaX = clientX - startX;
    const deltaY = clientY - startY;
    props.updateGameProps({
      ...props.gameProps,
      offsetX: props.gameProps.offsetX + deltaX,
      offsetY: props.gameProps.offsetY + deltaY,
    });
    startX = clientX;
    startY = clientY;
  };

  const onMouseUp = () => {
    if (gameStage) {
      gameStage.removeEventListener('mousemove', onMouseMove);
      gameStage.removeEventListener('touchmove', onMouseMove);
      gameStage.removeEventListener('mouseup', onMouseUp);
      gameStage.removeEventListener('touchend', onMouseUp);
    }
  };

  if (gameStage) {
    gameStage.addEventListener('mousemove', onMouseMove, { passive: true });
    gameStage.addEventListener('touchmove', onMouseMove, { passive: true });
    gameStage.addEventListener('mouseup', onMouseUp, { passive: true });
    gameStage.addEventListener('touchend', onMouseUp, { passive: true });
  }
};

const handleWheel = (event: WheelEvent) => {
  const scaleDelta = event.deltaY < 0 ? 2: -2;
  props.updateGameProps({
    ...props.gameProps,
    scaleFactor: Math.max(5, Math.min(200, props.gameProps.scaleFactor + scaleDelta)),
  });
};

const isPortrait = ref(false);

const handleResize = () => {
  stageConfig.value.width = window.innerWidth;
  stageConfig.value.height = window.innerHeight;
  isPortrait.value = window.innerWidth < window.innerHeight;
};

const lastDistance = ref(0);
const handlePinch = (event: TouchEvent) => {
  if (event.touches.length === 2) {
    const distance = Math.hypot(
      event.touches[0].clientX - event.touches[1].clientX,
      event.touches[0].clientY - event.touches[1].clientY
    );
    const scaleDelta = distance > lastDistance.value ? 4 : -4;
    lastDistance.value = distance;
    props.updateGameProps({
      ...props.gameProps,
      scaleFactor: Math.max(5, Math.min(200, props.gameProps.scaleFactor + scaleDelta)),
    });
  }
};


onMounted(() => {
  const imageObj = new window.Image();
  imageObj.src = '/images/game-bg.webp';

  imageObj.onload = () => {
    stageConfig.value.image = imageObj;
  };
});

onMounted(() => {
  gameStage = document.querySelector('.game-stage');
  if (gameStage) {
    gameStage.addEventListener('wheel', handleWheel, { passive: true });
    gameStage.addEventListener('mousedown', handleRightClickDrag, { passive: true });
    gameStage.addEventListener('touchstart', handleRightClickDrag, { passive: true });
    gameStage.addEventListener('touchmove', handlePinch, { passive: true });
    window.addEventListener('resize', handleResize, { passive: true });
  }
});

onUnmounted(() => {
  if (gameStage) {
    gameStage.removeEventListener('wheel', handleWheel);
    gameStage.removeEventListener('mousedown', handleRightClickDrag);
    gameStage.removeEventListener('touchstart', handleRightClickDrag);
    gameStage.removeEventListener('touchmove', handlePinch);
    window.removeEventListener('resize', handleResize);
  }
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

const checkFactoryAffordability = (player: Player, input_items: { [key: string]: number } | [{ [key: string]: number }], feature: { type: string, properties: any }) => {
  if (player === null) {
    return false;
  }
  // if (feature.properties['MustLend']) {
  //   if (player.specie === "Eni") {
  //     return false;
  //   }
  // }
  let discount = 0;
  if (feature.type === "Research" && Array.isArray(input_items)) {
    if (isOnFavorBuff(props.gameState, player.user_id)) {
      discount = 1;
    }
  }
  if (feature.properties['EnietInterest']) {
    if (Array.isArray(input_items)) {
      return false;
    }
    if (input_items["ArbitrarySmall"] > 0) {
      let maxSingleSmall = 0;
      for (let item of arbitrarySmallSource) {
        maxSingleSmall = Math.max(maxSingleSmall, (player.storage[item] || 0));
      }
      maxSingleSmall += (player.storage["WildSmall"] || 0);
      if (input_items["ArbitrarySmall"] > maxSingleSmall) {
        return false;
      }
      return true;
    } else if (input_items["ArbitraryBig"] > 0) {
      let maxSingleBig = 0;
      for (let item of arbitraryBigSource) {
        maxSingleBig = Math.max(maxSingleBig, (player.storage[item] || 0));
      }
      maxSingleBig += (player.storage["WildBig"] || 0);
      if (input_items["ArbitraryBig"] > maxSingleBig) {
        return false;
      }
      return true;
    }
  }
  if (!Array.isArray(input_items)) {
    for (let item in input_items) {
      if ((player.storage[item] || 0) < input_items[item]) {
        return false;
      }
    }
  } else if (Array.isArray(input_items)) {
    for (let cost of input_items) {
      let affordable = true;
      for (let item in cost) {
        if ((player.storage[item] || 0) < cost[item] - discount) {
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

const emitProduce = (factoryName: string, converter_index: number, extra_properties: any) => {
  socket.emit("produce", {
    room_name: props.gameState.room_name,
    username: props.username,
    factory_name: factoryName,
    converter_index: converter_index,
    extra_properties: extra_properties ? extra_properties : {}
  });
}

const produce = (factory: Factory, converter_index: number, extra_properties?: any) => {
  if (factory.feature.type === "Research") {
    handleResearchPanel(factory);
    return;
  }
  console.log(factory.feature);
  if (factory.feature.properties["EnietInterest"]) {
    handleEnietInterestPanel(factory);
    return
  }
  emitProduce(factory.name, converter_index, extra_properties);
}

const upgradeColony = (factory: Factory) => {
  socket.emit("upgrade-colony", {
    room_name: props.gameState.room_name,
    username: props.username,
    factory_name: factory.name
  });
}
const upgradeNormal = (factoryName: string, id: number, newFactoryName: string) => {
  pleaseCheckAgain(() => {
    socket.emit("upgrade-normal", {
      room_name: props.gameState.room_name,
      username: props.username,
      factory_name: factoryName,
      cost_type: id
    });
  }, `你是否确定以第 ${id} 种升级费用升级工厂 ${factoryName} 为 ${newFactoryName} ？注意这将是不可逆的操作。`,
    {
      component: FactoryDisplayerAsync,
      props: {
        roomName: props.gameState.room_name,
        me: getMe(),
        factory: newFactoryName,
        getFactoryConfig: getFactoryConfig
      }
    }
  );
}

const foldMetaFactories = ref(false);
const toggleFoldMetaFactories = () => {
  foldMetaFactories.value = !foldMetaFactories.value;
}

const getFactoryConfig = (me: Player, factory: Factory, x: number, y: number): FactoryConfig => {
  return {
    x: x,
    y: y,
    width: factoryWidth * props.gameProps.scaleFactor / 100,
    height: factoryHeight * props.gameProps.scaleFactor / 100,
    scaleFactor: props.gameProps.scaleFactor,
    factory: factory,
    owner: factory.owner,
    producible: (input_items: { [key: string]: number } | [{ [key: string]: number }]) => checkFactoryAffordability(me, input_items, factory.feature),
    gameState: props.gameState,
    produce: (converter_index: number) => produce(factory, converter_index),
    upgradeColony: () => {
      if (factory.feature.type === "Colony") {
        upgradeColony(factory);
      }
    },
    upgradeNormal: (id: number) => {
      if (factory.feature.type === "Normal") {
        upgradeNormal(factory.name, id, factory.feature.properties['upgrades'][id]['factory']);
      }
    },
    me: me,
    selectedPlayer: selectedPlayer.value
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
    if (factory.endsWith("_打出") && foldMetaFactories.value) {
      continue;
    }
    configs[factory] = getFactoryConfig(me, me.factories[factory], 
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


const showGameBoard = ref(true); 
const toggleGameBoard = () => {
  showGameBoard.value = !showGameBoard.value;
}

const displayTradePanel = ref(false);
const handleTradePanel = () => {
  if (!displayTradePanel.value) {
    displayTradePanel.value = true;
  } else {
    console.log("trade panel already displayed");
  }
};
const submitGift = (gift: Gift, toWhom: string) => {
  socket.emit("gift", {
    room_name: props.gameState.room_name,
    username: props.username,
    gift: gift,
    to: toWhom
  });
};
const submitProposal = (sendGift: Gift, receiveGift: Gift, to: string[], message: string) => {
  socket.emit("trade-proposal", {
    room_name: props.gameState.room_name,
    username: props.username,
    send: sendGift,
    receive: receiveGift,
    to: to,
    message: message
  });
};
const declineProposal = (proposal_id: number) => {
  socket.emit("decline-trade-proposal", {
    room_name: props.gameState.room_name,
    username: props.username,
    id: proposal_id
  });
}
const acceptProposal = (proposal_id: number) => {
  socket.emit("accept-trade-proposal", {
    room_name: props.gameState.room_name,
    username: props.username,
    id: proposal_id
  });
} 
const tradeItems = ref<{ [key: string]: number }>({});
const updateTradeItems = (items: { [key: string]: number }) => {
  tradeItems.value = items;
};

const closeTradePanel = () => {
  displayTradePanel.value = false;
  tradeItems.value = {};
};

const displayExchangePanel = ref(false);
const arbitraryItems = ref<{ [key: string]: number }>({});
const wildItems = ref<{ [key: string]: number }>({});
const handleExchangePanel = () => {
  displayExchangePanel.value = true;
}
const closeExchangePanel = () => {
  displayExchangePanel.value = false;
  arbitraryItems.value = {};
  wildItems.value = {};
}
const updateArbitraryItems = (items: { [key: string]: number }) => {
  arbitraryItems.value = items;
}
const updateWildItems = (items: { [key: string]: number }) => {
  wildItems.value = items;
}
const submitExchange = (colonies: string[], arbitraryItems: { [key: string]: number }, wildItems: { [key: string]: number }) => {
  for (const colony of colonies) {
    socket.emit("exchange-colony", {
      room_name: props.gameState.room_name,
      username: props.username,
      colony_name: colony
    });
  }
  socket.emit("exchange-arbitrary", {
    room_name: props.gameState.room_name,
    username: props.username,
    items: arbitraryItems
  });
  socket.emit("exchange-wild", {
    room_name: props.gameState.room_name,
    username: props.username,
    items: wildItems
  });
}


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

const isBidStage = (stage: string) => {
  return true;
  // return stage === "bid" || stage === "pick";
}

watch(() => props.gameState.stage, (newStage) => {
  displayBidPanel.value = isBidStage(newStage);
});
const submitBid = (colonyBid: number, researchBid: number) => {
  socket.emit("submit-bid", {
    room_name: props.gameState.room_name,
    username: props.username,
    colony_bid: colonyBid,
    research_bid: researchBid
  });
}

const submitKajsjavikalimmChooseSplit = (chooseSplit: boolean) => {
  socket.emit("submit-kajsjavikalimm-choose-split", {
    room_name: props.gameState.room_name,
    username: props.username,
    choose_split: chooseSplit
  });
}

const closeBidPanel = () => {
  displayBidPanel.value = false;
}

const submitPick = (type: string, id: number) => {
  socket.emit("submit-pick", {
    room_name: props.gameState.room_name,
    username: props.username,
    type: type,
    pick_id: id
  });
}

const displayEndPanel = ref(false);
const openEndPanel = () => {
  displayEndPanel.value = true;
}

const isEndStage = (stage: string) => {
  return stage === "gameend";
}

watch(() => props.gameState.stage, (newStage) => {
  displayEndPanel.value = isEndStage(newStage);
});

const closeEndPanel = () => {
  displayEndPanel.value = false;
}

const checkPanel = ref(false);
const checkCallback = ref<(() => void)>(() => {});
const checkMessage = ref<{ component: Component, props: any } | null>(null);
const checkTitle = ref<string>("");
const pleaseCheckAgain = (callback: () => void, title: string, message: { component: Component, props: any } | null) => {
  checkPanel.value = true;
  checkCallback.value = callback;
  checkMessage.value = message;
  checkTitle.value = title;
}
const closeCheckPanel = () => {
  checkPanel.value = false;
  checkCallback.value = () => {};
  checkMessage.value = null;
  checkTitle.value = "";
}

const displayDiscardColonyPanel = ref(false);
const isDiscardColonyStage = () => {
  return props.gameState.stage === "discard_colony" && props.gameState.current_discard_colony_player === props.username;
}
watch(() => props.gameState.stage, (newStage) => {
  displayDiscardColonyPanel.value = isDiscardColonyStage();
});
const submitDiscardColony = (colonies: string[]) => {
  socket.emit("discard-colonies", {
    room_name: props.gameState.room_name,
    username: props.username,
    colonies: colonies
  });
}
const openDiscardColonyPanel = () => {
  displayDiscardColonyPanel.value = true;
}
const closeDiscardColonyPanel = () => {
  displayDiscardColonyPanel.value = false;
}
const getDiscardNum = () => {
  const me = getMe()!;
  const maxColony = me.max_colony;
  const colonies = Object.keys(me.factories).filter(factory => me.factories[factory].feature.type === "Colony");
  console.log(colonies, maxColony);
  return colonies.length > maxColony ? colonies.length - maxColony : 0;
}

const displayEnietInterestPanel = ref(false);
const enietInterestFactory = ref<Factory | null>(null);
const handleEnietInterestPanel = (factory: Factory) => {
  displayEnietInterestPanel.value = true;
  enietInterestFactory.value = factory;
}
const closeEnietInterestPanel = () => {
  displayEnietInterestPanel.value = false;
  enietInterestFactory.value = null;
}


const submitEnietInterestSelect = (factoryName: string, properties: {"output_type": string, "input_combination": {[key: string]: number}}) => {
  socket.emit("produce", {
    room_name: props.gameState.room_name,
    username: props.username,
    factory_name: factoryName,
    extra_properties: properties
  });
}


const displayMask = () => {
  return displayTradePanel.value
    || displayResearchPanel.value
    || displayBidPanel.value
    || displayEndPanel.value
    || checkPanel.value
    || displayExchangePanel.value
    || displayDiscardColonyPanel.value
    || displayEnietInterestPanel.value;
};

const getToggleGameBoardButtonConfig = () => {
  if (isPortrait.value) {
    return {
      top: 10,
      left: 10,
    }
  }
  return {
    top: 10,
    left: 10 + (showGameBoard.value ? 300 : 0),
  }
}
</script>


<template>
  <div class="game-stage" :class="{'game-stage-show-gameboard': showGameBoard, 'game-stage-hide-gameboard': !showGameBoard}">
    <v-stage :config="stageConfig" class="game-stage-canvas">
      <v-layer>
        <v-image :config="stageConfig"/>
        <template v-for="factory in getFactoryConfigs()" :key="factory.id">
          <FactoryDisplayer :="factory" />
        </template>
      </v-layer>
    </v-stage>
  </div>
  <GameBoard :game-state="props.gameState" 
    :username="props.username" 
    :handle-trade-panel="handleTradePanel" 
    :selected-player="selectedPlayer"
    :handle-select-player="handleSelectPlayer"
    :handle-exchange-panel="handleExchangePanel"
    :exit-game="() => props.switchPage('lobby')"
    class="game-panel"
    v-if="showGameBoard"
  />
  <TradePanel :submit-gift="submitGift" 
    :submit-proposal="submitProposal"
    :update-trade-items="updateTradeItems" 
    :trade-items="tradeItems" 
    :close-trade-panel="closeTradePanel" 
    :decline-proposal="declineProposal"
    :accept-proposal="acceptProposal"
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
    :submit-pick="submitPick"
    :game-state="props.gameState"
    :get-factory-config="getFactoryConfig"
    :get-me="getMe"
    :get-player="getPlayer"
    :username="props.username"
    :room-name="props.gameState.room_name"
    :submit-kajsjavikalimm-choose-split="submitKajsjavikalimmChooseSplit"
    v-if="displayBidPanel"
  />
  <EndPanel :close-end-panel="closeEndPanel" 
    :get-me="getMe"
    :get-player="getPlayer"
    :username="props.username"
    :players="props.gameState.players"
    v-if="displayEndPanel"
  />
  <CheckPanel :check-title="checkTitle" :check-message="checkMessage" :check-callback="checkCallback" :close-callback="closeCheckPanel" v-if="checkPanel" />
  <ExchangePanel 
    :submit-exchange="submitExchange" 
    :close-exchange-panel="closeExchangePanel" 
    :username="props.username" 
    :game-state="props.gameState" 
    :get-me="getMe" 
    :arbitrary-items="arbitraryItems"
    :update-arbitrary-items="updateArbitraryItems"
    :wild-items="wildItems"
    :update-wild-items="updateWildItems"
    v-if="displayExchangePanel" 
  />
  <DiscardColonyPanel :submit-discard-colony="submitDiscardColony" 
    :close-discard-colony-panel="closeDiscardColonyPanel" 
    :username="props.username"
    :game-state="props.gameState"
    :get-me="() => getMe()!"
    :discard-num="getDiscardNum()"
    v-if="displayDiscardColonyPanel"
  />
  <EnietInterestPanel
    :submit-eniet-interest-select="submitEnietInterestSelect"
    :close-eniet-interest-panel="closeEnietInterestPanel"
    :factory="enietInterestFactory!"
    :me="getMe()!"
    :game-state="props.gameState"
    v-if="displayEnietInterestPanel"
  />
  <n-float-button 
    @click="openBidPanel" 
    v-if="isBidStage(props.gameState.stage)" 
    :top="10"
    :right="10"
  >
    <template #description>Bid</template>
  </n-float-button>
  <n-float-button 
    @click="openEndPanel" 
    v-if="isEndStage(props.gameState.stage)" 
    :top="10"
    :right="10"
  >
    <template #description>End</template>
  </n-float-button>
  <n-float-button 
    @click="openDiscardColonyPanel" 
    v-if="isDiscardColonyStage()"
    :top="10"
    :right="10"
  >
    <template #description>Discard Colony</template>
  </n-float-button>

  <n-float-button 
    @click="toggleGameBoard"
    :top="getToggleGameBoardButtonConfig().top"
    :left="getToggleGameBoardButtonConfig().left"
  >
    <n-icon>
      <IconMenu />
    </n-icon>
  </n-float-button>
  <n-float-button @click="toggleFoldMetaFactories" :left="10" :bottom="60" :type="foldMetaFactories ? 'default' : 'primary'">
    <template #description>{{ foldMetaFactories ? "展开打出" : "折叠打出" }}</template>
  </n-float-button>
</template>

<style scoped>
.game-stage {
  position: absolute;
  top: 0;
  height: 100vh;
  overflow: hidden;
}
/* .game-stage-show-gameboard {
  left: 300px;
  width: calc(100vw - 300px);
} */
.game-stage-show-gameboard {
  left: 0;
  width: 100vw;
}
.game-stage-hide-gameboard {
  left: 0;
  width: 100vw;
}
.game-stage-canvas {
  overflow: hidden;
}
</style>