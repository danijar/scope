<script setup>
import { reactive, computed, onMounted } from 'vue'

const props = defineProps({
  col: { type: String, required: true },
})

const state = reactive({
  status: '',
  col: { steps: [], values: [] },
})

onMounted(async () => {
  state.status = 'loading...'
  state.col = (await (await fetch(`/api/col/${props.col}`)).json())
  state.status = ''
})

const url = computed(() => {
  const value = state.col.values[state.col.values.length - 1]
  return `/api/file/${value}`
})

</script>

<template>
<div class="card">
  <h3>{{ props.col }}</h3>
  <span>Status: {{ state.status }}</span><br>
  <span>Count: {{ state.col.steps.length }}</span><br>
  <span>Step: {{ state.col.steps[state.col.steps.length - 1] }}</span><br>
  <video controls loop v-if="state.col.steps.length">
    <source :src="url" type="video/mp4">
  </video>
</div>
</template>

<style scoped>
.card { overflow: hidden; padding: 1rem; background: white; }
h3 {  }
video { max-width: 100%; max-height: 100%; }
</style>

