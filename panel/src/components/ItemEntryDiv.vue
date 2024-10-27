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
import { getIconSvg } from '@/utils/icon';

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