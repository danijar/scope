<script setup>

import { reactive, computed, watch, onMounted } from 'vue'
import Selector from './Selector.vue'
import VideoCard from './VideoCard.vue'
import { saveStorage, loadStorage } from './storage.js'

const persist = ['expids', 'exps', 'runs', 'cols', 'selExps', 'selRuns', 'selCols']

const state = reactive({
  status: '',

  // expids: [],
  // exps: {}
  // runs: {},
  // cols: {},
  // selExps: new Set(),
  // selRuns: new Set(),
  // selCols: new Set(),

  expids: loadStorage('expids', []),
  exps: loadStorage('exps', {}),
  runs: loadStorage('runs', {}),
  cols: loadStorage('cols', {}),
  selExps: loadStorage('selExps', new Set()),
  selRuns: loadStorage('selRuns', new Set()),
  selCols: loadStorage('selCols', new Set()),

  // selColGroups: [],  # TODO
})

watch(state.expids, x => saveStorage('expids', x))
watch(state.exps, x => saveStorage('exps', x))
watch(state.runs, x => saveStorage('runs', x))
watch(state.cols, x => saveStorage('cols', x))
watch(state.selExps, x => saveStorage('selExps', x))
watch(state.selRuns, x => saveStorage('selRuns', x))
watch(state.selCols, x => saveStorage('selCols', x))

const expsOptions = computed(() => {
  return [...state.expids].sort()
})

const runsOptions = computed(() => {
  let options = []
  for (const exp of state.selExps)
    if (exp in state.exps)
      options = options.concat(state.exps[exp]['runs'])
  return options
})

const colsOptions = computed(() => {
  let options = []
  for (const run of state.selRuns)
    if (run in state.runs)
      options = options.concat(state.runs[run]['cols'])
  return options
})

onMounted(async () => {
  if (state.expids.length == 0) {
    state.status = 'loading /exps...'
    state.expids = (await (await fetch('/api/exps')).json())['exps']
    state.status = ''
  }
})

async function selectExp(expid) {
  state.status = `loading exp/${expid}...`
  state.exps[expid] = await (await fetch(`/api/exp/${expid}`)).json()
  state.status = ''
}

async function selectRun(runid) {
  state.status = `loading run/${runid}...`
  state.runs[runid] = await (await fetch(`/api/run/${runid}`)).json()
  state.status = ''
}

</script>

<template>
<div class="left">
  <Selector :items="colsOptions" v-model="state.selCols" class="selector" title="Metrics" />
</div>
<div class="center">
  <VideoCard v-for="col in state.selCols" :cols="[col, col]" class="card" />
  <span>{{ state.status }}</span>
</div>
<div class="right">
  <Selector :items="expsOptions" v-model="state.selExps" class="selector" @select="selectExp" title="Experiments" />
  <Selector :items="runsOptions" v-model="state.selRuns" class="selector" @select="selectRun" title="Runs" />
</div>
</template>

<style scoped>
.center { flex: 1 1 20rem; overflow: auto; gap: 1em; background: #eee; padding: 1rem; display: flex; flex-wrap: wrap; align-content: flex-start; justify-content: flex-start; }
.left, .right { flex: 0 1 20rem; overflow: hidden; display: flex; flex-direction: column; padding: 1rem 0 0 1rem; }

.selector { flex: 1 1 0; overflow: hidden; } /* padding: .5rem 1rem; } */
.selector:not(:first-child) { margin-top: 1.5rem; }

.card { flex: 1 1 20rem; max-height: 20rem; }

</style>
