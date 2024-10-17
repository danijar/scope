<script setup>

import { reactive, computed, watch, onMounted, ref, useTemplateRef } from 'vue'
import store from './store.js'
import { reactiveCache } from './cache.js'
import { Chart } from 'chart.js'
import { getRelativePosition } from 'chart.js/helpers'
import Card from './Card.vue'

const props = defineProps({
  name: { type: String, required: true },
  cols: { type: Array, required: true },
})

const availableCols = computed(() => {
  return props.cols
    .filter(colid => colid in store.availableCols.value)
})

const datasetsCache = reactiveCache(colid => {
  const col = store.availableCols.value[colid]
  let data = col.steps.map((step, j) => ({ x: step, y: col.values[j]}))
  const mean = (vals) => vals.reduce((a, b) => a + b) / vals.length
  if (store.options.binsize)
    data = binning(data, store.options.binsize, mean)
  return {
    label: col.run,
    data: data,
    fill: false,
    pointRadius: 0,
    borderWidth: 1,
    col: col,
  }
})

watch(() => availableCols, () => {
  datasetsCache.setTo(availableCols.value)
}, { deep: true, immediate: true })

watch(() => store.options.binsize, () => {
  datasetsCache.refresh()
}, { deep: true })

const datasetsList = computed(() => {
  return props.cols
    .filter(colid => colid in datasetsCache.value)
    .map(colid => datasetsCache.value[colid])
    .map((col, i) => ({ ...col, borderColor: colors[i % colors.length] }))
})

const loading = computed(() => {
  return props.cols
    .filter(colid => store.pendingCols.value.has(colid))
    .length > 0
})

const mouseXY = ref([Number.MAX_VALUE, -Number.MAX_VALUE])

const root = useTemplateRef('root')

const chart = [null]

let prevClick = 0

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

const legend = computed(() => {
  return datasetsList.value
    .map(dataset => {
      const index = bisectNearestX(dataset.data, mouseXY.value[0])
      if (index === null)
        return null
      const step = dataset.data[index].x
      const value = dataset.data[index].y
      const formattedStep = step.toLocaleString('en-US')
      let formattedValue
      if (0.01 <= Math.abs(value) && Math.abs(value) <= 10000)
        formattedValue = value.toFixed(3)
      else
        formattedValue = value.toExponential(2)
      return {
        run: dataset.label,
        color: dataset.borderColor,
        step: step,
        value: value,
        formattedStep: formattedStep,
        formattedValue: formattedValue,
      }
    })
    .filter(entry => entry !== null)
    .sort((a, b) => {
      const distA = Math.abs(a.value - mouseXY.value[1])
      const distB = Math.abs(b.value - mouseXY.value[1])
      return distA - distB
    })
})

onMounted(() => {
  const canvas = root.value.$el.querySelector('canvas')
  chart[0] = createChart(canvas)
  updateChart()
})

watch(() => datasetsList, () => updateChart(), { deep: 2 })

function updateChart() {
  if (chart[0] === null)
    return
  chart[0].data.datasets = datasetsList.value.slice()
  chart[0].update()
}

function createChart(canvas) {
  return new Chart(canvas, {
    type: 'line',
    data: { datasets: [] },
    options: {
      animation: false,
      responsive: true,
      maintainAspectRatio: false,
      resizeDelay: 10,
      pointHoverRadius: 0,
      scales: {
        x: { type: 'linear', position: 'bottom', maxRotation: 0 },
        y: { type: 'linear', position: 'left', maxRotation: 0, },
      },
      plugins: {
        tooltip: { enabled: false },
        crosshair: {
          line: { color: 'rgba(127,127,127,0.8)' },
          sync: { enabled: false },
          zoom: {
            zoomboxBackgroundColor: 'rgba(127,127,127,0.05)',
            zoomboxBorderColor: 'rgba(127,127,127,0.8)',
          },
        },
      },
    },
    plugins: [{
      beforeEvent(chart, args, pluginOptions) {
        const event = args.event;
        if (event.type === 'mousemove') {
          // TODO: Add delay to compute this less frequently?
          const canvasPos = getRelativePosition(event, chart)
          const dataX = chart.scales.x.getValueForPixel(canvasPos.x)
          const dataY = chart.scales.y.getValueForPixel(canvasPos.y)
          mouseXY.value = [dataX, dataY]
        }
        if (event.type === 'click') {
          const now = Date.now()
          if (now - prevClick < 500) {
            const button = root.value.$el.querySelector('.reset-zoom')
            button && button.click()
            prevClick = 0
          } else {
            prevClick = now
          }
        }
      },
    }],
  })
}

