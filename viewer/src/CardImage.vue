<script setup>

import { reactive, computed, watch, ref, onMounted, useTemplateRef } from 'vue'
import store from './store.js'
import Card from './Card.vue'

const props = defineProps({
  name: { type: String, required: true },
  cols: { type: Array, required: true },
})

const cols = computed(() => {
  return props.cols
    .filter(colid => colid in store.availableCols.value)
    .sort().toReversed()
    .map(colid => store.availableCols.value[colid])
})

const loading = computed(() => {
  return props.cols
    .filter(colid => store.pendingCols.value.has(colid))
    .length > 0
})

const entries = computed(() => {
  return cols.value.map(col => {
    const index = nearestIndex(col.steps, store.options.stepsel)
    const lastValue = col.values[index]
    return {
      run: col.run,
      url: `/api/file/${lastValue}`,
      steps: col.steps,
      values: col.values,
      selectedIndex: index,
      selectedStep: col.steps[index],
      maxStep: Math.max(...col.steps),
    }
  })
})

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

const large = ref(false)

const root = useTemplateRef('root')

function toggleLarge() {
  large.value = !large.value
}

</script>

<template>
<Card :name="props.name" :loading="loading" :scrollX="large" :scrollY="true" ref="root">

  <template #buttons>
    <span class="btn icon" @click="toggleLarge" :title="large ? 'Small size' : 'Large size'">
      {{ large ? 'zoom_out' : 'zoom_in' }}</span>
  </template>

  <template #default>
    <div v-for="entry in entries" :key="entry.url" class="entry" :class="{ large }">
      <h3> {{ entry.run }}</h3>
      <span class="count">Index: {{ entry.selectedIndex }}/{{ entry.steps.length }}</span>
      <span class="step">Step: {{ entry.selectedStep }}/{{ entry.maxStep }}</span><br>
      <div class="box">
        <img :src="entry.url" v-if="entry.steps.length" tabindex="-1" />
      </div>
    </div>
  </template>

</Card>
</template>

<style scoped>

.entry { margin: 1rem 0 0; }
.entry:first-child { margin-top: 0 }

h3 { margin: 0; word-break: break-all; }

img { max-width: 100%; max-height: 25rem; }
.large img { max-width: inherit; max-height: inherit; min-height: 20vh; min-width: 20vh; }

.box { position: relative; display: inline-flex; background: rgba(0,0,0,.1); }

.count, .step { display: inline-block; margin: .2rem .5rem .2rem 0; }

</style>


