<script setup lang="ts">
import IconArrowForwardOutlined from '@/components/icons/IconArrowForwardOutlined.vue';
import type { MapProps } from '@/components/CityMap.vue';
import IconRenew from '@/components/icons/IconRenew.vue';
import IconSaveImg from '@/components/icons/IconSaveImg.vue';
import { NButton, NButtonGroup, NFloatButton, NIcon } from 'naive-ui';
import { socket } from '@/utils/connect';

// props
defineProps<{
  renewHandler: () => void;
  saveImgHandler: () => void;
}>();

const cityTick = () => {
  console.log('city-tick');
  socket.emit('city-tick');
};
</script>

<template>
  <div class="control-panel" style="height: 200px; transform: translate(0)">
    <n-float-button :right="0" :top="0" @click="cityTick" size="large" type="primary">
      <n-icon color="white" size="30">
        <IconArrowForwardOutlined/>
      </n-icon>
    </n-float-button>
    <n-float-button :right="60" :top="0" @click="renewHandler" size="large" type="primary">
      <n-icon color="white" size="30">
        <IconRenew/>
      </n-icon>
    </n-float-button>
    <n-float-button :right="120" :top="0" @click="saveImgHandler" size="large" type="primary"> 
      <n-icon color="white" size="30">
        <IconSaveImg/>
      </n-icon>
    </n-float-button>
  </div>
  <div class="control-panel">
    
  </div>
</template>

<style scoped>
.control-panel {
  position: absolute;
  top: 0;
  right: 0;
  margin: 1rem;
}


</style>