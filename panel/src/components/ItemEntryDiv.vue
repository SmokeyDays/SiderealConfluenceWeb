<template>
  <div style="display: flex; align-items: center; justify-content: center; overflow: hidden;">
    <p v-if="count != 1" :style="{
      fontSize: `${0.4 * iconHeight}px`,
      fontFamily: 'Calibri',
      color: 'black',
    }">{{ count }} * </p>
    <img :src="getSvg(item)" :style="{ width: `${iconWidth}px`, height: `${iconHeight}px` }" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
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

const props = defineProps<{
  item: string,
  count: number,
  iconWidth: number,
  iconHeight: number
}>();

const imageConfig = ref({
  image: new Image(),
  width: props.iconWidth,
  height: props.iconHeight,
});

const getIconSvg = (item: string) => {
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

const getSvg = (name: string) => {
  return getIconSvg(name);
};

onMounted(() => {
  const imageObj = new window.Image();
  imageObj.src = getSvg(props.item);
  imageObj.onload = () => {
    // set image only when it is loaded
    imageConfig.value.image = imageObj;
  };
});

watch(() => [props.iconWidth, props.iconHeight], () => {
  imageConfig.value.width = props.iconWidth;
  imageConfig.value.height = props.iconHeight;
});
</script>