<template>
  <v-group :config="{ x: props.x, y: props.y }">
    <v-rect :config="{
      x: 0,
      y: 0,
      width: props.width,
      height: props.height,
      fill: 'white',
      cornerRadius: 5
    }" />
    <template v-for="entry in generateItems(props.storage)" :key="'storage-' + entry.item">
      <item-entry :item="entry.item" :count="entry.count" :x="entry.x" :y="entry.y" :scale-factor="entry.scaleFactor" :icon-width="entry.iconWidth" :icon-height="entry.iconHeight"/>
    </template>
  </v-group>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import ItemEntry from '@/components/ItemEntry.vue';

const props = defineProps<{
  storage: {[key: string]: number};
  width: number;
  height: number;
  x: number;
  y: number;
  scaleFactor: number;
}>();

const generateItems = (items: {[key: string]: number}) => {
  const entries: { item: string, count: number, x: number, y: number, scaleFactor: number, iconWidth: number, iconHeight: number}[] = [];
  let num = 0;
  let x = 0;
  let y = 0;
  for (let item in items) {
    if (items[item] === 0) continue;
    y += num * 0.5 * props.height;
    if (y > props.height) {
      y = 0;
      x += 0.5 * props.width;
    }
    entries.push({
      item: item,
      count: items[item],
      x: x,
      y: y,
      scaleFactor: props.scaleFactor,
      iconWidth: 100 * props.scaleFactor / 100,
      iconHeight: 100 * props.scaleFactor / 100
    });
    num++;
  }
  return entries;
}

</script>


