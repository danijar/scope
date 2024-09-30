<script setup>
import { reactive, computed, onMounted } from 'vue'

const props = defineProps({
  cols: { type: Array, required: true },
})

const state = reactive({
  status: '',
  cols: [],
})

const title = computed(() => {
  return props.cols[0].substr(props.cols[0].lastIndexOf(':') + 1)
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
<div class="card">
  <div class="header">
    <h2>{{ title }}</h2>
    <span>Status: {{ state.status }}</span><br>
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
.card { display: flex; flex-direction: column; padding: 1rem; background: white; }
.header {}
.content { width: 100%; overflow-y: auto; }

h3 {  }
video { max-width: 100%; max-height: 10rem; }
</style>