function bisectNearestX(data, target, trimNull = true) {
  // This function is more complex that one would expect, because the ChartJS
  // crosshair plugin modifies the data lists in-place. We don't know exactly
  // what they do, but can be null values that we handle below.
  let lo = 0
  let hi = data.length - 1
  if (trimNull) {
    while (lo < data.length - 1 && lo < hi && data[lo].y === null) lo++
    while (hi > 0 && hi > lo && data[hi].y === null) hi--
  }
  if (!(lo < hi))
    return null
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2)
    const val = data[mid].x
    if (target > val)
      lo = mid + 1
    else if (target < val)
      hi = mid - 1
    else
      return mid
  }
  lo = Math.max(0, Math.min(lo, data.length - 1))
  hi = Math.max(0, Math.min(hi, data.length - 1))
  let index = (data[lo] - target) < (target - data[hi]) ? lo : hi
  while (index < data.length && data[index].y === null) index++
  return index < data.length ? index : null
}

function binning(data, binsize, aggFn, nullLimits = true) {
  const result = []

  if (nullLimits)
    result.push({ x: data[0].x, y: null })

  let prev = null
  let curr = null
  let vals = []
  for (const [i, point] of data.entries()) {
    curr = (Math.round(point.x / binsize) + 0.5) * binsize
    if (curr !== prev) {
      if (vals.length)
        result.push({ x: prev, y: aggFn(vals) })
      vals.length = 0
      prev = curr
    }
    vals.push(point.y)
  }
  if (vals.length)
    result.push({ x: prev, y: aggFn(vals) })

  if (nullLimits)
    result.push({ x: data[data.length - 1].x, y: null })

  return result
}

</script>

<template>
  <Card :name="props.name" :loading="loading" :scrollX="false" :scrollY="false" ref="root">
    <template #default>
      <div class="content layoutCol">
        <div ref="chart" class="chart">
          <canvas></canvas>
        </div>
        <div class="legend">
          <div class="entry" v-for="entry in legend">
            <div :style="{ background: entry.color }"></div>
            <div>{{ entry.run }}</div>
            <div>{{ entry.formattedStep }}</div>
            <div>{{ entry.formattedValue }}</div>
          </div>
        </div>
     </div>
    </template>
  </Card>
</template>

<style scoped>

.content { height: 100%; width: 100%; overflow: hidden; }

.chart { flex: 1 1 100%; position: relative; overflow: hidden; }
:deep(.reset-zoom) { display: none; }

.legend { flex: 0 0 content; max-height: 40%; width: 100%; display: flex; flex-direction: column; overflow: auto; margin: 1.5rem 0 0; }
.entry { width: 100%; display: flex; align-items: center; margin-bottom: .5rem; }

.entry { line-height: 0.95; font-family: monospace; }
.entry div:nth-child(1) { flex: 0 0 1rem; margin-right: .5rem; width: 1rem; height: 100%; min-height: 1rem; border-radius: .2rem; }
.entry div:nth-child(2) { flex: 1 1 content; margin-right: .5rem; word-break: break-all; min-width: 10rem; }
.entry div:nth-child(3) { flex: 0 0 10ch; margin-right: .5rem; text-align: right; }
.entry div:nth-child(4) { flex: 0 0 10ch; padding-right: .5rem; text-align: right; }

</style>
