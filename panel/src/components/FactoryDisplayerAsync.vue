<script setup lang="ts">
import { Player, type Factory } from '@/interfaces/GameState';
import FactoryDisplayer, { type FactoryConfig } from '@/components/FactoryDisplayer.vue';
import { ref } from 'vue';
import { factoryLib } from '@/interfaces/FactoryLib';
import { NEmpty } from 'naive-ui';

const props = defineProps<{
  roomName: string;
  me: Player;
  factory: string | Factory;
  getFactoryConfig: (me: Player, factory: Factory, x: number, y: number) => FactoryConfig;
}>();

const factory = ref<Factory | null>(null);

if (typeof props.factory === 'string') {
  factoryLib.getFactory(props.roomName, props.me.user_id, props.factory).then((f: Factory) => {
    factory.value = f;
  });
} else {
  console.log(props.factory);
  factory.value = props.factory;
}
</script>

<template>
  <template v-if="factory">
    <v-stage :config="{ width: getFactoryConfig(props.me, factory, 0, 0).width, height: getFactoryConfig(props.me, factory, 0, 0).height }">
      <v-layer>
        <FactoryDisplayer :="getFactoryConfig(props.me, factory, 0, 0)" />
      </v-layer>
    </v-stage>
  </template>
  <template v-else>
    <n-empty description="预览加载中..." />
  </template>
</template>