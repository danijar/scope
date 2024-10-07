import './assets/main.css'

import { createApp } from 'vue'
// import { createPinia } from 'pinia'
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

// const pinia = createPinia()
const app = createApp(App)

// app.use(pinia)

// app.use(router)

// app.config.errorHandler = (err, vm, info) => {
//   console.error('Error:', err)
//   console.error('Vue component:', vm)
//   console.error('Additional info:', info)
// };

app.mount('body')
