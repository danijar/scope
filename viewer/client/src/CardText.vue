<script setup>

import { reactive, computed, watch, onMounted } from 'vue'
import Card from './Card.vue'
import * as api from './api.js'

const props = defineProps({
  name: { type: String, required: true },
  cols: { type: Array, required: true },
})

const state = reactive({
  status: '',
  cols: {},
})

// TODO: Figure out how to abstract this logic out into the API file.
const inflight = new Set()

function refresh() {
  api.getCols(props.cols, storeCol)
}

watch(() => props.cols, () => {
  for (const colid of Object.keys(state.cols))
    if (!props.cols.includes(colid))
      delete state.cols[colid]
  const missing = [...props.cols]
    .filter(x => !(x in state.cols))
    .filter(x => !inflight.has(x))
  missing.forEach(x => inflight.add(x))
  api.getCols(missing, storeCol)
}, { immediate: true })

watch(() => state.cols, () => {
  for (const col of Object.values(state.cols)) {
    if (col === null) continue
    if (col.fileidSelected !== col.fileidFetching) {
      col.fileidFetching = col.fileidSelected
      fetch(`/api/file/${col.fileidSelected}`).then(async response => {
        col.text = (await ((await response).json()))['text'].replace(/\n/g, '<br>')
      })
    }
  }
}, { deep: true })

function storeCol(col) {
  const lastValue = col.values[col.values.length - 1]
  col.text = 'loading...'
  col.fileidSelected = lastValue
  col.fileidFetching = null
  if (props.cols.includes(col.id))
    state.cols[col.id] = col
  inflight.delete(col.id)
}

const displayCols = computed(() => {
  return Object.values(state.cols)
    .filter(x => x !== null)
    .sort((a, b) => a.run.localeCompare(b.run))
})

</script>

<template>
<Card :name="props.name" :status="state.status">
  <div v-for="col in displayCols" class="col">
    <h3> {{ col.run }}</h3>
    <span class="count">Count: {{ col.steps.length }}</span>
    <span class="step">Step: {{ col.steps[col.steps.length - 1] }}</span><br>
    <pre v-html="col.text"></pre>
  </div>
</Card>
</template>

<style scoped>

.col { margin: 1rem 0 0; }
.col:first-child { margin-top: 0 }

h3 { margin: 0; }
pre { margin: .3rem 0 0; padding: .3rem; font-family: monospace; background: #eee; color: #444; border-radius: .2rem; overflow: auto; }

.count, .step { display: inline-block; margin: .2rem .5rem .2rem 0; }

</style>

