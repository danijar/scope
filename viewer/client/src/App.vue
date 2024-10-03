<script setup>

import { reactive, computed, watch, onMounted } from 'vue'
import { saveStorage, loadStorage } from './storage.js'
import Selector from './Selector.vue'
import Card from './Card.vue'
import CardFloat from './CardFloat.vue'
import CardVideo from './CardVideo.vue'
import CardText from './CardText.vue'

const persist = ['expids', 'exps', 'runs', 'cols', 'selExps', 'selRuns', 'selMets']

const state = reactive({
  status: '',
  // columns: 3,
  // columns: 2,

  // expids: [],
  // exps: {}
  // runs: {},
  // cols: {},
  // selExps: new Set(),
  // selRuns: new Set(),
  // selMets: new Set(),

  columns: loadStorage('columns', 3),
  expids: loadStorage('expids', []),
  exps: loadStorage('exps', {}),
  runs: loadStorage('runs', {}),
  cols: loadStorage('cols', {}),
  selExps: loadStorage('selExps', new Set()),
  selRuns: loadStorage('selRuns', new Set()),
  selMets: loadStorage('selMets', new Set()),
})

watch(state.expids, x => saveStorage('expids', x))
watch(state.exps, x => saveStorage('exps', x))
watch(state.runs, x => saveStorage('runs', x))
watch(state.cols, x => saveStorage('cols', x))
watch(state.selExps, x => saveStorage('selExps', x))
watch(state.selRuns, x => saveStorage('selRuns', x))
watch(state.selMets, x => saveStorage('selMets', x))
watch(state.columns, x => saveStorage('columns', state.columns))

function colToMet(col) {
  return col.substr(col.lastIndexOf(':') + 1)
}

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

const metsOptions = computed(() => {
  const options = new Set()
  for (const run of state.selRuns)
    if (run in state.runs)
      for (const col of state.runs[run]['cols'])
        options.add(colToMet(col))
  return [...options].sort()
})

const selGroups = computed(() => {
  const groups = []
  for (const met of state.selMets) {
    const cols = []
    const ext = met.substr(met.lastIndexOf('.') + 1)
    for (const run of state.selRuns)
      if (run in state.runs)
        for (const col of state.runs[run]['cols'])
          if (colToMet(col) === met)
            cols.push(col)
    groups.push({ name: met, ext, ext, cols: cols })
  }
  return groups
})

onMounted(async () => {
  if (state.expids.length == 0) {
    state.status = 'loading /exps...'
    state.expids = (await (await fetch('/api/exps')).json())['exps']
    saveStorage('expids', state.expids)  // TODO: fix watcher
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

function toggleLayout() {
  state.columns = state.columns % 5 + 1
  saveStorage('columns', state.columns)
}

</script>

<template>
<div class="app layoutCol">
  <div class="header layoutRow">
    <h1>Scope</h1>
    <span class="fill"></span>
    <span class="btn icon">refresh</span>
    <span class="btn icon" @click="toggleLayout">settings</span>
  </div>
  <div class="content layoutRow">
    <div class="left layoutCol">
      <Selector
        :items="metsOptions" v-model="state.selMets"
        title="Metrics" class="selector" />
    </div>
    <div class="center">
      <div class="cards">
        <span v-if="state.status">{{ state.status }}</span>
        <template v-for="group in selGroups" :key="group.met">
          <CardFloat v-if="group.ext == 'float'"    :name="group.name" :cols="group.cols" class="card" />
          <CardVideo v-else-if="group.ext == 'mp4'" :name="group.name" :cols="group.cols" class="card" />
          <CardText  v-else-if="group.ext == 'txt'" :name="group.name" :cols="group.cols" class="card" />
          <Card v-else :name="group.name" class="card">Unknown metric type: {{ group.ext }}</Card>
        </template>
      </div>
    </div>
    <div class="right layoutCol">
      <Selector
        :items="expsOptions" v-model="state.selExps" @select="selectExp"
        title="Experiments" class="selector" />
      <Selector
        :items="runsOptions" v-model="state.selRuns" @select="selectRun"
        title="Runs" class="selector" />
    </div>
  </div>
</div>
</template>

<style scoped>

.app { height: 100vh; width: 100vw; }
.header { flex: 0 0 content; align-items: center; padding: 1rem; border-bottom: 2px solid #eee; }
.content { flex: 1 1; }

.center { flex: 1 1 20rem; overflow: auto; background: #eee; }
.left, .right { flex: 0 1 20rem; max-width: 25%; }

.header h1 { font-size: 1.8rem; font-weight: 500; color: #000; padding-left: 1.3em; line-height: 1em; background: url(/logo.png) no-repeat; background-size: contain; user-select: none; }

.selector { flex: 1 1 0; overflow: hidden; padding: 1rem 0 0 1rem; }

.cards { --columns: v-bind(state.columns); width: 100%; display: grid; grid-template-columns: repeat(var(--columns), 1fr); gap: 1rem; overflow: auto; padding: 1rem; }
.card { flex: 1 1 20rem; aspect-ratio: 4 / 3; border: 1px solid #ddd; }

</style>
