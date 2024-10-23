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
  const scaleDelta = event.deltaY < 0 ? 1: -1;
  props.updateGameProps({
    ...props.gameProps,
    scaleFactor: Math.max(5, Math.min(100, props.gameProps.scaleFactor + scaleDelta)),
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
}

const factoryWidth = 600;
const factoryHeight = 400;

const getFactoryConfigs = (): {[key: string]: FactoryConfig} => {
  let me: Player | null = null;
  for (let player in props.gameState.players) {
    if (props.gameState.players[player].name === props.username) {
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
      width: factoryWidth,
      height: factoryHeight,
      factory: me.factories[factory],
      scaleFactor: props.gameProps.scaleFactor,
    };
    xOffset += factoryWidth;
    if (xOffset + factoryWidth > stageConfig.value.width) {
      xOffset = 100;
      yOffset += factoryHeight;
    }
  }
  return configs;
}

const baseGridSize = 50;
const gridColor = ref('rgba(200, 200, 200, 0.5)');

const getGridConfig = () => {
  const gridLines = [];
  const width = stageConfig.value.width;
  const height = stageConfig.value.height;
  const scaledGridSize = baseGridSize * props.gameProps.scaleFactor / 10;

  for (let x = props.gameProps.offsetX % scaledGridSize; x < width; x += scaledGridSize) {
    gridLines.push({
      points: [x, 0, x, height],
      stroke: gridColor.value,
      strokeWidth: 1,
    });
  }

  for (let y = props.gameProps.offsetY % scaledGridSize; y < height; y += scaledGridSize) {
    gridLines.push({
      points: [0, y, width, y],
      stroke: gridColor.value,
      strokeWidth: 1,
    });
  }

  return gridLines;
};

const getGridCoordinates = () => {
  const coordinates = [];
  const width = stageConfig.value.width;
  const height = stageConfig.value.height;
  const scaledGridSize = baseGridSize * props.gameProps.scaleFactor / 10;

  for (let x = props.gameProps.offsetX % scaledGridSize; x < width; x += scaledGridSize) {
    for (let y = props.gameProps.offsetY % scaledGridSize; y < height; y += scaledGridSize) {
      const gridX = Math.floor((x - props.gameProps.offsetX) / props.gameProps.scaleFactor);
      const gridY = Math.floor((y - props.gameProps.offsetY) / props.gameProps.scaleFactor);
      coordinates.push({
        x: x,
        y: y,
        text: `(${gridX},${gridY})`,
        fontSize: 10,
        fill: 'rgba(0, 0, 0, 0.5)',
      });
    }
  }

  return coordinates;
};

</script>

<template>
  <div class="game-stage">
    <v-stage :config="stageConfig">
      <v-layer>
        <v-line v-for="(line, index) in getGridConfig()" :key="'grid-' + index" v-bind="line" />
        <v-text v-for="(coord, index) in getGridCoordinates()" :key="'coord-' + index" v-bind="coord" />
        <v-rect :config="{ x: 0, y: 0, width: stageConfig.width, height: stageConfig.height, fill: 'white' }" />
        <template v-for="factory in getFactoryConfigs()" :key="factory.id">
          <FactoryDisplayer :factory="factory.factory" :scale-factor="factory.scaleFactor" :x="factory.x" :y="factory.y" :width="factory.width" :height="factory.height" />
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