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

    <converter 
      :x="props.x" 
      :y="props.y" 
      :width="props.width" 
      :height="props.height" 
      :scale-factor="props.scaleFactor" 
      :producible="props.producible" 
      :used="props.factory.used" 
      :run_in_trading="props.factory.run_in_trading" 
      :stage-opacity="stageOpacity()"
      :input_items="getMainInputItems()"
      :output_items="props.factory.output_items"
    />
    
    <template v-if="props.factory.feature.type === 'Research'">
      <v-text :config="getTechTextConfig()" />
    </template>
    <template v-if="props.factory.feature.type === 'Colony'">
      <item-entry 
        :item="props.factory.feature.properties['climate']" 
        :count="1" 
        :x="props.x + props.width - 0.4 * props.width" 
        :y="props.y + 0.5 * props.height - 0.47 * props.height" 
        :scale-factor="props.scaleFactor" 
        :icon-width="0.6 / 6 * props.width" 
        :icon-height="0.6 / 4 * props.height" 
      />
      <v-text :config="{
        text: props.factory.feature.properties['climate'][0],
        fontSize: 0.05 * props.height,
        fill: 'black',
        x: props.x + props.width - 0.4 * props.width + 0.04 * props.width,
        y: props.y + 0.5 * props.height - 0.42 * props.height
      }" />
    </template>
  </v-group>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import { GameState, type Factory } from '@/interfaces/GameState';
import ItemEntry from '@/components/ItemEntry.vue';
import Converter from '@/components/Converter.vue';
import { getSpecieColor } from '@/interfaces/GameConfig';
import { getIconSvg } from '@/utils/icon';

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


const props = defineProps<FactoryConfig>();
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

const getTechTextConfig = () => {
  const desc = '发明：' + props.factory.feature.properties['tech'];
  const estimateWidth = desc.length * 0.05 * props.height;
  return {
    text: desc,
    fontSize: 0.05 * props.height,
    fill: 'white',
    x: props.x + props.width / 2 - estimateWidth / 2,
    y: props.y + props.height - 0.1 * props.height
  }
}

const getMainInputItems = () => {
  if (props.factory.feature.type === 'Research') {
    return props.factory.feature.properties['research_cost'];
  }
  return props.factory.input_items;
}
</script>
