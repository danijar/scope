<script setup>
import { reactive, computed, onMounted } from 'vue'
import Selector from './Selector.vue'

const state = reactive({
  status: 'loading...',
  exps: [],
  expsSelected: new Set(),
  expsRuns: {},
})

const flatRuns = computed(() => {
  let runs = []
  for (const exp of state.expsSelected) {
    runs = runs.concat(state.expsRuns[exp])
  }
  console.log('flat runs', runs)
  return runs
})

onMounted(async () => {
  const response = await fetch('/api/exps')
  const result = await response.json()
  state.exps = result['exps']
  state.status = ''
})

async function selectExp(exp) {
  console.log('select', exp)
  if (!(exp in state.expsRuns)) {
    state.status = 'loading...'
    const response = await fetch(`/api/exp/${exp}`)
    const result = await response.json()
    console.log(result);
    state.expsRuns[exp] = result['runs']
    state.status = ''
  }
  state.expsSelected.add(exp);
}

function unselectExp(exp) {
  state.expsSelected.delete(exp);
  console.log('unselect', exp)
}

</script>

<template>
<div class="left">
</div>
<div class="center">
  <span>{{ state.status }}</span>
</div>
<div class="right">
  <Selector :items="state.exps" @select="selectExp" @unselect="unselectExp" class="selector" title="Experiments" />
  <Selector :items="flatRuns" class="selector" title="Runs" />
</div>
</template>

<style scoped>
.center { flex: 1 1 20rem; overflow: auto; }
.left { flex: 0 1 20rem; overflow: hidden; display: flex; flex-direction: column; }
.right { flex: 0 1 20rem; overflow: hidden; display: flex; flex-direction: column; }

.right > .selector { flex: 1 1 50%; background: #eee; }

.selector { overflow: hidden; padding: .5rem 1rem; }

</style>
