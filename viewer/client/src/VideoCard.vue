<script setup>
import { reactive, computed, watch, onMounted } from 'vue'

const props = defineProps({
  title: { type: String, default: 'VideoCard' },
  cols: { type: Array, required: true },
})

const state = reactive({
  status: '',
  cols: [],
  zoom: false,
})

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

</script>

<template>
<div class="card" :class="{ zoom: state.zoom }">
  <div class="header">
    <span class="btnZoom btn icon" @click="state.zoom = !state.zoom">fullscreen</span>
    <h2>{{ props.title }}</h2>
    <span v-if="state.status">{{ state.status }}</span>
  </div>
  <div class="content">
    <div class="col" v-for="col in state.cols">
      <h3> {{ col.run }}</h3>
      <span>Count: {{ col.steps.length }}</span><br>
      <span>Step: {{ col.steps[col.steps.length - 1] }}</span><br>
      <video controls loop v-if="col.steps.length">
        <source :src="col.url" type="video/mp4">
      </video>
    </div>
  </div>
</div>
</template>

<style scoped>
.card { max-height: 20rem; display: flex; flex-direction: column; padding: 1rem 0; background: white; border-radius: .2rem; border: 1px solid #ddd; }
.header { padding: 0 1rem 1rem; }
.content { width: 100%; overflow-y: auto; padding: 0 1rem 0; }


.col { margin: 1rem 0 0; }
.col:first-child { margin-top: 0 }

h3 { margin: 0; }
video { max-width: 100%; max-height: 15rem; }

.btnZoom { float: right; }
.zoom.card { position: absolute; max-height: inherit; top: 2rem; right: 2rem; bottom: 2rem; left: 2rem; z-index: 1; }
.zoom video { max-height: 50vh; }

</style>

