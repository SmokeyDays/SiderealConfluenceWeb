import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import VueKonva from 'vue-konva';
import { socket } from "./utils/connect"
import './assets/main.css'

createApp(App)

const app = createApp(App);
app.use(VueKonva as any);
app.mount('#app');