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
    const lastValue = col.values[col.values.length - 1]
    return {
      run: col.run,
      url: `/api/file/${lastValue}`,
      steps: col.steps,
      values: col.values,
    }
  })
})

const playing = ref(false)
const large = ref(false)
const controls = ref(true)

const root = useTemplateRef('root')

function playAll() {
  [...root.value.$el.querySelectorAll('video')].map(x => x.play())
  playing.value = true
}

function pauseAll() {
  [...root.value.$el.querySelectorAll('video')].map(x => x.pause())
  playing.value = false
}

function stopAll() {
  playing.value = false
  const elements = [...root.value.$el.querySelectorAll('video')]
  elements.map(x => {
    x.pause()
    x.currentTime = 0
  })
}

function toggleLarge() {
  large.value = !large.value
}

function toggleControls() {
  controls.value = !controls.value
}

</script>

<template>
<Card :name="props.name" :loading="loading" :scrollX="large" :scrollY="true" ref="root">

  <template #buttons>
    <span class="btn icon" @click="playAll" v-if="!playing" title="Play all">play_arrow</span>
    <span class="btn icon" @click="pauseAll" v-if="playing" title="Pause all">pause</span>
    <span class="btn icon" @click="stopAll" title="Stop all">stop</span>
    <span class="btn icon" @click="toggleControls" :title="controls ? 'Hide controls' : 'Show controls'">
      {{ controls ? 'videogame_asset_off' : 'videogame_asset' }}</span>
    <span class="btn icon" @click="toggleLarge" :title="large ? 'Small size' : 'Large size'">
      {{ large ? 'zoom_out' : 'zoom_in' }}</span>
  </template>

  <template #default>
    <div v-for="entry in entries" :key="entry.url" class="entry" :class="{ large }">
      <h3> {{ entry.run }}</h3>
      <span class="count">Count: {{ entry.steps.length }}</span>
      <span class="step">Step: {{ entry.steps[entry.steps.length - 1] }}</span><br>
      <video :controls="controls" loop v-if="entry.steps.length" tabindex="-1">
        <source :src="entry.url">
      </video>
    </div>
  </template>

</Card>
</template>

<style scoped>

.entry { margin: 1rem 0 0; }
.entry:first-child { margin-top: 0 }

h3 { margin: 0; word-break: break-all; }

video { max-width: 100%; max-height: 25rem; }

.large video { max-width: inherit; max-height: inherit; min-height: 20vh; min-width: 20vh; }

.count, .step { display: inline-block; margin: .2rem .5rem .2rem 0; }

</style>

