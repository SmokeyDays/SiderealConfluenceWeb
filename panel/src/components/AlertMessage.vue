<template>
  <n-alert v-if="props.visible" :type="props.type" closable :title="props.title">
    {{ props.content }}
  </n-alert>
</template>

<script setup lang="ts">
import { defineComponent } from 'vue'
import { NAlert } from 'naive-ui'

const props = defineProps<{
  title: string
  content: string
  type: "default" | "error" | "info" | "success" | "warning" | undefined
  visible: boolean
}>()

</script>

<style scoped>


</style>
