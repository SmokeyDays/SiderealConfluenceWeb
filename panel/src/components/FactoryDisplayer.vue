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
    <template v-if="props.factory.feature.type === 'Normal'">
      <v-group :config="{ x: props.x + 0.033 * props.width, y: props.y + 0.5 * props.height - 0.5 * getEstimatedItemEntriesHeight(generateItems(props.factory.input_items).length) }">
        <template v-for="entry in generateItems(props.factory.input_items)" :key="'input-' + entry.item">
          <item-entry :item="entry.item" :count="entry.count" :x="entry.x" :y="entry.y" :scale-factor="entry.scaleFactor" :icon-width="entry.iconWidth" :icon-height="entry.iconHeight"/>
        </template>
      </v-group>
    </template>
    <template v-if="props.factory.feature.type === 'Research'">
      <template v-for="index in Object.keys(props.factory.feature.properties['research_cost']).map(Number)" :key="'research-' + index">
        <v-group :config="{ 
          x: props.x + 0.033 * props.width, 
          y: props.y + 0.5 * props.height 
          - 0.5 * getEstimatedItemEntriesHeight(generateResearchItems(props.factory.feature.properties['research_cost'][index], index).length)
        }">
          <v-text :config="{
            text: '或',
            fontSize: 0.05 * props.height,
            fill: 'black',
            x: 1.0 / 6 * props.width * researchItemScaleFactor * index,
            y: 0.05 * props.height
          }" v-if="index != 0"/>
          <template v-for="entry in generateResearchItems(props.factory.feature.properties['research_cost'][index], index)" 
            :key="'research-' + entry.item">
            <item-entry :item="entry.item" :count="entry.count" :x="entry.x" :y="entry.y" :scale-factor="entry.scaleFactor" :icon-width="entry.iconWidth" :icon-height="entry.iconHeight"/>
          </template>
        </v-group>
      </template>
    </template>
    
    <!-- Output items -->
    <v-group :config="{ x: props.x + props.width - 0.33 * props.width, y: props.y + 0.5 * props.height - 0.5 * getEstimatedItemEntriesHeight(generateItems(props.factory.output_items).length) }">
      <template v-for="entry in generateItems(props.factory.output_items)" :key="'output-' + entry.item">
        <item-entry :item="entry.item" :count="entry.count" :x="entry.x" :y="entry.y" :scale-factor="entry.scaleFactor" :icon-width="entry.iconWidth" :icon-height="entry.iconHeight"/>
      </template>
    </v-group>

    <!-- Arrow connecting input to output -->
    <template>
      <v-arrow :config="{
        points: [props.x + 0.35 * props.width, props.y + props.height / 2, props.x + props.width - 0.37 * props.width, props.y + props.height / 2],
        pointerLength: 0.04 * props.width,
        pointerWidth: 0.08 * props.height,
        fill: props.factory.run_in_trading ? 'purple' : 'white',
        stroke: props.factory.run_in_trading ? 'purple' : 'white',
        strokeWidth: 0.05 * props.height
      }" />
      <template v-if="!props.producible && !props.factory.used">
        <v-line :config="{
          points: [props.x + 0.45 * props.width, props.y + 0.45 * props.height, props.x + 0.55 * props.width, props.y + 0.55 * props.height],
          stroke: 'red',
          strokeWidth: 0.02 * props.height,
          opacity: stageOpacity()
        }" />
        <v-line :config="{
          points: [props.x + 0.45 * props.width, props.y + 0.55 * props.height, props.x + 0.55 * props.width, props.y + 0.45 * props.height],
          stroke: 'red',
          strokeWidth: 0.02 * props.height,
          opacity: stageOpacity()
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
          opacity: stageOpacity()
        }" />
        <template v-if="props.factory.used">
          <v-line :config="{
            points: [props.x + 0.45 * props.width, props.y + 0.5 * props.height, props.x + 0.5 * props.width, props.y + 0.57 * props.height, props.x + 0.57 * props.width, props.y + 0.4 * props.height],
            stroke: 'lightgreen',
            strokeWidth: 0.02 * props.height,
            opacity: stageOpacity()
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
  produce: () => void;
  research: () => void;
}

const stageOpacity = () => {
  const rightStage = props.factory.run_in_trading ? 'trading' : 'production';
  return props.gameState.stage === rightStage ? 1 : 0.5;
}

const produceClick = () => {
  if (props.factory.used || !props.producible) {
    return;
  }
  if (props.factory.feature.type === 'Normal') {
    props.produce();
  } else if (props.factory.feature.type === 'Research') {
    props.research();
  }
}

const props = defineProps<FactoryConfig>();

const generateItems = (items: {[key: string]: number}) => {
  const entries: { item: string, count: number, x: number, y: number, scaleFactor: number, iconWidth: number, iconHeight: number, isFirst: boolean}[] = [];
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
      iconHeight: 1.0 / 4 * props.height,
      isFirst: num === 0
    });
    num++;
  }
  return entries;
}
const researchItemScaleFactor = 0.5;
const generateResearchItems = (items: {[key: string]: number}, column: number) => {
  const entries: { item: string, count: number, x: number, y: number, scaleFactor: number, iconWidth: number, iconHeight: number, isFirst: boolean}[] = [];
  let num = 0;
  console.log(column);
  for (let item in items) {
    if (items[item] === 0) continue;
    entries.push({
      item: item,
      count: items[item],
      x: column * 0.12 * props.width,
      y: num * 0.12 * props.height,
      scaleFactor: props.scaleFactor * researchItemScaleFactor,
      iconWidth: 1.0 / 6 * props.width * researchItemScaleFactor,
      iconHeight: 1.0 / 4 * props.height * researchItemScaleFactor,
      isFirst: num === 0
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
