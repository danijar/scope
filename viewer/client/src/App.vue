<script setup>

import { reactive, computed, watch, onMounted, ref } from 'vue'
import { saveStorage, loadStorage } from './storage.js'
import Selector from './Selector.vue'
import Card from './Card.vue'
import CardFloat from './CardFloat.vue'
import CardVideo from './CardVideo.vue'
import CardText from './CardText.vue'

const persist = ['expids', 'exps', 'runs', 'cols', 'selExps', 'selRuns', 'selMets']

const state = reactive({
  status: '',
  columns: loadStorage('columns', [3]),
  expids: loadStorage('expids', []),
  exps: loadStorage('exps', {}),
  runs: loadStorage('runs', {}),
  cols: loadStorage('cols', {}),
  selExps: loadStorage('selExps', new Set()),
  selRuns: loadStorage('selRuns', new Set()),
  selMets: loadStorage('selMets', new Set()),
  loadingExps: false,
  loadingRuns: false,
  loadingMets: false,
})

watch(() => state.expids, x => saveStorage('expids', x))
watch(() => state.exps, x => saveStorage('exps', x))
watch(() => state.runs, x => saveStorage('runs', x))
watch(() => state.cols, x => saveStorage('cols', x))
watch(() => state.selExps, x => saveStorage('selExps', x))
watch(() => state.selRuns, x => saveStorage('selRuns', x))
watch(() => state.selMets, x => saveStorage('selMets', x))
watch(() => state.columns, x => saveStorage('columns', x))

function colToMet(col) {
  return col.substr(col.lastIndexOf(':') + 1)
}

const expsOptions = computed(() => {
  return [...state.expids].sort()
})

const runsOptions = computed(() => {
  let options = []
  for (const expid of state.selExps)
    if (expid in state.exps)
      options = options.concat(state.exps[expid]['runs'])
  return options
})

const metsOptions = computed(() => {
  const options = new Set()
  for (const runid of state.selRuns)
    if (runid in state.runs)
      for (const col of state.runs[runid]['cols'])
        options.add(colToMet(col))
  return [...options].sort()
})

const selGroups = computed(() => {
  const groups = []
  for (const met of state.selMets) {
    // TODO: Turn cols into a reactive container so that cards update when
    // the run selection changes.
    const cols = []
    const ext = met.substr(met.lastIndexOf('.') + 1)
    for (const runid of state.selRuns)
      if (runid in state.runs)
        for (const col of state.runs[runid]['cols'])
          if (colToMet(col) === met)
            cols.push(col)
    groups.push({ name: met, ext, ext, cols: cols })
  }
  return groups
})

onMounted(async () => {
  loadExps()
})

async function loadExps() {
  if (state.exps.length)
    return
  state.loadingExps = true
  state.expids = (await (await fetch('/api/exps')).json())['exps']
  state.loadingExps = false
}

async function loadExp(expid) {
  if (expid in state.exps)
    return
  state.loadingRuns = true
  state.exps[expid] = await (await fetch(`/api/exp/${expid}`)).json()
  state.loadingRuns = false
}

async function loadRun(runid) {
  if (runid in state.runs)
    return
  state.loadingMets = true
  state.runs[runid] = await (await fetch(`/api/run/${runid}`)).json()
  state.loadingMets = false
}

async function refreshAll() {
  state.loadingExps = true
  state.loadingRuns = true
  state.loadingMets = true

  state.expids = (await (await fetch('/api/exps')).json())['exps']
  const expsOptionsSet = new Set(expsOptions.values)
  for (const selected in state.selExps)
    if (!expsOptionsSet.has(selected))
      state.selExps.remove(selected)

  state.exps = Object.fromEntries(await Promise.all(
    [...state.selExps].map(async expid => (
      [expid, await (await fetch(`/api/exp/${expid}`)).json()]))))
  const runsOptionsSet = new Set(runsOptions.value)
  for (const selected in state.selRuns)
    if (!runsOptionsSet.has(selected))
      state.selRuns.remove(selected)

  state.runs = Object.fromEntries(await Promise.all(
    [...state.selRuns].map(async runid => (
      [runid, await (await fetch(`/api/run/${runid}`)).json()]))))
  const metsOptionsSet = new Set(metsOptions.value)
  for (const selected in state.selMets)
    if (!metsOptionsSet.has(selected))
      state.selMets.remove(selected)

  state.loadingExps = false
  state.loadingRuns = false
  state.loadingMets = false

}

function toggleLayout() {
  state.columns[0] = state.columns[0] % 5 + 1
}

</script>

<template>
<div class="app layoutCol">
  <div class="header layoutRow">
    <h1>Scope</h1>
    <span class="fill"></span>
    <span class="btn icon" @click="refreshAll">refresh</span>
    <span class="btn icon" @click="toggleLayout">settings</span>
  </div>
  <div class="content layoutRow">
    <div class="left layoutCol">
      <Selector
        :items="metsOptions" v-model="state.selMets"
        :loading="state.loadingMets" title="Metrics" class="selector" />
    </div>
    <div class="center">
      <div class="cards">
        <template v-for="group in selGroups" :key="group.met">
          <CardFloat
            v-if="group.ext == 'float'"
            :name="group.name" :cols="group.cols" class="card" />
          <CardText
            v-else-if="group.ext == 'txt'"
            :name="group.name" :cols="group.cols" class="card" />
          <CardVideo
            v-else-if="['mp4', 'webm'].includes(group.ext)"
            :name="group.name" :cols="group.cols" class="card" />
          <Card v-else :name="group.name" class="card">Unknown metric type: {{ group.ext }}</Card>
        </template>
      </div>
    </div>
    <div class="right layoutCol">
      <Selector
        :items="expsOptions" v-model="state.selExps" @select="loadExp"
        :loading="state.loadingExps" title="Experiments" class="selector" />
      <Selector
        :items="runsOptions" v-model="state.selRuns" @select="loadRun"
        :loading="state.loadingRuns" title="Runs" class="selector" />
    </div>
  </div>
  <!-- <div class="footer layoutRow"> -->
  <!--   <span class="status">{{ state.status }}</span> -->
  <!-- </div> -->
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

.cards { --columns: v-bind(state.columns[0]); width: 100%; display: grid; grid-template-columns: repeat(var(--columns), 1fr); gap: 1rem; overflow: auto; padding: 1rem; }
.card { height: 30rem; max-height: 80vh; border: 1px solid #ddd; }

.status { color: #999; }

</style>
