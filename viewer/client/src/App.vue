<script setup>
import { reactive, onMounted } from 'vue'
import HelloWorld from './HelloWorld.vue'

const state = reactive({
  status: 'loading...',
  exps: [],
  selected: [],
})

onMounted(async () => {
  console.log('hi')
  let response = await fetch('/api/exps')
  console.log(response)
  // console.log(await response.text())
  let exps = await response.json()
  console.log(exps)
  state.exps = exps['exps']
  state.status = 'done!'
})

function selectExp(exp) {
  state.selected.push(exp)
}

function unselectExp(exp) {
  state.selected.splice(state.selected.indexOf(exp), 1)
}

</script>

<template>
  <!--HelloWorld msg="You did it!" /-->
  <span>{{ state.status }}</span>
  <h2>Selected</h2>
  <ul>
    <li v-for="exp in state.selected" @click="unselectExp(exp)">{{ exp }}</li>
  </ul>
  <h2>All</h2>
  <ul>
    <li v-for="exp in state.exps" @click="selectExp(exp)">{{ exp }}</li>
  </ul>

</template>

<style scoped>
</style>
