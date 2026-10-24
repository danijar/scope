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
  <h2>Root</h2>
  <div class="inputs layoutRow">
    <InputText
      v-model="text" class="input"
      insetIcon="folder" @keydown.enter="apply"/>
    <button class="btn icon" @click="apply" title="Apply">arrow_forward</button>
  </div>
</div>
</template>

<style scoped>

h2 { margin: 0 0 .9rem; }
.inputs { align-items: center; }
.input { flex: 1 1; margin-right: .3rem; }

</style>
