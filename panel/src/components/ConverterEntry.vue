<template>
  <!-- Input items -->
  <template v-if="!Array.isArray(props.converter.input_items)">
      <v-group :config="{ x: props.x + 0.28 * props.width, y: props.y + 0.5 * props.height - 0.5 * getEstimatedItemEntriesHeight(generateItems(props.converter.input_items).length) }">
        <template v-for="entry in generateItems(props.converter.input_items)" :key="'input-' + entry.item">
          <item-entry :item="entry.item" :count="entry.count" :x="entry.x" :y="entry.y" :scale-factor="entry.scaleFactor" :icon-width="entry.iconWidth" :icon-height="entry.iconHeight"/>
        </template>
      </v-group>
    </template>
    <template v-if="Array.isArray(props.converter.input_items)">
      <template v-for="index in Object.keys(props.converter.input_items).map(Number)" :key="'research-' + index">
        <v-group :config="{ 
          x: props.x + 0.1 * props.width, 
          y: props.y + 0.5 * props.height 
          - 0.5 * getEstimatedItemEntriesHeight(generateResearchItems(props.converter.input_items[index], index).length)
        }">
          <v-text :config="{
            text: '或',
            fontSize: 0.05 * props.height,
            fill: 'white',
            x: 0.82 / 6 * props.width * researchItemScaleFactor * index,
            y: 0.05 * props.height
          }" v-if="index != 0"/>
          <template v-for="entry in generateResearchItems(props.converter.input_items[index], index)" 
            :key="'research-' + entry.item">
            <item-entry :item="entry.item" :count="entry.count" :x="entry.x" :y="entry.y" :scale-factor="entry.scaleFactor" :icon-width="entry.iconWidth" :icon-height="entry.iconHeight"/>
          </template>
        </v-group>
      </template>
    </template>
    
    <!-- Output items -->
    <v-group :config="{ x: props.x + props.width - 0.33 * props.width, y: props.y + 0.5 * props.height - 0.5 * getEstimatedItemEntriesHeight(generateItems(props.converter.output_items).length) }">
      <template v-for="entry in generateItems(props.converter.output_items)" :key="'output-' + entry.item">
        <item-entry :item="entry.item" :count="entry.count" :x="entry.x" :y="entry.y" :scale-factor="entry.scaleFactor" :icon-width="entry.iconWidth" :icon-height="entry.iconHeight"/>
      </template>
    </v-group>

    <!-- Arrow connecting input to output -->
    <template>
      <v-arrow :config="{
        points: [props.x + 0.4 * props.width, props.y + props.height / 2, props.x + props.width - 0.37 * props.width, props.y + props.height / 2],
        pointerLength: 0.03 * props.width,
        pointerWidth: 0.06 * props.height,
        fill: props.converter.running_stage === 'trading' ? 'purple' : 'white',
        stroke: props.converter.running_stage === 'trading' ? 'purple' : 'white',
        strokeWidth: 0.05 * props.height
      }" @click="props.onClick" />
      <template v-if="!props.producible && !props.converter.used">
        <v-line :config="{
          points: [props.x + 0.45 * props.width, props.y + 0.45 * props.height, props.x + 0.55 * props.width, props.y + 0.55 * props.height],
          stroke: 'red',
          strokeWidth: 0.02 * props.height,
          opacity: stageOpacity(props.converter.running_stage)
        }" />
        <v-line :config="{
          points: [props.x + 0.45 * props.width, props.y + 0.55 * props.height, props.x + 0.55 * props.width, props.y + 0.45 * props.height],
          stroke: 'red',
          strokeWidth: 0.02 * props.height,
          opacity: stageOpacity(props.converter.running_stage)
        }" />
      </template>
      <template v-else>
        <v-circle :config="{
          x: props.x + props.width / 2,
          y: props.y + props.height / 2,
          radius: 0.05 * props.width,
          fill: '',
          stroke: props.converter.used ? 'gray' : 'yellow',
          strokeWidth: 0.02 * props.height,
          opacity: stageOpacity(props.converter.running_stage)
        }" />
        <template v-if="props.converter.used">
          <v-line :config="{
            points: [props.x + 0.45 * props.width, props.y + 0.5 * props.height, props.x + 0.5 * props.width, props.y + 0.57 * props.height, props.x + 0.57 * props.width, props.y + 0.4 * props.height],
            stroke: 'lightgreen',
            strokeWidth: 0.02 * props.height,
            opacity: stageOpacity(props.converter.running_stage)
          }" />
        </template>
      </template>
    </template>
</template>

<script setup lang="ts">
import ItemEntry from '@/components/ItemEntry.vue';
import { getItemsValue } from '@/interfaces/GameConfig';
import type { Converter, GameState } from '@/interfaces/GameState';



const props = defineProps<{
  x: number;
  y: number;
  width: number;
  height: number;
  scaleFactor: number;
  producible: boolean;
  converter: Converter;
  gameState: GameState;
  onClick: () => void;
}>();


const stageOpacity = (running_stage: string) => {
  return props.gameState.stage === running_stage ? 1 : 0.5;
}


const generateItems = (items: {[key: string]: number}) => {
  const entries: { item: string, count: number, x: number, y: number, scaleFactor: number, iconWidth: number, iconHeight: number, isFirst: boolean}[] = [];
  let num = 0;
  for (let item in items) {
    if (items[item] === 0) continue;
    entries.push({
      item: item,
      count: items[item],
      x: Math.floor(num / 4) * 0.8 / 6 * props.width,
      y: (num % 4) * 0.6 / 4 * props.height,
      scaleFactor: props.scaleFactor,
      iconWidth: 0.6/ 6 * props.width,
      iconHeight: 0.6 / 4 * props.height,
      isFirst: num === 0
    });
    num++;
  }
  return entries;
}

const researchItemScaleFactor = 0.8;
const generateResearchItems = (items: {[key: string]: number}, column: number) => {
  const entries: { item: string, count: number, x: number, y: number, scaleFactor: number, iconWidth: number, iconHeight: number, isFirst: boolean}[] = [];
  let num = 0;
  for (let item in items) {
    if (items[item] === 0) continue;
    entries.push({
      item: item,
      count: items[item],
      x: column * 0.9 / 6 * props.width,
      y: num * 0.8 / 4 * props.height,
      scaleFactor: props.scaleFactor * researchItemScaleFactor,
      iconWidth: 0.8 / 6 * props.width * researchItemScaleFactor,
      iconHeight: 0.8 / 4 * props.height * researchItemScaleFactor,
      isFirst: num === 0
    });
    num++;
  }
  return entries;
}

const getEstimatedItemEntriesHeight = (len: number) => {
  return len * 0.6 / 4 * props.height;
}

</script>
