<script setup>

import { reactive, computed, watch, onMounted, useTemplateRef } from 'vue'
import Card from './Card.vue'

const props = defineProps({
  name: { type: String, required: true },
  cols: { type: Array, required: true },
})

const state = reactive({
  status: '',
  cols: [],
  playing: false,
})

const root = useTemplateRef('root')

onMounted(async () => {
  state.status = 'loading...'
  const requests = props.cols.map(col => fetch(`/api/col/${col}`))
  const results = await Promise.all(requests.map(async x => (await x).json()))
  state.cols = props.cols.map(function(col, i) {
    const result = results[i]
    const lastValue = result.values[result.values.length - 1]
    return {
      run: col.substr(0, col.lastIndexOf(':', col.lastIndexOf(':') - 1)),
      url: `/api/file/${lastValue}`,
      steps: result.steps,
      values: result.values,
    }
  })
  state.status = ''
})

function togglePlayAll() {
  const videos = [...root.value.$el.querySelectorAll('video')]
  if (state.playing)
    videos.map(x => x.pause())
  else
    videos.map(x => x.play())
  state.playing = !state.playing
}

function stopAll() {
  [...root.value.$el.querySelectorAll('video')].map(x => {
    x.pause()
    x.currentTime = 0
  })
}

</script>

<template>
<Card :name="props.name" :status="state.status" ref="root">

  <template #buttons>
    <span class="btn icon" @click="togglePlayAll" v-if="!state.playing" title="Play all">play_arrow</span>
    <span class="btn icon" @click="togglePlayAll" v-if="state.playing" title="Pause all">pause</span>
    <span class="btn icon" @click="stopAll" title="Stop all">stop</span>
  </template>

  <template #default>
    <div v-for="col in state.cols" class="col">
      <h3> {{ col.run }}</h3>
      <span class="count">Count: {{ col.steps.length }}</span>
      <span class="step">Step: {{ col.steps[col.steps.length - 1] }}</span><br>
      <video controls loop v-if="col.steps.length">
        <source :src="col.url" type="video/mp4">
      </video>
    </div>
  </template>

</Card>
</template>

<style scoped>

.col { margin: 1rem 0 0; }
.col:first-child { margin-top: 0 }

h3 { margin: 0; }
video { max-width: 100%; max-height: 25rem; /* 15rem */ }

.count, .step { display: inline-block; margin: .2rem .5rem .2rem 0; }

</style>

