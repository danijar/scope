<script setup>

import { reactive, computed, watch, onMounted } from 'vue'

// const emit = defineEmits(['resize'])

const props = defineProps({
  name: { type: String, required: true },
  loading: { type: Boolean, default: false },
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
  class="card layoutCol" :class="{ zoom: state.zoom }"
  tabindex="0" @keydown.f.prevent="toggleZoom" @keydown.esc.prevent="state.zoom = false">
  <div class="header">
    <h2>{{ props.name }}</h2>
    <Transition>
      <span v-if="props.loading" class="icon spinner">progress_activity</span>
    </Transition>
    <div class="buttons">
      <slot name="buttons"></slot>
      <span class="btn icon" @click="toggleZoom" title="Fullscreen">fullscreen</span>
    </div>
  </div>
  <div class="content">
    <slot></slot>
  </div>
</div>
</template>

<style scoped>
.card { padding: 1rem 0; background: white; border-radius: .2rem; }
.header { flex: 0 0 content; display: flex; padding: 0 1rem 1rem; }
.content { flex: 1 1 content; width: 100%; overflow-x: hidden; overflow-y: auto; padding: 0 1rem; }

h2 { flex: 1 1 content; margin: 0; }
.buttons { flex: 0 0 content; margin: -.3rem; margin-left: 0; }

.zoom.card { position: absolute; height: inherit; max-height: inherit; aspect-ratio: auto; top: 2rem; right: 2rem; bottom: 2rem; left: 2rem; z-index: 1; }

</style>
