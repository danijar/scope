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
  class="card layoutCol" :class="{ zoom: state.zoom }" title="Fullscreen"
  tabindex="0" @keydown.f.prevent="toggleZoom" @keydown.esc.prevent="state.zoom = false">
  <div class="header">
    <div class="buttons layoutRow">
      <slot name="buttons"></slot>
      <span class="btn icon" @click="toggleZoom">fullscreen</span>
    </div>
    <h2>{{ props.name }}</h2>
    <span v-if="props.status">{{ props.status }}</span>
  </div>
  <div class="content">
    <slot></slot>
  </div>
</div>
</template>

<style scoped>
.card { padding: 1rem 0; background: white; border-radius: .2rem; }
.header { flex: 0 0 content; padding: 0 1rem 1rem; }
.content { flex: 1 1 content; width: 100%; overflow-x: hidden; overflow-y: auto; padding: 0 1rem; }

h3 { margin: 0; }

.buttons { float: right; margin: -.3rem; }

.zoom.card { position: absolute; height: inherit; max-height: inherit; aspect-ratio: auto; top: 2rem; right: 2rem; bottom: 2rem; left: 2rem; z-index: 1; }

</style>
