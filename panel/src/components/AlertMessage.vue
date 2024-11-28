<template>
  <n-alert v-if="props.visible" :type="props.type" closable :title="props.title">
    <template v-if="props.icon" #icon>
      <n-icon :size="50">
        <ItemIcon :item="props.icon" />
      </n-icon>
    </template>
    {{ props.content }}
  </n-alert>
</template>

<script setup lang="ts">
import { defineComponent } from 'vue'
import { NAlert, NIcon } from 'naive-ui'
import ItemIcon from './ItemIcon.vue';
const props = defineProps<{
  title: string
  content: string
  type: "default" | "error" | "info" | "success" | "warning" | undefined
  visible: boolean
  icon?: string
}>()
</script>

<style scoped>


</style>
