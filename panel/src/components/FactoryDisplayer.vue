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

    <converter-entry :="getMainConverterConfig()" />
    
    <template v-if="props.factory.feature.type === 'Research'">
      <v-text :config="getTechTextConfig()" />
    </template>
    <template v-if="props.factory.feature.type === 'Colony'">
      <item-entry 
        :item="props.factory.feature.properties['climate']" 
        :count="1" 
        :x="props.x + 0.36 * props.width"
        :y="props.y + 0.4 * props.height"
        :scale-factor="props.scaleFactor" 
        :icon-width="1.5 / 6 * props.width" 
        :icon-height="1.5 / 4 * props.height" 
        :desc="props.factory.feature.properties['climate'][0]"
      />
      <converter-entry v-if="!props.factory.feature.properties['upgraded']" :="getColonyUpgradeConverterConfig()" />
    </template>
    <template v-if="props.factory.feature.type === 'Normal' && props.factory.feature.properties['upgrade_cost'].length > 0">
      <template v-if="typeof props.factory.feature.properties['upgrade_cost'][0] !== 'string'">
        <converter-entry :="getUpgradeCostConverterConfig(props.factory.feature.properties['upgrade_cost'][0], 0)" />
      </template>
      <template v-for="id in Object.keys(props.factory.feature.properties['upgrade_cost']).map(Number)" :key="id">
        <template v-if="typeof props.factory.feature.properties['upgrade_cost'][id] === 'string'">
          <v-text :config="getUpgradeCostTextConfig(props.factory.feature.properties['upgrade_cost'][id], id)" @click="() => {
            props.upgradeNormal(id);
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
import ConverterEntry from '@/components/ConverterEntry.vue';
import { Converter } from '@/interfaces/GameState';
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
  producible: (input_items: { [key: string]: number } | [{ [key: string]: number }]) => boolean;
  gameState: GameState;
  produce: () => void;
  research: () => void;
  upgradeColony: () => void;
  upgradeNormal: (id: number) => void;
}


const props = defineProps<FactoryConfig>();

const produceClick = () => {
  if (props.factory.converter.used || !props.producible) {
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
    y: props.y + props.height - 0.4 * props.height
  }
}

const getTechPreviewConverterConfig = () => {
}

const getColonyUpgradeConverterConfig = () => {
  const converter: Converter = new Converter(props.factory.feature.properties['upgrade_cost'], {}, {}, 'trading', false);
  return {
    x: props.x - 0.05 * props.width,
    y: props.y + 0.5 * props.height,
    width: props.width * 0.75,
    height: props.height * 0.75,
    scaleFactor: props.scaleFactor,
    producible: props.producible(props.factory.feature.properties['upgrade_cost']),
    gameState: props.gameState,
    converter: converter,
    onClick: props.upgradeColony
  }
}

const getUpgradeCostConverterConfig = (converter: Converter, id: number) => {
  return {
    x: props.x - 0.05 * props.width,
    y: props.y + 0.65 * props.height,
    width: props.width * 0.5,
    height: props.height * 0.5,
    scaleFactor: props.scaleFactor,
    producible: props.producible(converter.input_items),
    gameState: props.gameState,
    converter: converter,
    onClick: () => props.upgradeNormal(id)
  }
}

const getUpgradeCostTextConfig = (text: string, id: number) => {
  const pos = [
    [props.x + 0.05 * props.width, props.y + 0.9 * props.height],
    [props.x + 0.95 * props.width, props.y + 0.9 * props.height],
    [props.x + 0.5 * props.width, props.y + 0.9 * props.height]
  ]
  const multiplier = [0, 1, 0.5];
  const fontSize = 0.05 * props.height;
  const estimateWidth = text.length * fontSize;
  return {
    text: text,
    fontSize: fontSize,
    fill: 'white',
    x: pos[id][0] - multiplier[id] * estimateWidth,
    y: pos[id][1]
  }
}

const getMainInputItems = () => {
  if (props.factory.feature.type === 'Research') {
    return props.factory.feature.properties['research_cost'];
  }
  return props.factory.converter.input_items;
}

const getMainConverterConfig = () => {
  let y = props.y;
  if (props.factory.feature.type === 'Research') {
    y -= 0.2 * props.height;
  }
  if (props.factory.feature.type === 'Colony') {
    y -= 0.2 * props.height;
  }
  return {
    x: props.x,
    y: y,
    width: props.width,
    height: props.height,
    scaleFactor: props.scaleFactor,
    producible: props.producible(props.factory.converter.input_items),
    gameState: props.gameState,
    converter: props.factory.converter, 
    onClick: produceClick
  }
}
</script>
