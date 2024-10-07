import { reactive, computed, watch, ref } from 'vue'
import { saveStorage, loadStorage } from './storage.js'

/*****************************************************************************
 * Helpers
 *****************************************************************************/

async function get(url) {
  if (url.indexOf('[') >= 0)
    throw new Error(`Invalid URL: ${url}`)
  console.log(url)
  const result = await (await fetch(url)).json()
  // await new Promise(x => setTimeout(x, 500))  // TODO
  return result
}

function colToMet(col) {
  return col.substr(col.lastIndexOf(':') + 1)
}

/*****************************************************************************
 * State
 *****************************************************************************/

const pendingEids = ref(false)
const pendingExps = ref(new Set())
const pendingRuns = ref(new Set())

const cachedEids = ref(loadStorage('cachedEids', []))
const cachedExps = ref(loadStorage('cachedExps', {}))
const cachedRuns = ref(loadStorage('cachedRuns', {}))

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

async function refresh() {
  // TODO: Trigger requests to refresh cols first, so that time series that
  // will be added later don't refresh again right away.
  Object.keys(cachedExps.value)
    .filter(expid => !selExps.value.has(expid))
    .map(expid => delete cachedExps.value[expid])
  Object.keys(cachedRuns.value)
    .filter(runid => !selRuns.value.has(runid))
    .map(runid => delete cachedRuns.value[runid])
  updateEids(true)
  updateRuns(true)
  updateExps(true)
}

/*****************************************************************************
 * Automatic fetching
 *****************************************************************************/

updateEids()
watch(() => selExps, () => updateExps(false), { deep: 2 })
watch(() => selRuns, () => updateRuns(false), { deep: 2 })

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

/*****************************************************************************
 * Export
 *****************************************************************************/

const store = {

  pendingEids,
  pendingExps,
  pendingRuns,

  refresh,

  // cachedEids,
   cachedExps,
  // cachedRuns,

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

}

export default store
