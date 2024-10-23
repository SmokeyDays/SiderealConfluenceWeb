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
    <v-group :config="{ x: props.x + 10, y: props.y + 10 }">
      <template v-for="entry in generateItems(props.factory.input_items)" :key="'input-' + entry.item">
        <item-entry :item="entry.item" :count="entry.count" :x="0" :y="entry.y" />
      </template>
    </v-group>

    <!-- Output items -->
    <v-group :config="{ x: props.x + props.width - 40, y: props.y + 10 }">
      <template v-for="entry in generateItems(props.factory.output_items)" :key="'output-' + entry.item">
        <item-entry :item="entry.item" :count="entry.count" :x="0" :y="entry.y" />
      </template>
    </v-group>

    <!-- Arrow connecting input to output -->
    <v-arrow :config="{
      points: [props.x + 60, props.y + props.height / 2, props.x + props.width - 60, props.y + props.height / 2],
      pointerLength: 10,
      pointerWidth: 10,
      fill: 'white',
      stroke: 'white',
      strokeWidth: 4
    }" />
  </v-group>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import { type Factory } from '@/interfaces/GameState';
import ItemEntry from '@/components/ItemEntry.vue';

const props = defineProps<{
  factory: Factory;
  scaleFactor: number;
  x: number;
  y: number;
  width: number;
  height: number;
}>();

const generateItems = (items: {[key: string]: number}) => {
  const entries: { item: string, count: number, x: number, y: number }[] = [];
  let num = 0;
  for (let item in items) {
    entries.push({
      item: item,
      count: items[item],
      x: 0,
      y: num * 40
    });
    num++;
  }
  return entries;
}

const getTitleConfig = (text: string) => {
  const fontSize = 20;    
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
</script>
