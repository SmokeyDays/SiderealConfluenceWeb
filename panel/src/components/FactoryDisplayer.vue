<template>
  <v-group>
    <!-- Factory background -->
    <v-rect @click="produceClick" :config="{
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
    <template>
      <v-arrow :config="{
        points: [props.x + 0.25 * props.width, props.y + props.height / 2, props.x + props.width - 0.35 * props.width, props.y + props.height / 2],
        pointerLength: 0.05 * props.width,
        pointerWidth: 0.1 * props.height,
        fill: 'white',
        stroke: 'white',
        strokeWidth: 0.05 * props.height
      }" />
      <template v-if="!props.producible && !props.factory.used">
        <v-line :config="{
          points: [props.x + 0.45 * props.width, props.y + 0.45 * props.height, props.x + 0.55 * props.width, props.y + 0.55 * props.height],
          stroke: 'red',
          strokeWidth: 0.02 * props.height,
          opacity: props.gameState.stage !== 'production' ? 0.5 : 1
        }" />
        <v-line :config="{
          points: [props.x + 0.45 * props.width, props.y + 0.55 * props.height, props.x + 0.55 * props.width, props.y + 0.45 * props.height],
          stroke: 'red',
          strokeWidth: 0.02 * props.height,
          opacity: props.gameState.stage !== 'production' ? 0.5 : 1
        }" />
      </template>
      <template v-else>
        <v-circle :config="{
          x: props.x + props.width / 2,
          y: props.y + props.height / 2,
          radius: 0.05 * props.width,
          fill: '',
          stroke: props.factory.used ? 'gray' : 'yellow',
          strokeWidth: 0.02 * props.height,
          opacity: props.gameState.stage !== 'production' ? 0.5 : 1
        }" />
        <template v-if="props.factory.used">
          <v-line :config="{
            points: [props.x + 0.45 * props.width, props.y + 0.5 * props.height, props.x + 0.5 * props.width, props.y + 0.57 * props.height, props.x + 0.57 * props.width, props.y + 0.4 * props.height],
            stroke: 'lightgreen',
            strokeWidth: 0.02 * props.height,
            opacity: props.gameState.stage !== 'production' ? 0.5 : 1
          }" />
        </template>
      </template>
    </template>
  </v-group>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import { GameState, type Factory } from '@/interfaces/GameState';
import ItemEntry from '@/components/ItemEntry.vue';
import { getSpecieColor } from '@/interfaces/GameConfig';

export interface FactoryConfig {
  x: number;
  y: number;
  width: number;
  height: number;
  factory: Factory;
  scaleFactor: number;
  owner: string;
  producible: boolean;
  gameState: GameState;
  produce: (factoryName: string) => void;
}

const produceClick = () => {
  props.produce(props.factory.name);
}

const props = defineProps<FactoryConfig>();

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
      iconWidth: 1.0 / 6 * props.width,
      iconHeight: 1.0 / 4 * props.height
    });
    num++;
  }
  return entries;
}

const getTitleConfig = (text: string) => {
  const fontSize = 0.06 * props.height;    
  const estimateWidth = text.length * fontSize;
  return {
    text: text,
    fontSize: fontSize,
    fontFamily: 'Calibri',
    fill: getSpecieColor(props.owner),
    x: props.x + props.width / 2 - estimateWidth / 2,
    y: props.y + fontSize
  }
}

const getEstimatedItemEntriesHeight = (len: number) => {
  return len * 0.12 * props.height;
}
</script>
