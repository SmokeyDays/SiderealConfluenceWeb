<script setup lang="ts">
import { defineProps, onMounted, ref } from 'vue';
import ItemIcon from '@/components/ItemIcon.vue';
import FoodSvg from '@/components/icons/items/Food.svg';
import CultureSvg from '@/components/icons/items/Culture.svg';
import IndustrySvg from '@/components/icons/items/Industry.svg';
import InformationSvg from '@/components/icons/items/Information.svg';
import BiotechSvg from '@/components/icons/items/Biotech.svg';
import EnergySvg from '@/components/icons/items/Energy.svg';
import HypertechSvg from '@/components/icons/items/Hypertech.svg';
import AnySmallSvg from '@/components/icons/items/AnySmall.svg';
import AnyBigSvg from '@/components/icons/items/AnyBig.svg';
import ShipSvg from '@/components/icons/items/Ship.svg';
import ScoreSvg from '@/components/icons/items/Score.svg';
import PlaceholderSvg from '@/components/icons/items/Placeholder.svg';

const getIconSvg = (item: string) =>  {
  switch (item) {
    case 'Food':
      return FoodSvg;
    case 'Culture':
      return CultureSvg;
    case 'Industry':
      return IndustrySvg;
    case 'Information':
      return InformationSvg;
    case 'Biotech':
      return BiotechSvg;
    case 'Energy':
      return EnergySvg;
    case 'Hypertech':
      return HypertechSvg;
    case 'AnySmall':
      return AnySmallSvg;
    case 'AnyBig':
      return AnyBigSvg;
    case 'Ship':
      return ShipSvg;
    case 'Score':
      return ScoreSvg;
    default:
      return PlaceholderSvg;
  }
};

const props = defineProps<{
  item: string;
  count: number;
  x: number;
  y: number;
}>();

const imageConfig = ref({
  x: 10,
  y: 5,
  image: new Image(),
  width: 30,
  height: 30
});

function getSvg(name: string) {
  return getIconSvg(name);
} 

onMounted(() => {
  const imageObj = new window.Image();
  imageObj.src = getSvg(props.item);
  imageObj.onload = () => {
    // set image only when it is loaded
    console.log(imageObj);
    imageConfig.value.image = imageObj;
    console.log(imageConfig.value);
  };
});

</script>

<template>
  <v-group :config="{ x: props.x, y: props.y }">
    <v-text :config="{
      text: `${props.count}`,
      fontSize: 20,
      fontFamily: 'Calibri',
      fill: 'black',
      x: 0,
      y: 0
    }" />
    <v-image :config="imageConfig" />
  </v-group>
</template>