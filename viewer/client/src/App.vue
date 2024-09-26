<script setup>
import { reactive, onMounted } from 'vue'
import HelloWorld from './HelloWorld.vue'

const state = reactive({
  exps: ['foo', 'bar'],
})

onMounted(async () => {
  console.log('hi')
  let response = await fetch('/api/exps')
  console.log(response)
  // console.log(await response.text())
  let exps = await response.json()
  console.log(exps)
  state.exps = exps['exps']
})

</script>

<template>
  <!--HelloWorld msg="You did it!" /-->
  <ul>
    <li v-for="exp in state.exps">{{ exp }}</li>
  </ul>

</template>

<style scoped>
</style>
