<script setup>

import { reactive, computed, watch, onMounted, useTemplateRef } from 'vue'
import Card from './Card.vue'
import * as chartjs from 'chart.js'
import * as chartjsHelpers from "chart.js/helpers";

chartjs.Chart.register(chartjs.LineController, chartjs.ScatterController, chartjs.LineElement, chartjs.PointElement, chartjs.LinearScale, chartjs.Title, chartjs.CategoryScale, chartjs.Tooltip)

const props = defineProps({
  name: { type: String, required: true },
  cols: { type: Array, required: true },
})

const state = reactive({
  status: '',
  cols: [],
  legend: [],
})

const canvas = useTemplateRef('canvas')

const chart = [null]

// TODO: Move into helper file
function binarySearchAttrX(array, target) {
  let lo = 0
  let hi = array.length - 1
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2)
    const cur = array[mid].x // NOTE
    if (target > cur)
      lo = mid + 1
    if (target < cur)
      hi = mid - 1
  }
  // TODO: actually return nearest point
  return Math.max(0, Math.min(lo, array.length - 1))
}

onMounted(async () => {

  chart[0] = new chartjs.Chart(canvas.value, {
    type: 'line',
    data: { datasets: [] },
    options: {
      animation: false,
      responsive: true,
      maintainAspectRatio: false,
      resizeDelay: 50,
      scales: {
        x: { type: 'linear', position: 'bottom', maxRotation: 0 },
        y: { type: 'linear', position: 'left', maxRotation: 0 }
      },
      plugins: { tooltip: { enabled: false } },
      events: ['mousemove'],
    },
    plugins: [{
      id: 'mousemove',
      beforeEvent(chart, args, pluginOptions) {
        const event = args.event;
        if (event.type !== 'mousemove')
          return
        // TODO: add delay to compute this less frequently
        const canvasPos = chartjsHelpers.getRelativePosition(event, chart)
        const dataX = chart.scales.x.getValueForPixel(canvasPos.x)
        const dataY = chart.scales.y.getValueForPixel(canvasPos.y)
        // console.log(dataX, dataY)

        // chart.data.datasets.map(dataset => {
        //   console.log(binarySearchAttrX(dataset.data, dataX))
        // })

        state.legend = chart.data.datasets.map(dataset => {
          const index = binarySearchAttrX(dataset.data, dataX);
          return {
            run: dataset.label,
            color: dataset.borderColor,
            step: dataset.data[index].x,
            value: dataset.data[index].y,
          }
        })

      }
    }],
  })

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
      borderColor: colors[i % colors.length],  // TODO
      borderWidth: 1,
    })
    i++
  }

  chart[0].data.datasets = datasets
  chart[0].update()

  state.status = ''
})

</script>

<template>
<Card :name="props.name" :status="state.status">
<div class="content layoutCol">

  <div class="chart">
    <canvas ref="canvas"></canvas>
  </div>

  <div class="legend">
    <table>
      <tr class="entry" v-for="entry in state.legend">
        <td class="handle" :style="{ background: entry.color }"></td>
        <td>{{ entry.run }}</td>
        <td>{{ entry.step }}</td>
        <td>{{ entry.value }}</td>
      </tr>
    </table>
  </div>

  <!-- <div v-for="col in state.cols" class="col"> -->
  <!--   <h3> {{ col.run }}</h3> -->
  <!--   <p>{{ col.values }}</p> -->
  <!-- </div> -->

</div>
</Card>
</template>

<style scoped>

.content { height: 100%; width: 100%; overflow: hidden; }

.chart { flex: 1 1 100%; position: relative; overflow: hidden; }

.legend { flex: 0 1 content; width: 100%; }
table { width: 100%; }

</style>

