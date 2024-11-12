<template>
  <div 
    class="player-specie" 
    :style="{ color: getSpecieColor(specie) }"
  >
    {{ getSpecieZhName(specie) }}
    {{ isMe ? ' (你)' : '' }}
  </div>
</template>
<script lang="ts" setup>
import { getSpecieZhName, getSpecieColor } from '@/interfaces/GameConfig';

const props = defineProps<{
  specie: string;
  isMe: boolean;
}>();
</script>

