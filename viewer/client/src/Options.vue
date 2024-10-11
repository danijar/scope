<script setup>

import { reactive, computed, watch } from 'vue'
import InputText from './InputText.vue'

// const props = defineProps({
//   title: { type: String, default: '' },
//   items: { type: Array, required: true },
//   loading: { type: Boolean, default: false },
// })

const state = reactive({
  binsize: null,
  stepsel: null,
})

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

h2 { margin: 0 0 .8rem; }

.input { margin: 0 0 .5rem; }

</style>

