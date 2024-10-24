<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { defineProps } from 'vue';
import { type Factory, type GameState, type Player } from '../interfaces/GameState';
import FactoryDisplayer from '@/components/FactoryDisplayer.vue';

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
    event.preventDefault();
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

interface FactoryConfig {
  x: number;
  y: number;
  width: number;
  height: number;
  factory: Factory;
  scaleFactor: number;
  owner: string;
}

const factoryWidth = 600;
const factoryHeight = 400;

const getFactoryConfigs = (): {[key: string]: FactoryConfig} => {
  let me: Player | null = null;
  for (let player in props.gameState.players) {
    if (props.gameState.players[player].user_id === props.username) {
      me = props.gameState.players[player];
    }
  }
  if (me === null) {
    console.log("player", props.username, "not found");
    return {};
  }
  const configs: {[key: string]: FactoryConfig} = {};
  let xOffset = 0;
  let yOffset = 0;
  for (let factory in me.factories) {
    configs[factory] = {
      x: xOffset + props.gameProps.offsetX,
      y: yOffset + props.gameProps.offsetY,
      width: factoryWidth * props.gameProps.scaleFactor / 100,
      height: factoryHeight * props.gameProps.scaleFactor / 100,
      scaleFactor: props.gameProps.scaleFactor,
      factory: me.factories[factory],
      owner: me.factories[factory].owner
    };
    xOffset += (factoryWidth + 50) * props.gameProps.scaleFactor / 100;
    if (xOffset + (factoryWidth + 50) * props.gameProps.scaleFactor / 100 > stageConfig.value.width) {
      xOffset = 0;
      yOffset += (factoryHeight + 50) * props.gameProps.scaleFactor / 100;
    }
  }
  return configs;
}
</script>

<template>
  <div class="game-stage">
    <v-stage :config="stageConfig">
      <v-layer>
        <v-rect :config="{ x: 0, y: 0, width: stageConfig.width, height: stageConfig.height, fill: 'white' }" />
        <template v-for="factory in getFactoryConfigs()" :key="factory.id">
          <FactoryDisplayer :factory="factory.factory"
            :scale-factor="factory.scaleFactor" 
            :x="factory.x" 
            :y="factory.y" 
            :width="factory.width" 
            :height="factory.height" 
            :owner="factory.owner" />
        </template>
      </v-layer>
    </v-stage>
  </div>
</template>

<style scoped>
.game-stage {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  z-index: -100;
}
</style>