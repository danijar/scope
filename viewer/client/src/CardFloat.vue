<script setup>

import { reactive, computed, watch, onMounted, useTemplateRef } from 'vue'
import Card from './Card.vue'
import * as chartjs from 'chart.js'
import * as chartjsHelpers from "chart.js/helpers";

chartjs.Chart.register(chartjs.LineController, chartjs.ScatterController, chartjs.LineElement, chartjs.PointElement, chartjs.LinearScale, chartjs.LogarithmicScale, chartjs.Title, chartjs.CategoryScale, chartjs.Tooltip)

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

const colors = [
  '#e41a1c',
  '#377eb8',
  '#4daf4a',
  '#984ea3',
  '#ff7f00',
  '#ffd92e',
  '#a65628',
  '#f781bf',
  '#999999',
]

onMounted(async () => {

  chart[0] = new chartjs.Chart(canvas.value, {
    type: 'line',
    data: { datasets: [] },
    options: {
      animation: false,
      responsive: true,
      maintainAspectRatio: false,
      resizeDelay: 50,
      pointHoverRadius: 0,
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
        updateLegend(dataX)

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
  updateLegend(0)

  state.status = ''
})

function updateLegend(nearestStep) {
  state.legend = chart[0].data.datasets.map(dataset => {
    const index = bisectNearestX(dataset.data, nearestStep)
    const value = dataset.data[index].y

    let formattedValue
    if (0.01 <= Math.abs(value) && Math.abs(value) <= 10000)
      formattedValue = value.toFixed(3)
    else
      formattedValue = value.toExponential(2)

    return {
      run: dataset.label,
      color: dataset.borderColor,
      step: dataset.data[index].x,
      value: value,
      formattedValue: formattedValue,
    }
  })
}

function bisectNearestX(array, target) {
  let lo = 0
  let hi = array.length - 1
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2)
    const val = array[mid].x
    if (target > val)
      lo = mid + 1
    else if (target < val)
      hi = mid - 1
    else
      return mid
  }
  lo = Math.max(0, Math.min(lo, array.length - 1))
  hi = Math.max(0, Math.min(hi, array.length - 1))
  return (array[lo] - target) < (target - array[hi]) ? lo : hi
}

function toggleLogScaleX() {
  if (chart[0].options.scales.y.type == 'linear')
    chart[0].options.scales.y.type = 'logarithmic'
  else
    chart[0].options.scales.y.type = 'linear'
  chart[0].update()
}

</script>

<template>
<Card :name="props.name" :status="state.status">

<template #buttons>
  <span class="btn icon" @click="toggleLogScaleX">query_stats</span>
</template>

<template #default>
  <div class="content layoutCol">

    <div class="chart">
      <canvas ref="canvas"></canvas>
    </div>

    <div class="legend">
      <!-- <div class="entries"> -->
      <!-- <div class="entry head"><div></div><div>Run</div><div>Step</div><div>Value</div></div> -->
      <div class="entry" v-for="entry in state.legend">
        <div :style="{ background: entry.color }"></div>
        <div>{{ entry.run }}</div>
        <div>{{ entry.step }}</div>
        <div>{{ entry.formattedValue }}</div>
      </div>
      <!-- </div> -->
    </div>

  </div>
</template>

</Card>
</template>

<style scoped>

.content { height: 100%; width: 100%; overflow: hidden; }

.chart { flex: 1 1 100%; position: relative; overflow: hidden; }

.legend { flex: 0 0 content; max-height: 40%; width: 100%; display: flex; flex-direction: column; overflow: auto; margin: 1.5rem 0 0; font-family: monospace; }
.entry { width: 100%; display: flex; align-items: center; margin-bottom: .5rem; }

.entry div:nth-child(1) { flex: 0 0 1rem; margin-right: .5rem; width: 1rem; height: 100%; min-height: 1rem; border-radius: .2rem; }
.entry div:nth-child(2) { flex: 1 1 content; margin-right: .5rem; word-break: break-all; line-height: 0.95; font-size: 0.8rem; }
.entry div:nth-child(3) { flex: 0 0 10ch; margin-right: .5rem; text-align: right; }
.entry div:nth-child(4) { flex: 0 0 10ch; padding-right: .5rem; text-align: right; }

</style>

