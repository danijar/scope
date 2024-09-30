<script setup>

import { reactive, computed, watch, onMounted } from 'vue'

// const emit = defineEmits(['resize'])

const props = defineProps({
  name: { type: String, required: true },
  status: { type: String, default: '' },
})

const state = reactive({
  zoom: false,
})

function toggleZoom() {
  state.zoom = !state.zoom
  // emit('resize')
}

// watch(state.zoom, (zoom) => {
//   emit('resize')
// })

</script>

<template>
<div
  class="card" :class="{ zoom: state.zoom }"
  tabindex="0" @keydown.f.prevent="toggleZoom" @keydown.esc.prevent="state.zoom = false">
  <div class="header">
    <span class="btnZoom btn icon" @click="toggleZoom">fullscreen</span>
    <h2>{{ props.name }}</h2>
    <span v-if="props.status">{{ props.status }}</span>
  </div>
  <div class="content">
    <slot></slot>
  </div>
</div>
</template>

<style scoped>
.card { overflow: hidden; display: flex; flex-direction: column; padding: 1rem 0; background: white; border-radius: .2rem; border: 1px solid #ddd; }
.header { flex: 0 0 content; padding: 0 1rem 1rem; }
.content { flex: 1 1 content; width: 100%; overflow-x: hidden; overflow-y: auto; padding: 0 1rem 1rem; }

h3 { margin: 0; }

.btnZoom { float: right; }
.zoom.card { position: absolute; height: inherit; aspect-ratio: auto; top: 2rem; right: 2rem; bottom: 2rem; left: 2rem; z-index: 1; }

</style>
