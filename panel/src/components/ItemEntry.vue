<script setup lang="ts">
import { defineProps, onMounted, ref, watch } from 'vue';
import { getIconSvg } from '@/utils/icon';

const props = defineProps<{
  item: string;
  count: number;
  x: number;
  y: number;
  iconWidth: number;
  iconHeight: number
  scaleFactor: number;
  desc?: string;
  preview?: boolean;
}>();

const imageConfig = ref({
  x: 0 * props.iconWidth,
  y: 0 * props.iconHeight,
  image: new Image(),
  width: props.iconWidth,
  height: props.iconHeight,
});

function getSvg(name: string) {
  return getIconSvg(name);
} 

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

<template>
  <v-group :config="{ x: props.x, y: props.y, opacity: props.preview ? 0.5 : 1 }">
    <v-image :config="imageConfig" />
    <v-text v-if="count != 1" :config="{
      text: `${props.count}`,
      fontSize: 0.8 * props.iconHeight,
      fontFamily: 'Calibri',
      fill: 'black',
      x: 0.2 * props.iconWidth,
      y: 0.2 * props.iconHeight,
      shadowColor: 'white',
      shadowBlur: 2,
      shadowOffsetX: 1,
      shadowOffsetY: 1
    }" />
    <v-text v-if="props.desc" :config="{
      text: props.desc,
      fontSize: 0.7 * props.iconHeight,
      fontFamily: 'Calibri',
      fill: 'black',
      x: 0.2 * props.iconWidth,
      y: 0.2 * props.iconHeight,
      shadowColor: 'white',
      shadowBlur: 2,
      shadowOffsetX: 1,
      shadowOffsetY: 1
    }" />
  </v-group>
</template>