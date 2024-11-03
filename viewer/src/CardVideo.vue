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

const playing = ref(false)
const large = ref(false)
const controls = ref(true)
const seeking = ref(new Set())

const root = useTemplateRef('root')

function getVideos() {
  return [...root.value.$el.querySelectorAll('video')]
}

function playAll() {
  getVideos().map(video => video.play())
  playing.value = true
}

function pauseAll() {
  getVideos().map(video => video.pause())
  playing.value = false
}

function stopAll() {
  playing.value = false
  getVideos().map(video => {
    video.pause()
    seeking.value.add(video.getAttribute('url'))
    video.currentTime = 0
  })
}

function toggleLarge() {
  large.value = !large.value
}

function toggleControls() {
  controls.value = !controls.value
}

let lastSeek = 0
let lastSync = 0
function seekStart(e) {
  const now = Date.now()
  // Skip if this is not a double click.
  if (!lastSeek || now - lastSeek > 200) {
    lastSeek = now
    return
  }
  // Ignore seek events on videos without loaded metadata.
  if (!e.target.duration)
    return
  // Ignore seek events of videos we triggered by syncing.
  if (lastSync && now - lastSync < 200)
    return
  lastSeek = now
  lastSync = now
  seeking.value.add(e.target.getAttribute('url'))
  const time = e.target.currentTime
  setTimeout(() => {
    getVideos()
      .filter(video => video !== e.target)
      .filter(video => video.paused)
      .filter(video => video.duration)
      .forEach(video => {
        seeking.value.add(video.getAttribute('url'))
        video.currentTime = Math.min(time, video.duration)
      })
  }, 10)
}

function seekDone(e) {
  seeking.value.delete(e.target.getAttribute('url'))
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
      <span class="count">Index: {{ entry.selectedIndex }}/{{ entry.steps.length }}</span>
      <span class="step">Step: {{ entry.selectedStep }}/{{ entry.maxStep }}</span><br>
      <div class="player">
        <video
          :controls="controls" loop tabindex="-1" :url="entry.url"
          v-if="entry.steps.length" @seeking="seekStart" @seeked="seekDone">
          <source :src="entry.url">
        </video>
        <Transition>
          <span v-if="seeking.has(entry.url)" class="icon spinner">progress_activity</span>
        </Transition>
      </div>
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

.player { position: relative; display: inline-flex; background: rgba(0,0,0,.1); }
.spinner { display: block; position: absolute; top: 50%; left: 50%; margin: -.5em; font-size: 3rem; }

.count, .step { display: inline-block; margin: .2rem .5rem .2rem 0; }

</style>

