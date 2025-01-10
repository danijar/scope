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

const aggFn = (vals) => {
  if (vals.some(x => x === null))
    return null
  return vals.reduce((a, b) => a + b) / vals.length
}

const datasetsCache = reactiveCache(colid => {
  const col = store.availableCols.value[colid]
  let data = col.steps.map((step, j) => ({ x: step, y: col.values[j]}))
  if (store.options.binsize)
    data = binning(data, store.options.binsize, aggFn)
  return {
    label: col.run,
    data: data,
    fill: false,
    pointRadius: 0,
    borderWidth: 1,
    col: col,
  }
})

watch(() => [props.cols, store.availableCols], () => {
  const available = props.cols
    .filter(colid => colid in store.availableCols.value)
  datasetsCache.setTo(available)
  for (const colid of available) {
    if (colid in datasetsCache.value) {
      const x1 = datasetsCache.value[colid].col
      const x2 = store.availableCols.value[colid]
      if (x1 !== x2)
        datasetsCache.add(colid, true)  // refresh = true
    }
  }
}, { deep: true, immediate: true })

watch(() => store.options.binsize, () => {
  datasetsCache.refresh()
}, { deep: true })

const datasetsList = computed(() => {
  return props.cols
    .sort()
    .filter(colid => colid in datasetsCache.value)
    .map(colid => datasetsCache.value[colid])
    .map((col, i) => ({ ...col, borderColor: colors[i % colors.length] }))
})

const loading = computed(() => {
  return props.cols
    .filter(colid => store.pendingCols.value.has(colid))
    .length > 0
})

const dataPosFallback = { x: Number.MAX_VALUE, y: -Number.MAX_VALUE }
const dataPos = ref(dataPosFallback)

const root = useTemplateRef('root')
let chart = null

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
      const index = findNearest(dataset.data, dataPos.value.x)
      const step = dataset.data[index].x
      const value = dataset.data[index].y
      const formattedStep = step.toLocaleString('en-US')
      let formattedValue
      if (value === null)
        formattedValue = 'NaN'
      else if (0.01 <= Math.abs(value) && Math.abs(value) <= 10000)
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
      const distA = Math.abs(a.value - dataPos.value.y)
      const distB = Math.abs(b.value - dataPos.value.y)
      return distA - distB
    })
})

onMounted(() => {
  const canvas = root.value.$el.querySelector('canvas')
  chart = createChart(canvas)
  updateChart()
})

watch(() => datasetsList, () => updateChart(), { deep: 2 })

function updateChart() {
  if (chart === null)
    return
  const datasets = datasetsList.value.slice()
  for (const dataset of datasets) {
    let missing = []
    let prev = true
    for (const [index, point] of dataset.data.entries()) {
      if (point.y === null)
        if (prev.y !== null || index == dataset.data.length - 1)
          missing.push({x: point.x, y: 0})
      prev = point
    }
    if (missing.length)
      datasets.push({
        data: missing,
        borderWidth: 0,
        backgroundColor: dataset.borderColor,
        showLine: false,
        pointStyle: 'triangle',
        pointRadius: 10,
        pointHoverRadius: 10,
      })
  }
  chart.data.datasets = datasets
  chart.updateDebounced()
}

function createChart(canvas) {
  const chart = new Chart(canvas, {
    type: 'line',
    data: { datasets: [] },
    options: {
      animation: false,
      responsive: true,
      maintainAspectRatio: false,
      resizeDelay: 10,
      pointHoverRadius: 0,
      parsing: false,
      scales: {
        x: { type: 'linear', position: 'bottom', maxRotation: 0 },
        y: { type: 'linear', position: 'left', maxRotation: 0, },
      },
      plugins: {
        tooltip: { enabled: false },
        zoom: {
          enabled: true,
          onMove: (dataXY) => { dataPos.value = dataXY },
        },
      },
    },
  })
  chart.updateDebounced = debounce(() => chart.update('none'), 200, true)
  return chart
}

function findNearest(data, target) {
  // Because the time steps may not be sorted due to checkpoint restore and
  // this should be reflected in the graphs, we cannot use binary search.
  // However, drawing the chart needs to iterate over all data points anyways,
  // so this is likely cheap in comparison.
  if (!data.length)
    return null
  let bestIndex = 0
  let bestDist = Infinity
  for (const [index, point] of data.entries()) {
    // if (point.y === null)
    //   continue
    const dist = Math.abs(point.x - target)
    if (dist <= bestDist) {
      bestIndex = index
      bestDist = dist
    }
  }
  return bestIndex
  // return (bestDist === Infinity) ? null : bestIndex
}

function binning(data, binsize, aggFn) {
  const result = []
  // result.push({ x: data[0].x, y: null })
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
  if (vals.length && curr !== null)
    result.push({ x: prev, y: aggFn(vals) })
  // result.push({ x: data[data.length - 1].x, y: null })
  return result
}

let lastScroll = null

function wheel(e) {
  if (!legend.value.length)
    return
  const el = root.value.$el.querySelector('.legend')
  let targetX = el.scrollLeft + e.deltaX
  let targetY = el.scrollTop + e.deltaY
  targetX = Math.max(0, Math.min(targetX, el.scrollWidth - el.offsetWidth))
  targetY = Math.max(0, Math.min(targetY, el.scrollHeight - el.offsetHeight))
  const now = Date.now()
  if (lastScroll !== null && now - lastScroll > 100)
    if (targetX == el.scrollLeft && targetY == el.scrollTop)
      return
  lastScroll = now
  el.scrollTo({ left: targetX, top: targetY, behavior: 'instant' })
  e.preventDefault()
}

const debounce = (func, wait, immediate) => {
  let timeout = null
  return function() {
    let context = this, args = arguments
    const callNow = immediate && !timeout
    clearTimeout(timeout)
    timeout = setTimeout(() => {
      timeout = null
      if (!callNow)
        func.apply(context, args)
    }, wait)
    if (callNow)
      setTimeout(() => func.apply(context, args))
  }
}

</script>

<template>
  <Card :name="props.name" :loading="loading" :scrollX="false" :scrollY="false" ref="root">
    <template #default>
      <div class="content layoutCol">
        <div class="chart" @wheel="wheel">
          <canvas></canvas>
        </div>
        <div class="legend">
          <div class="entry" v-for="entry in legend" :key="entry.run">
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
