<template>
  <div 
    class="player-specie" 
    :style="{ fontWeight: 'bold', color: getSpecieColor(specie) }"
    v-if="!props.isSpan"
  >
    {{ getSpecieZhName(specie) }}
    {{ isMe ? ' (你)' : '' }}
  </div>
  <span v-else :style="{ fontWeight: 'bold', color: getSpecieColor(specie) }">
    {{ getSpecieZhName(specie) }}
    {{ isMe ? ' (你)' : '' }}
  </span>
</template>
<script lang="ts" setup>
import { getSpecieZhName, getSpecieColor } from '@/interfaces/GameConfig';

const props = defineProps<{
  specie: string;
  isMe: boolean;
  isSpan?: boolean;
}>();
</script>

