import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
// import router from './router'

import * as chart from 'chart.js'
import { CrosshairPlugin } from 'chartjs-plugin-crosshair'

chart.Chart.register(
  chart.LineController,
  chart.ScatterController,
  chart.BarController,
  chart.LineElement,
  chart.PointElement,
  chart.BarElement,
  chart.LinearScale,
  chart.LogarithmicScale,
  chart.Title,
  chart.CategoryScale,
  chart.Tooltip,
  CrosshairPlugin,
)

const app = createApp(App)

// app.use(router)

app.mount('body')
