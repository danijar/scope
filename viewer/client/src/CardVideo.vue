<script setup>

import { reactive, computed, watch, onMounted } from 'vue'
import Card from './Card.vue'

const props = defineProps({
  name: { type: String, required: true },
  cols: { type: Array, required: true },
})

const state = reactive({
  status: '',
  cols: [],
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
<Card :name="props.name" :status="state.status">
  <div v-for="col in state.cols" class="col">
    <h3> {{ col.run }}</h3>
    <span>Count: {{ col.steps.length }}</span><br>
    <span>Step: {{ col.steps[col.steps.length - 1] }}</span><br>
    <video controls loop v-if="col.steps.length">
      <source :src="col.url" type="video/mp4">
    </video>
  </div>
</Card>
</template>

<style scoped>

.col { margin: 1rem 0 0; }
.col:first-child { margin-top: 0 }

h3 { margin: 0; }
video { max-width: 100%; max-height: 50%; /* 15rem */ }

</style>

