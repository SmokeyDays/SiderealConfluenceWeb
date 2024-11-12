<template>
  <n-tooltip>
    <template #trigger>
      <div class="item-entry-div" style="display: flex; align-items: center; justify-content: center; overflow: hidden;">
        <p class="count-text" v-if="count != 1" :style="{
          fontSize: `${0.4 * iconHeight}px`,
          fontFamily: 'Calibri',
          color: 'black',
          position: 'absolute',
          top: `${0.2 * iconHeight}px`,
          left: `${0.4 * iconWidth}px`,
          textShadow: '2px 1px 1px #ccc',
        }">{{ count }}</p>
        <img :src="getSvg(item)" :style="{ width: `${iconWidth}px`, height: `${iconHeight}px` }" />
      </div>
    </template>
    <div>{{ getItemZhName(item) }} * {{ count }}</div>
  </n-tooltip>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { getIconSvg } from '@/utils/icon';
import { getItemZhName } from '@/interfaces/GameConfig';
import { NTooltip } from 'naive-ui';

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

<style scoped>
.item-entry-div {
  position: relative;
}
.count-text {
  position: absolute;
  top: 0.4;
  left: 0;
}
</style>

