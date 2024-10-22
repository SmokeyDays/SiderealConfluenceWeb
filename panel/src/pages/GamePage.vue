<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { defineProps } from 'vue';
import { type GameState } from '../interfaces/GameState';

export interface GameProps {
  scaleFactor: number;
  offsetX: number;
  offsetY: number;
}

const props = defineProps<{
  gameProps: GameProps;
  updateGameProps: (props: GameProps) => void;
  gameState: GameState;
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
      console.log('mouse move', props.gameProps);
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
</script>

<template>
  <div class="game-stage">
    <v-stage :config="stageConfig">
      <v-layer>
        <v-rect :config="{ x: 0, y: 0, width: stageConfig.width, height: stageConfig.height, fill: 'white' }" />
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