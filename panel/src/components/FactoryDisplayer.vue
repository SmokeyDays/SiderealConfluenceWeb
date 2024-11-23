<template>
  <v-group>
    <!-- Factory background -->
    <v-image :config="{
      x: props.x,
      y: props.y,
      width: props.width,
      height: props.height,
      cornerRadius: 10,
      opacity: 0.9,
      image: getFactoryBackgroundImage()
    }" />

    <v-text :config="getTitleConfig(props.factory.name)" />

    <template v-for="converterConfig in getConverterConfigs()" :key="converterConfig.converter.input_items">
      <converter-entry :="converterConfig" />
    </template>
    
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
    <template 
      v-if="props.factory.feature.type === 'Normal' && props.factory.feature.properties['upgrade_cost'] && props.factory.feature.properties['upgrade_cost'].length > 0">
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
      <template v-for="converterConfig in getPreviewConverterConfigs()" :key="converterConfig.converter.input_items">
        <converter-entry :="converterConfig" />
      </template>
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
import { getItemsDonationValue, getItemsValue, getSpecieColor } from '@/interfaces/GameConfig';
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
  let donationValue = getItemsDonationValue(converter.output_items).toString();
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
  produce: (converter_index: number) => void;
  upgradeColony: () => void;
  upgradeNormal: (id: number) => void;
  me: Player;
}


const props = defineProps<FactoryConfig>();

const getFactoryBackgroundImage = () => {
  const img = new Image();
  img.src = new URL('/images/factory-bg.webp', import.meta.url).href; // 确保图片路径正确
  return img;
};

const produceClick = (converter_index: number) => {
  props.produce(converter_index);
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

const getPreviewConverterConfigs = () => {
  let xCenter = props.x + props.width * 0.5;
  let yCenter = props.y + props.height * 0.85;
  let width = props.width * 0.4;
  let height = props.height * 0.4; 
  if (props.factory.feature.type === 'Research') {
    xCenter = props.x + props.width * 0.325;
    yCenter = props.y + props.height * 0.625;
    width = props.width * 0.75;
    height = props.height * 0.75;
  }
  if (props.factory.feature.type === 'Colony') {
    xCenter = props.x + props.width * 0.575;
    yCenter = props.y + props.height * 0.7;
    width = props.width * 0.75;
    height = props.height * 0.75;
  }
  const res = [];
  const totalCount = props.factory.preview!.length;
  const totalHeight = height * totalCount;
  let curY = yCenter - totalHeight / 2;
  for (let i = 0; i < props.factory.preview!.length; i++) {
    res.push({
      x: xCenter - width / 2,
      y: curY,
      width: width,
      height: height,
      scaleFactor: props.scaleFactor,
      converter: props.factory.preview![i], 
      producible: props.producible(props.factory.preview![i].input_items),
      gameState: props.gameState,
      onClick: () => {}
    })
    curY += height;
  }
  return res;
}

const getConvertersValue = (converters: Converter[]) => {
  let value = "";
  for (let i = 0; i < converters.length; i++) {
    if (i != 0) value += " 以及 ";
    value += getConverterValue(converters[i]);
  }
  return value;
}

const getPreviewConverterValueTextConfig = () => {
  let value = getConvertersValue(props.factory.preview!);
  let fontSize = 0.03 * props.height;
  let x = props.x + props.width * 0.5;
  let y = props.y + props.height * 0.93;
  if (props.factory.feature.type !== 'Research') {
    if (props.factory.feature.type === 'Normal' || props.factory.feature.type === 'Colony') {
      value = "升级后：" + value;
    }
    if (props.factory.feature.type === 'Meta') {
      value = "打出：" + value;
    }
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
  const converter: Converter = new Converter(props.factory.feature.properties['upgrade_cost'], { [newClimate]: 1 }, 'trading', false);
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

const getConverterConfigs = () => {
  let y = props.y;
  if (props.factory.feature.type === 'Research') {
    y -= 0.2 * props.height;
  }
  if (props.factory.feature.type === 'Colony') {
    y -= 0.2 * props.height;
  }
  const res = [];
  for (let i = 0; i < props.factory.converters.length; i++) {
    res.push({
      x: props.x,
      y: y + i * props.height,
      width: props.width,
      height: props.height,
      scaleFactor: props.scaleFactor,
      producible: props.producible(props.factory.converters[i].input_items),
      gameState: props.gameState,
      converter: props.factory.converters[i], 
      onClick: () => produceClick(i)
    })
  }
  return res;
}

const getConverterValueTextConfig = () => {
  const fontSize = 0.08 * props.height;
  const converterValue = getConvertersValue(props.factory.converters);
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
