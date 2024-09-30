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
      text: 'loading...',
    }
  })
  const requests2 = state.cols.map(col => fetch(col.url))
  const results2 = await Promise.all(requests2.map(async x => (await x).json()))
  state.cols.map(function(col, i) {
    console.log(results2[i]['text'])
    col.text = results2[i]['text'].replace(/\n/g, '<br>')
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
    <p v-html="col.text"></p>
  </div>
</Card>
</template>

<style scoped>

.col { margin: 1rem 0 0; }
.col:first-child { margin-top: 0 }

h3 { margin: 0; }
p { margin: .3rem 0 0; padding: .3rem; font-family: monospace; background: #eee; color: #444; border-radius: .2rem; overflow: auto; }

</style>

