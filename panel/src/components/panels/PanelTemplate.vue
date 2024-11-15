<template> 
  <div class="mask">
    <slot></slot>
  </div>
</template>
<style>
.mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}
.mask > .standard-panel {
  width: calc(min(max(60vw, 500px), 95vw));
  height: 75vh;
}
</style>
