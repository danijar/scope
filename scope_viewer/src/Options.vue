<script setup>

import { reactive, computed, watch, ref } from 'vue'
import InputText from './InputText.vue'
import store from './store.js'

// const props = defineProps({
//   title: { type: String, default: '' },
//   items: { type: Array, required: true },
//   loading: { type: Boolean, default: false },
// })

const state = reactive({
  binsize: store.options.binsize ? store.options.binsize.toString() : '',
  stepsel: store.options.stepsel ? store.options.stepsel.toString() : '',
})

watch(() => state.binsize, x => store.options.binsize = x ? parseFloat(x) : null)
watch(() => state.stepsel, x => store.options.stepsel = x ? parseInt(parseFloat(x)) : null)

</script>

<template>
<div class="options layoutCol">
  <h2>Options</h2>
  <InputText
    v-model="state.binsize" class="input" label="Binning"
    align="center" placeholder="number" labelIcon="leaderboard"/>
  <InputText
    v-model="state.stepsel" class="input" label="Step"
    align="center" placeholder="number" labelIcon="location_on"/>
</div>
</template>

<style scoped>
.options { display: flex; flex-direction: column; }

h2 { margin: 0 0 .9rem; }

.input { margin: 0 0 .5rem; }

</style>

