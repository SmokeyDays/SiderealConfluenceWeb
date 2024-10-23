<script setup lang="ts">
import { defineProps, onMounted, ref } from 'vue';
import ItemIcon from '@/components/ItemIcon.vue';
import Food from './icons/items/Food.vue';

const props = defineProps<{
  item: string;
  count: number;
  x: number;
  y: number;
}>();

const imageConfig = ref({
  x: 0,
  y: 0,
  image: new Image(),
  width: 20,
  height: 20
});

function svgToURL(s: any) {
  const uri = window.btoa(unescape(encodeURIComponent(s)));
  return "data:image/svg+xml;base64," + uri;
}

function getSvg(name: string) {
  return import(`@/components/icons/items/${name}.vue`).then((module) => module.default);
} 

const svg = getSvg("AnyBig");
const url = svgToURL(svg);


onMounted(() => {
  const imageObj = new window.Image();
  imageObj.src = url;
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
  <div ref="icon" class="invisible-icon">
    <ItemIcon :item="props.item" />
  </div>
</template>
<style>
.invisible-icon {
  position: absolute;
  width: 0;
  height: 0;
  overflow: hidden;
}
</style>