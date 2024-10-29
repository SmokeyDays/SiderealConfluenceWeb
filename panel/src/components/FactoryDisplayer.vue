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
    
    <v-text :config="getConverterValueTextConfig()" /> 
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
            if (props.me.factories[props.factory.feature.properties['upgrade_cost'][id]]) {
              props.upgradeNormal(id);
            }
          }" />
        </template>
      </template>
    </template>
    <template v-if="props.factory.preview">
      <converter-entry :="getPreviewConverterConfig()" />
      <v-text :config="getPreviewConverterValueTextConfig()" />
    </template>
    <template v-if="props.factory.feature.type === 'Colony' && props.factory.feature.properties['caylion_colony']">
      <v-text :config="getCaylionDescConfig()" />
    </template>
  </v-group>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import { GameState, Player, type Factory } from '@/interfaces/GameState';
import ItemEntry from '@/components/ItemEntry.vue';
import ConverterEntry from '@/components/ConverterEntry.vue';
import { Converter } from '@/interfaces/GameState';
import { getItemsValue, getSpecieColor } from '@/interfaces/GameConfig';
import { getIconSvg } from '@/utils/icon';
import { factory } from 'typescript';


const getConverterValue = (converter: Converter) => {
  let inputValue = "";
  if (Array.isArray(converter.input_items)) {
    for (let index = 0; index < converter.input_items.length; index++) {
      if (index != 0) inputValue += " / ";
      inputValue += getItemsValue(converter.input_items[index]).toString();
    }
  } else {
    inputValue = getItemsValue(converter.input_items).toString();
  }
  let outputValue = getItemsValue(converter.output_items).toString();
  let donationValue = getItemsValue(converter.donation_items).toString();
  const donationText = donationValue === "0" ? "" : " + (" + donationValue + ")";
  return inputValue + " -> " + outputValue + donationText;
}

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
  me: Player;
}


const props = defineProps<FactoryConfig>();

const produceClick = () => {
  if (props.factory.converter.used || !props.producible) {
    return;
  }
  if (props.factory.feature.type === 'Normal' || props.factory.feature.type === 'Colony') {
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

const getPreviewConverterConfig = () => {
  let x = props.x + props.width * 0.28;
  let y = props.y + props.height * 0.65;
  let width = props.width * 0.4;
  let height = props.height * 0.4; 
  if (props.factory.feature.type === 'Research') {
    x = props.x + props.width * 0.125;
    y = props.y + props.height * 0.425;
    width = props.width * 0.75;
    height = props.height * 0.75;
  }
  if (props.factory.feature.type === 'Colony') {
    x = props.x + props.width * 0.375;
    y = props.y + props.height * 0.5;
    width = props.width * 0.75;
    height = props.height * 0.75;
  }
  return {
    x: x,
    y: y,
    width: width,
    height: height,
    scaleFactor: props.scaleFactor,
    converter: props.factory.preview!, 
    producible: props.producible(props.factory.preview!.input_items),
    gameState: props.gameState,
    onClick: () => {}
  }
}

const getPreviewConverterValueTextConfig = () => {
  let value = getConverterValue(props.factory.preview!);
  let fontSize = 0.03 * props.height;
  let x = props.x + props.width * 0.5;
  let y = props.y + props.height * 0.93;
  if (props.factory.feature.type !== 'Research') {
    value = "升级后：" + value;
    if (props.factory.feature.type === 'Colony') {
      x = props.x + props.width * 0.9;
      y = props.y + props.height * 0.75;
      fontSize = 0.05 * props.height;
    }
  } else if (props.factory.feature.type === 'Research') {
    x = props.x + props.width * 0.55;
    y = props.y + props.height * 0.68;
    fontSize = 0.06 * props.height;
  }
  let estimateWidth = value.length * fontSize;
  return {
    x: x - estimateWidth / 2,
    y: y,
    fontFamily: 'Calibri',
    fontStyle: 'italic',
    text: value,
    fontSize: fontSize,
    fill: 'white',
  }
}



const getColonyUpgradeConverterConfig = () => {
  const newClimate = props.factory.feature.properties['upgrade_climate'];
  const converter: Converter = new Converter(props.factory.feature.properties['upgrade_cost'], { [newClimate]: 1 }, {}, 'trading', false);
  return {
    x: props.x - 0.18 * props.width,
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
    x: props.x - 0.12 * props.width,
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
    [props.x + 0.01 * props.width, props.y + 0.91 * props.height],
    [props.x + 0.98 * props.width, props.y + 0.91 * props.height],
    [props.x + 0.5 * props.width, props.y + 0.91 * props.height]
  ]
  const multiplier = [0, 1, 0.5];
  const fontSize = 0.05 * props.height;
  const estimateWidth = text.length * fontSize;
  const opacity = props.me.factories[text]? 1: 0.4;
  return {
    text: text,
    fontSize: fontSize,
    fill: getSpecieColor(props.owner),
    x: pos[id][0] - multiplier[id] * estimateWidth,
    y: pos[id][1],
    opacity: opacity
  }
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

const getConverterValueTextConfig = () => {
  const fontSize = 0.08 * props.height;
  const converterValue = getConverterValue(props.factory.converter);
  const estimateWidth = converterValue.length * fontSize;
  return {
    text: converterValue,
    fontSize: fontSize,
    fontStyle: 'italic',
    fontFamily: 'Calibri',
    fill: 'white',
    x: props.x + 0.5 * props.width - estimateWidth / 4,
    y: props.y + 0.15 * props.height
  }
}

const getCaylionDescConfig = () => {
  const desc = 2 - props.factory.run_count;
  return {
    text: "x" + desc,
    fontSize: 0.1 * props.height,
    fill: getSpecieColor("Caylion"),
    x: props.x + 0.9 * props.width,
    y: props.y + 0.05 * props.height
  }
}
</script>
