<template>
  <v-group>
    <!-- Factory background -->
    <v-rect :config="{
      x: props.x,
      y: props.y,
      width: props.width,
      height: props.height,
      fill: '#555',
      cornerRadius: 5
    }" />

    <v-text :config="getTitleConfig(props.factory.name)" />

    <!-- Input items -->
    <v-group :config="{ x: props.x + 0.033 * props.width, y: props.y + 0.5 * props.height - 0.5 * getEstimatedItemEntriesHeight(generateItems(props.factory.input_items).length) }">
      <template v-for="entry in generateItems(props.factory.input_items)" :key="'input-' + entry.item">
        <item-entry :item="entry.item" :count="entry.count" :x="0" :y="entry.y" :scale-factor="entry.scaleFactor" :icon-width="entry.iconWidth" :icon-height="entry.iconHeight"/>
      </template>
    </v-group>

    <!-- Output items -->
    <v-group :config="{ x: props.x + props.width - 0.33 * props.width, y: props.y + 0.5 * props.height - 0.5 * getEstimatedItemEntriesHeight(generateItems(props.factory.output_items).length) }">
      <template v-for="entry in generateItems(props.factory.output_items)" :key="'output-' + entry.item">
        <item-entry :item="entry.item" :count="entry.count" :x="0" :y="entry.y" :scale-factor="entry.scaleFactor" :icon-width="entry.iconWidth" :icon-height="entry.iconHeight"/>
      </template>
    </v-group>

    <!-- Arrow connecting input to output -->
    <v-arrow :config="{
      points: [props.x + 0.25 * props.width, props.y + props.height / 2, props.x + props.width - 0.35 * props.width, props.y + props.height / 2],
      pointerLength: 0.05 * props.width,
      pointerWidth: 0.1 * props.height,
      fill: 'white',
      stroke: 'white',
      strokeWidth: 0.05 * props.height
    }" />
  </v-group>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import { type Factory } from '@/interfaces/GameState';
import ItemEntry from '@/components/ItemEntry.vue';

const props = defineProps<{
  scaleFactor: number;
  factory: Factory;
  x: number;
  y: number;
  width: number;
  height: number;
}>();

const generateItems = (items: {[key: string]: number}) => {
  const entries: { item: string, count: number, x: number, y: number, scaleFactor: number, iconWidth: number, iconHeight: number}[] = [];
  let num = 0;
  for (let item in items) {
    if (items[item] === 0) continue;
    entries.push({
      item: item,
      count: items[item],
      x: 0,
      y: num * 0.12 * props.height,
      scaleFactor: props.scaleFactor,
      iconWidth: 100 * props.scaleFactor / 100,
      iconHeight: 100 * props.scaleFactor / 100
    });
    num++;
  }
  return entries;
}

const getTitleConfig = (text: string) => {
  const fontSize = 0.05 * props.height;    
  const estimateWidth = text.length * fontSize;
  return {
    text: text,
    fontSize: fontSize,
    fontFamily: 'Calibri',
    fill: 'black',
    x: props.x + props.width / 2 - estimateWidth / 2,
    y: props.y + fontSize
  }
}

const getEstimatedItemEntriesHeight = (len: number) => {
  return len * 0.12 * props.height;
}
</script>
