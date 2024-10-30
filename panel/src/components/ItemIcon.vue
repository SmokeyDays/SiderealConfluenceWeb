<script setup lang="ts">  
import Food from '@/components/icons/items/Food.vue';
import Culture from '@/components/icons/items/Culture.vue';
import Industry from '@/components/icons/items/Industry.vue';
import Information from '@/components/icons/items/Information.vue';
import Biotech from '@/components/icons/items/Biotech.vue';
import Energy from '@/components/icons/items/Energy.vue';
import Hypertech from '@/components/icons/items/Hypertech.vue';
import WildSmall from '@/components/icons/items/WildSmall.vue';
import WildBig from '@/components/icons/items/WildBig.vue';
import Ship from '@/components/icons/items/Ship.vue';
import Placeholder from '@/components/icons/items/Placeholder.vue';

const props = defineProps<{
  item: string;
}>();

const getIcon = (item: string) =>  {
  switch (item) {
    case 'Food':
      return Food;
    case 'Culture':
      return Culture;
    case 'Industry':
      return Industry;
    case 'Information':
      return Information;
    case 'Biotech':
      return Biotech;
    case 'Energy':
      return Energy;
    case 'Hypertech':
      return Hypertech;
    case 'WildSmall':
      return WildSmall;
    case 'WildBig':
      return WildBig;
    case 'Ship':
      return Ship;
      
    default:
      return Placeholder;
  }
};
</script>

<template>
  <component :is="getIcon(item)" />
</template>

