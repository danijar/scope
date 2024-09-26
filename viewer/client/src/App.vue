<script setup>
import { reactive, onMounted } from 'vue'
import Selector from './Selector.vue'

const state = reactive({
  status: 'loading...',
  exps: [],
})

onMounted(async () => {
  let response = await fetch('/api/exps')
  let exps = await response.json()
  state.exps = exps['exps']
  state.status = 'done!'
})

</script>

<template>

  <span>{{ state.status }}</span>

  <h1>Exps</h1>
  <Selector :items="state.exps" />

</template>

<style scoped>
</style>
