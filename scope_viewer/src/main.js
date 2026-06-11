import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'

import * as chart from 'chart.js'
 import { ZoomPlugin } from './chartZoomPlugin.js'

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
  ZoomPlugin,
)

const app = createApp(App)

// app.config.errorHandler = (err, vm, info) => {
//   console.error('Error:', err)
//   console.error('Vue component:', vm)
//   console.error('Additional info:', info)
// };

app.mount('body')

document.fonts.load('24px "Material Symbols Outlined"').then(results => {
  if (results.length)
    document.body.classList.add('icon-font-loaded')
  else
    console.error('Failed to load icon font')
})
