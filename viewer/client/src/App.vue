<script setup>
import { reactive, computed, onMounted } from 'vue'
import Selector from './Selector.vue'
import VideoCard from './VideoCard.vue'

const state = reactive({
  status: 'loading...',
  exps: [],
  leafs: {},  //  {exp: leafs}
  keys: {}, // {leaf: keys}
  expsSelected: new Set(),
  leafsSelected: new Set(),
  keysSelected: new Set(),
})

const flatLeafs = computed(() => {
  let leafs = []
  for (const exp of state.expsSelected)
    leafs = leafs.concat(state.leafs[exp])
  return leafs
})

const flatKeys = computed(() => {
  let keys = []
  for (const leaf of state.leafsSelected)
    keys = keys.concat(state.keys[leaf])
  return keys
})

onMounted(async () => {
  const response = await fetch('/api/exps')
  const result = await response.json()
  state.exps = result['exps']
  state.status = ''
})

async function selectExp(exp) {
  // if (!(exp in state.leafs)) {
  state.status = 'loading...'
  const response = await fetch(`/api/leafs/${exp}`)
  const result = await response.json()
  state.leafs[exp] = result['leafs']
  state.status = ''
  // }
  state.expsSelected.add(exp);
}

function unselectExp(exp) {
  state.expsSelected.delete(exp);
}

async function selectLeaf(leaf) {
  // if (!(leaf in state.keys)) {
  state.status = 'loading...'
  const leafEncoded = leaf.replace(/\//g, ':')
  console.log(leafEncoded)
  const response = await fetch(`/api/keys/${leafEncoded}`)
  const result = await response.json()
  console.log('keys', result)
  state.keys[leaf] = result['keys']
  state.status = ''
  // }
  state.leafsSelected.add(leaf);
}

function unselectLeaf(leaf) {
  state.leafsSelected.delete(leaf);
}


function selectKey(key) {
  // state.leafsSelected.add(leaf);
}

function unselectKey(kel) {
  // state.leafsSelected.delete(leaf);
}

</script>

<template>
<div class="left">
  <Selector :items="flatKeys" @select="selectKey" @unselect="unselectKey" class="selector" title="Metrics" />
</div>
<div class="center">

  <div v-for="key in state.keysSelected">
    <VideoCard path="key" />
  </div>

  <span>{{ state.status }}</span>
</div>
<div class="right">
  <Selector :items="state.exps" @select="selectExp" @unselect="unselectExp" class="selector" title="Experiments" />
  <Selector :items="flatLeafs" @select="selectLeaf" @unselect="unselectLeaf" class="selector" title="Leafs" />
</div>
</template>

<style scoped>
.center { flex: 1 1 20rem; overflow: auto; gap: 1em; background: #eee; padding: 1rem; }
.left, .right { flex: 0 1 20rem; overflow: hidden; display: flex; flex-direction: column; padding: 1rem 0 0 1rem; }

.selector { flex: 1 1 0; overflow: hidden; } /* padding: .5rem 1rem; } */
.selector:not(:first-child) { margin-top: 1.5rem; }

</style>
