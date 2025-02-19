<script setup>

import { reactive, computed, watch, ref, onMounted } from 'vue'
import store from './store.js'
import Card from './Card.vue'

const props = defineProps({
  name: { type: String, required: true },
  cols: { type: Array, required: true },
})

const cachedFiles = ref({})
const pendingFiles = ref(new Set())

const cols = computed(() => {
  return props.cols
    .filter(colid => colid in store.availableCols.value)
    .sort().toReversed()
    .map(colid => store.availableCols.value[colid])
})

const loading = computed(() => {
  return props.cols
    .filter(colid => store.pendingCols.value.has(colid))
    .length > 0 || pendingFiles.size > 0
})

const entries = computed(() => {
  return cols.value.map(col => {
    const index = nearestIndex(col.steps, store.options.stepsel)
    const value = col.values[index]
    return {
      run: col.run,
      file: value,
      steps: col.steps,
      values: col.values,
      selectedIndex: index,
      selectedStep: col.steps[index],
      maxStep: Math.max(...col.steps),
    }
  })
})

watch(() => entries, () => {
  const usedFiles = new Set(entries.value.map(entry => entry.file))
  Object.keys(cachedFiles.value)
    .filter(fileid => !(usedFiles.has(fileid)))
    .map(fileid => delete cachedFiles.value[fileid]);
  [...usedFiles]
    .filter(fileid => !(fileid in cachedFiles.value))
    .map(fileid => { pendingFiles.value.add(fileid); return fileid })
    .map(fileid => store.get(`/api/file/${fileid}`)
      .then(data => cachedFiles.value[data.id] = data)
      .finally(() => pendingFiles.value.delete(fileid)))
}, { deep: 2 })

function nearestIndex(steps, target) {
  if (target === null)
    return steps.length - 1
  let bestIndex = 0
  let bestDist = Infinity
  for (const [index, step] of steps.entries()) {
    const dist = Math.abs(step - target)
    if (dist <= bestDist) {
      bestIndex = index
      bestDist = dist
    }
  }
  return (bestDist === Infinity) ? null : bestIndex
}

</script>

<template>
<Card :name="props.name" :loading="loading" :scrollX="false" :scrollY="true">
  <div v-for="entry in entries" class="entry">
    <h3> {{ entry.run }}</h3>
      <span class="count">Index: {{ entry.selectedIndex }}/{{ entry.steps.length }}</span>
      <span class="step">Step: {{ entry.selectedStep }}/{{ entry.maxStep }}</span><br>
    <pre v-if="entry.file in cachedFiles" v-html="cachedFiles[entry.file].text"></pre>
    <span v-else class="icon spinner">progress_activity</span>
  </div>
</Card>
</template>

<style scoped>

.entry { margin: 1rem 0 0; }
.entry:first-child { margin-top: 0 }

h3 { margin: 0; word-break: break-all; }
pre { margin: .3rem 0 0; padding: .3rem; font-family: monospace; background: var(--bg2); color: var(--fg2); border-radius: .2rem; overflow: auto; }

.count, .step { display: inline-block; margin: .2rem .5rem .2rem 0; }

</style>

