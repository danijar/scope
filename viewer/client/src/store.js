import { reactive, computed, watch, ref } from 'vue'
import { saveStorage, loadStorage } from './storage.js'

/*****************************************************************************
 * Helpers
 *****************************************************************************/

async function get(url, delay = 0) {
  if (url.indexOf('[') >= 0)
    throw new Error(`Invalid URL: ${url}`)
  console.log(url)
  const result = await (await fetch(url)).json()
  // await new Promise(x => setTimeout(x, 500))  // TODO
  if (delay > 0)
    await new Promise(x => setTimeout(x, delay))  // TODO
  return result
}

function colToMet(col) {
  return col.substr(col.lastIndexOf(':') + 1)
}

function colToRun(col) {
  // Remove metric name and scope folder.
  return col.split(':').slice(0, -2).join(':')
}

/*****************************************************************************
 * State
 *****************************************************************************/

const pendingEids = ref(false)
const pendingExps = ref(new Set())
const pendingRuns = ref(new Set())
const pendingCols = ref(new Set())

const cachedEids = ref(loadStorage('cachedEids', []))
const cachedExps = ref(loadStorage('cachedExps', {}))
const cachedRuns = ref(loadStorage('cachedRuns', {}))
const cachedCols = ref({})

const selExps = ref(loadStorage('selExps', new Set()))
const selRuns = ref(loadStorage('selRuns', new Set()))
const selMets = ref(loadStorage('selMets', new Set()))

/*****************************************************************************
 * Persistence
 *****************************************************************************/

watch(() => cachedEids, x => saveStorage('cachedEids', x.value), { deep: 2 })
watch(() => cachedExps, x => saveStorage('cachedExps', x.value), { deep: 2 })
watch(() => cachedRuns, x => saveStorage('cachedRuns', x.value), { deep: 2 })
watch(() => selExps, x => saveStorage('selExps', x.value), { deep: 2 })
watch(() => selRuns, x => saveStorage('selRuns', x.value), { deep: 2 })
watch(() => selMets, x => saveStorage('selMets', x.value), { deep: 2 })

/*****************************************************************************
 * Computed
 *****************************************************************************/

const availableExps = computed(() => {
  return cachedEids.value.sort()
})

const availableRuns = computed(() => {
  return [...selExps.value]
    .filter(expid => expid in cachedExps.value)
    .flatMap(expid => cachedExps.value[expid]['runs'])
    .sort()
})

const availableMets = computed(() => {
  const results = [...selRuns.value]
    .filter(runid => runid in cachedRuns.value)
    .flatMap(runid => cachedRuns.value[runid]['cols'])
    .map(colid => colToMet(colid))
  return [...new Set(results)].sort()
})

const availableCards = computed(() => {
  return [...selMets.value]
    .sort()
    .map(met => {
      const ext = met.substr(met.lastIndexOf('.') + 1)
      const cols = [...selRuns.value]
        .filter(runid => runid in cachedRuns.value)
        .flatMap(runid => cachedRuns.value[runid]['cols'])
        .filter(colid => met === colToMet(colid))
      return { name: met, ext: ext, cols: cols }
    })
})

const availableCols = computed(() => {
  return cachedCols.value
})

/*****************************************************************************
 * Fetching
 *****************************************************************************/

async function updateEids(force = false) {
  if (cachedEids.value.length > 0 && !force)
    return
  pendingEids.value = true
  get('/api/exps')
    .then(data => cachedEids.value = data['exps'])
    .finally(() => pendingEids.value = false)
}

async function updateExps(force = false) {
  [...selExps.value]
    .filter(expid => !(expid in pendingExps.value))
    .filter(expid => !(expid in cachedExps.value) || force)
    .map(expid => { pendingExps.value.add(expid); return expid })
    .map(expid => get(`/api/exp/${expid}`)
      .then(data => cachedExps.value[data.id] = data)
      .finally(() => pendingExps.value.delete(expid)))
}

async function updateRuns(force = false) {
  [...selRuns.value]
    .filter(runid => !(runid in pendingRuns.value))
    .filter(runid => !(runid in cachedRuns.value) || force)
    .map(runid => { pendingRuns.value.add(runid); return runid })
    .map(runid => get(`/api/run/${runid}`)
      .then(data => cachedRuns.value[data.id] = data)
      .finally(() => pendingRuns.value.delete(runid)))
}

async function updateCols(force = false) {
  Object.keys(cachedCols.value)
    .filter(colid => (
      !selMets.value.has(colToMet(colid)) ||
      !selRuns.value.has(colToRun(colid))))
    .map(colid => delete cachedCols.value[colid])
  availableCards.value
    .flatMap(card => card['cols'])
    .filter(colid => !pendingCols.value.has(colid))
    .filter(colid => !(colid in cachedCols.value) || force)
    .map(colid => { pendingCols.value.add(colid); return colid })
    .map(colid => get(`/api/col/${colid}`)
      .then(data => cachedCols.value[data.id] = data)
      .finally(() => pendingCols.value.delete(colid)))
}

async function refresh() {
  Object.keys(cachedExps.value)
    .filter(expid => !selExps.value.has(expid))
    .map(expid => delete cachedExps.value[expid])
  Object.keys(cachedRuns.value)
    .filter(runid => !selRuns.value.has(runid))
    .map(runid => delete cachedRuns.value[runid])
  updateCols(true)
  updateExps(true)
  updateRuns(true)
  updateEids(true)
}

/*****************************************************************************
 * Automatic fetching
 *****************************************************************************/

updateEids()
setTimeout(() => {
  watch(() => selExps, () => updateExps(false), { deep: 2 })
  watch(() => selRuns, () => updateRuns(false), { deep: 2 })
  watch(() => [selRuns, selMets], () => updateCols(false), { deep: 3, immediate: true })
}, 200)

/*****************************************************************************
 * Other
 *****************************************************************************/

const options = reactive(loadStorage('options', {
  binsize: null,
  stepsel: null,
}))

watch(() => options, x => saveStorage('options', x), { deep: true })

/*****************************************************************************
 * Export
 *****************************************************************************/

const store = {

  pendingEids,
  pendingExps,
  pendingRuns,
  pendingCols,

  get,
  refresh,

  // cachedEids,
  // cachedExps,
  // cachedRuns,
  // cachedCols,

  selExps,
  selRuns,
  selMets,

  // updateEids,
  // updateExps,
  // updateRuns,

  availableExps,
  availableRuns,
  availableMets,
  availableCards,
  availableCols,

  options,

}

export default store
