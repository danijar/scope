<script setup>

import { ref } from 'vue'
import InputText from './InputText.vue'
import store from './store.js'

const text = ref(store.path.value)

function apply() {
  store.path.value = text.value.trim()
}

</script>

<template>
<div class="path layoutCol">
  <h2>Path</h2>
  <div class="layoutRow">
    <InputText
      v-model="text" class="input" placeholder="basedir"
      insetIcon="folder" @keydown.enter="apply"/>
    <button class="btn icon" @click="apply" title="Apply">check</button>
  </div>
</div>
</template>

<style scoped>

h2 { margin: 0 0 .9rem; }
.input { flex: 1 1; }
.btn { margin-left: .5rem; }

</style>
