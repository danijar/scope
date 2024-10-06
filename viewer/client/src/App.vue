<script setup>

import { reactive, computed, watch, onMounted, ref, toRef } from 'vue'
import { saveStorage, loadStorage } from './storage.js'
import * as api from './api.js'
import Selector from './Selector.vue'
import Card from './Card.vue'
import CardFloat from './CardFloat.vue'
import CardVideo from './CardVideo.vue'
import CardText from './CardText.vue'

const state = reactive({
  columns: loadStorage('columns', 3),
  expids: loadStorage('expids', []),
  exps: loadStorage('exps', {}),
  runs: loadStorage('runs', {}),
  selExps: loadStorage('selExps', new Set()),
  selRuns: loadStorage('selRuns', new Set()),
  selMets: loadStorage('selMets', new Set()),
})

const loadingExps = ref(false)
const loadingRuns = ref(false)
const loadingMets = ref(false)

///////////////////////////////////////////////////////////////////////////////
// Persistence
///////////////////////////////////////////////////////////////////////////////

watch(() => state.expids, x => saveStorage('expids', x))
watch(() => state.exps, x => saveStorage('exps', x), { deep: true })
watch(() => state.runs, x => saveStorage('runs', x), { deep: true })
watch(() => state.selExps, x => saveStorage('selExps', x), { deep: true })
watch(() => state.selRuns, x => saveStorage('selRuns', x), { deep: true })
watch(() => state.selMets, x => saveStorage('selMets', x), { deep: true })
watch(() => state.columns, x => saveStorage('columns', x))

///////////////////////////////////////////////////////////////////////////////
// Fetching
///////////////////////////////////////////////////////////////////////////////

onMounted(async () => {
  if (!state.expids.length)
    api.getExpids(x => state.expids = x, loadingExps)
})

watch(() => state.selExps, () => {
  const missing = [...state.selExps].filter(expid => !(expid in state.exps))
  api.getExps(missing, x => state.exps[x.id] = x, loadingRuns)
}, { deep: true, immediate: true })

watch(() => state.selRuns, async () => {
  const missing = [...state.selRuns].filter(runid => !(runid in state.runs))
  await api.getRuns(missing, x => state.runs[x.id] = x, loadingMets)
}, { deep: true, immediate: true })

async function refresh() {
  for (const expid of Object.keys(state.exps))
    if (!state.selExps.has(expid))
      delete state.exps[expid]
  for (const runid of Object.keys(state.runs))
    if (!state.selRuns.has(runid))
      delete state.runs[runid]
  api.getExpids(x => state.expids = x, loadingExps)
  api.getExps([...state.selExps], x => state.exps[x.id] = x, loadingRuns)
  api.getRuns([...state.selRuns], x => state.runs[x.id] = x, loadingMets)
}

///////////////////////////////////////////////////////////////////////////////
// Display
///////////////////////////////////////////////////////////////////////////////

const expsOptions = computed(() => {
  return [...state.expids]
    .sort((a, b) => a.localeCompare(b))
})

const runsOptions = computed(() => {
  let options = []
  for (const expid of state.selExps)
    if (expid in state.exps)
      options = options.concat(state.exps[expid]['runs'])
  return options.sort((a, b) => a.localeCompare(b))
}, { deep: true })

const metsOptions = computed(() => {
  const options = new Set()
  for (const runid of state.selRuns)
    if (runid in state.runs)
      for (const col of state.runs[runid]['cols'])
        options.add(colToMet(col))
  return [...options].sort((a, b) => a.localeCompare(b))
}, { deep: true })

const cardsData = computed(() => {
  const cards = [...state.selMets].map(met => {
    const cols = []
    const ext = met.substr(met.lastIndexOf('.') + 1)
    for (const runid of state.selRuns)
      if (runid in state.runs)
        for (const col of state.runs[runid]['cols'])
          if (colToMet(col) === met)
            cols.push(col)
    return { name: met, ext, ext, cols: cols }
  })
  return cards

}, { deep: true })

///////////////////////////////////////////////////////////////////////////////
// Other
///////////////////////////////////////////////////////////////////////////////

function colToMet(col) {
  return col.substr(col.lastIndexOf(':') + 1)
}

function toggleLayout() {
  state.columns = state.columns % 5 + 1
}

</script>

<template>
<div class="app layoutCol">
  <div class="header layoutRow">
    <h1>Scope</h1>
    <span class="fill"></span>
    <span class="btn icon" @click="refresh">refresh</span>
    <span class="btn icon" @click="toggleLayout">settings</span>
  </div>
  <div class="content layoutRow">
    <div class="left layoutCol">
      <Selector
        :items="metsOptions" v-model="state.selMets"
        :loading="loadingMets" title="Metrics" class="selector" />
    </div>
    <div class="center">
      <div class="cards">
        <template v-for="card in cardsData" :key="card.met">
          <CardFloat
            v-if="card.ext == 'float'"
            :name="card.name" :cols="card.cols" class="card" />
          <CardText
            v-else-if="card.ext == 'txt'"
            :name="card.name" :cols="card.cols" class="card" />
          <CardVideo
            v-else-if="['mp4', 'webm'].includes(card.ext)"
            :name="card.name" :cols="card.cols" class="card" />
          <Card v-else :name="card.name" class="card">
            Unknown metric type: {{ card.ext }}</Card>
        </template>
      </div>
    </div>
    <div class="right layoutCol">
      <Selector
        :items="expsOptions" v-model="state.selExps"
        :loading="loadingExps" title="Experiments" class="selector" />
      <Selector
        :items="runsOptions" v-model="state.selRuns"
        :loading="loadingRuns" title="Runs" class="selector" />
    </div>
  </div>
</div>
</template>

<style scoped>

.app { height: 100vh; width: 100vw; }
.header { flex: 0 0 content; align-items: center; padding: 1rem; border-bottom: 2px solid #eee; }
.footer { flex: 0 0 3rem; align-items: center; padding: 1rem; border-top: 2px solid #eee; }
.content { flex: 1 1; }

.center { flex: 1 1 20rem; overflow: auto; background: #eee; }
.left, .right { flex: 0 1 20rem; max-width: 20%; }

.header h1 { font-size: 1.8rem; font-weight: 500; color: #000; padding-left: 1.3em; line-height: 1em; background: url(/logo.png) no-repeat; background-size: contain; user-select: none; }
.header .btn { margin-left: .5rem; }

.selector { flex: 1 1 0; overflow: hidden; padding: 1rem 0 0 1rem; }

.cards { --columns: v-bind(state.columns); width: 100%; display: grid; grid-template-columns: repeat(var(--columns), 1fr); gap: 1rem; overflow: auto; padding: 1rem; }
.card { height: 30rem; max-height: 80vh; border: 1px solid #ddd; }

</style>
