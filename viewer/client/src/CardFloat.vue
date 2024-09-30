<script setup>

import { reactive, computed, watch, onMounted, useTemplateRef } from 'vue'
import Card from './Card.vue'
import * as chartjs from 'chart.js'

chartjs.Chart.register(chartjs.LineController, chartjs.ScatterController, chartjs.LineElement, chartjs.PointElement, chartjs.LinearScale, chartjs.Title, chartjs.CategoryScale, chartjs.Tooltip)

const props = defineProps({
  name: { type: String, required: true },
  cols: { type: Array, required: true },
})

const state = reactive({
  status: '',
  cols: [],
})

const canvas = useTemplateRef('canvas')

const chart = [null]

onMounted(async () => {
  state.status = 'loading...'

  const requests = props.cols.map(col => fetch(`/api/col/${col}`))
  const results = await Promise.all(requests.map(async x => (await x).json()))
  state.cols = props.cols.map(function(col, i) {
    const result = results[i]
    return {
      run: col.substr(0, col.lastIndexOf(':', col.lastIndexOf(':') - 1)),
      steps: result.steps,
      values: result.values,
    }
  })

  const colors = [
    '#ff0000',
    '#00ff00',
    '#0000ff',
  ]

  const datasets = []
  let i = 0;
  for (const col of state.cols) {
    const data = col.steps.map((step, i) => ({ x: step, y: col.values[i]}))
    datasets.push({
      label: col.run,
      data: data,
      fill: false,
      pointRadius: 0,
      borderColor: colors[i % colors.length],
    })
    i++
  }

  chart[0] = new chartjs.Chart(canvas.value, {
    type: 'line',
    // type: 'scatter',
    data: { datasets: datasets },
    options: {
      animation: false,
      responsive: true,
      maintainAspectRatio: false,
      resizeDelay: 50,
      // showLines: true,
      // parsing: { xAxisKey: 'x', yAxisKey: 'y' },
      // scales: {
      //   xAxes: [{ type: 'linear', position: 'bottom', }],
      //   yAxes: [{ type: 'linear' }],
      // }
      scales: {
        x: { type: 'linear', position: 'bottom' },
        y: { type: 'linear', position: 'left' }
      },
      plugins: {
        tooltip: {
          enabled: true,
          mode: 'index',
          intersect: false,
        }
      }
    }
  })

  state.status = ''
})

// function refreshChart() {
//   console.log('update')
//   chart[0].update()
// }

// watch(state.cols, () => {
//   console.log(state.chart)
//   for (const col of state.cols) {
//     state.chart.data.datasets.push({
//       label: col.run,
//       data: { xs: col.steps, ys: col.values },
//       // borderColor: `rgb(${Math.random()*255},${Math.random()*255},${Math.random()*255})`,
//       // tension: 0.1
//     })
//   }
//   console.log('UPDATING')
//   state.chart.update()
// })

</script>

<template>
<Card :name="props.name" :status="state.status">

  <div class="chart">
    <canvas ref="canvas"></canvas>
  </div>

  <!-- <div v-for="col in state.cols" class="col"> -->
  <!--   <h3> {{ col.run }}</h3> -->
  <!--   <p>{{ col.values }}</p> -->
  <!-- </div> -->

</Card>
</template>

<style scoped>

.col { margin: 1rem 0 0; }
.col:first-child { margin-top: 0 }

.chart {
  position: relative;
  width: 100%;
  height: 100%;
}

/* canvas { width: 100%; height: 100%; } */

</style>

