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
    <template v-if="isColony()">
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
      v-if="props.factory.feature.type === 'Normal' && props.factory.feature.properties['upgrades'] && props.factory.feature.properties['upgrades'].length > 0">
      <template v-if="typeof props.factory.feature.properties['upgrades'][0]['cost'] !== 'string'">
        <converter-entry :="getUpgradeCostConverterConfig(props.factory.feature.properties['upgrades'][0]['cost'], 0)" />
      </template>
      <template v-for="id in Object.keys(props.factory.feature.properties['upgrades']).map(Number)" :key="id">
        <template v-if="typeof props.factory.feature.properties['upgrades'][id]['cost'] === 'string'">
          <v-text 
            :config="getUpgradeCostTextConfig(
              props.factory.feature.properties['upgrades'].length, 
              props.factory.feature.properties['upgrades'][id]['cost'], 
              id)"
            @click="() => {
              props.upgradeNormal(id);
            }" 
            @touchstart="() => {
              props.upgradeNormal(id);
            }"
          />
        </template>
      </template>
    </template>
    <template v-if="directPreview()">
      <template v-for="converterConfig in getPreviewConverterConfigs()" :key="converterConfig.converter.input_items">
        <converter-entry :="converterConfig" />
      </template>
      <v-text :config="getPreviewConverterValueTextConfig()" />
    </template>
    <template v-if="isColony() && props.factory.feature.properties['caylion_colony']">
      <v-circle :config="{
        x: props.x + props.width * 0.94,
        y: props.y + props.height * 0.09,
        radius: 0.05 * props.width,
        fill: 'darkgreen',
        stroke: 'green',
        strokeWidth: 0.02 * props.height
      }"/>
      <v-text :config="getCaylionDescConfig()" />
    </template>
    <template v-if="props.factory.preview && !directPreview() && !props.factory.feature.properties['multipleUpgrades']">
      <v-circle :config="{
        x: props.x + props.width / 2,
        y: props.y + props.height * 0.9,
        radius: 0.05 * props.width,
        fill: isPreview ? 'white' : 'gray',
        stroke: isPreview ? 'gray' : 'white',
        strokeWidth: 0.02 * props.height
      }" @click="togglePreview" @touchstart="togglePreview" />
    </template>
    <template v-if="getFleetCost() > 0">
      <item-entry 
        :item="'Fleet'" 
        :count="getFleetCost()" 
        :x="props.x + props.width * 0.12"
        :y="props.y + props.height * 0.18"
        :scale-factor="props.scaleFactor" 
        :icon-width="0.5 / 6 * props.width" 
        :icon-height="0.5 / 4 * props.height"
        :preview="isPreview"
      />
    </template>
  </v-group>
</template>

<script setup lang="ts">
import { defineProps, ref } from 'vue';
import { GameState, Player, type Factory } from '@/interfaces/GameState';
import ItemEntry from '@/components/ItemEntry.vue';
import ConverterEntry from '@/components/ConverterEntry.vue';
import { Converter } from '@/interfaces/GameState';
import { getItemsDonationValue, getItemsValue, getSpecieColor } from '@/interfaces/GameConfig';
import { getIconSvg } from '@/utils/icon';
import { factory } from 'typescript';

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

const isPreview = ref(false);

const togglePreview = () => {
  isPreview.value = !isPreview.value;
}

const getFleetCost = () => {
  return props.factory.feature.properties[isPreview.value ? 'upgradeFleetCost' : 'fleetCost'] || 0;
}

const directPreview = () => {
  return props.factory.preview && (isColony() || props.factory.feature.type === 'Research');
}
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

const getFactoryBackgroundImage = () => {
  const img = new Image();
  img.src = new URL('/images/factory-bg.webp', import.meta.url).href; // 确保图片路径正确
  return img;
};

const produceClick = (converter_index: number) => {
  props.produce(converter_index);
}

const isColony = () => {
  return props.factory.feature.type === 'Colony' || props.factory.feature.properties['isColony'];
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
    width = props.width * 0.75;
    height = props.height * 0.75;
    xCenter = props.x + props.width * 0.125 + width / 2;
    yCenter = props.y + props.height * 0.425 + height / 2;
  }
  if (isColony()) {
    width = props.width * 0.75;
    height = props.height * 0.75;
    xCenter = props.x + props.width * 0.375 + width / 2;
    yCenter = props.y + props.height * 0.5 + height / 2;
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
    if (props.factory.feature.type === 'Normal' || isColony()) {
      value = "升级后：" + value;
    }
    if (props.factory.feature.type === 'Meta') {
      value = "打出：" + value;
    }
    if (isColony()) {
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

const getUpgradeCostTextConfig = (totalCount: number, text: string, id: number) => {
  let pos: [number, number][] = []
  let multiplier: number[] = []
  if (totalCount <= 3) {
    pos = [
      [props.x + 0.01 * props.width, props.y + 0.91 * props.height],
      [props.x + 0.98 * props.width, props.y + 0.91 * props.height],
      [props.x + 0.5 * props.width, props.y + 0.91 * props.height],
    ]
    multiplier = [0, 1, 0.5];
  } else if (totalCount <= 4) {
    pos = [
      [props.x + 0.01 * props.width, props.y + 0.83 * props.height],
      [props.x + 0.01 * props.width, props.y + 0.93 * props.height],
      [props.x + 0.98 * props.width, props.y + 0.83 * props.height],
      [props.x + 0.98 * props.width, props.y + 0.93 * props.height]
    ]
    multiplier = [0, 0, 1, 1];
  }
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
  let xCenter = props.x + props.width * 0.5;
  let yCenter = props.y + props.height * 0.5;
  if (props.factory.feature.type === 'Research') {
    yCenter -= 0.2 * props.height;
  }
  if (isColony()) {
    yCenter -= 0.2 * props.height;
  }
  const res = [];
  const converters = isPreview.value ? props.factory.preview! : props.factory.converters;
  const totalCount = converters.length;

  const scaleFactor = 1 / Math.pow(1.5, totalCount - 1);
  const estimateHeight = 0.4 * props.height * scaleFactor;
  let width = props.width * scaleFactor;
  let height = props.height * scaleFactor;
  for (let i = 0; i < converters.length; i++) {
    res.push({
      x: xCenter - width * 0.5,
      y: yCenter - height * 0.5 + (i - (totalCount - 1) / 2) * estimateHeight,
      width: width,
      height: height,
      scaleFactor: props.scaleFactor,
      producible: props.producible(converters[i].input_items),
      gameState: props.gameState,
      preview: isPreview.value,
      converter: converters[i], 
      onClick: () => produceClick(i)
    })
  }
  return res;
}

const getConverterValueTextConfig = () => {
  const fontSize = 0.08 * props.height;
  const converterValue = getConvertersValue(isPreview.value ? props.factory.preview! : props.factory.converters);
  const estimateWidth = converterValue.length * fontSize;
  return {
    text: converterValue,
    fontSize: fontSize,
    fontStyle: 'italic',
    fontFamily: 'Calibri',
    fill: 'white',
    x: props.x + 0.5 * props.width - estimateWidth / 4,
    y: props.y + 0.15 * props.height,
    opacity: isPreview.value ? 0.5 : 1
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
