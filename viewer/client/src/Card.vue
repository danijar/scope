<script setup>

import { reactive, computed, watch, onMounted } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  loading: { type: Boolean, default: false },
  scrollX: { type: Boolean, default: false },
  scrollY: { type: Boolean, default: true },
})

const state = reactive({
  zoom: false,
})

function toggleZoom() {
  state.zoom = !state.zoom
}

</script>

<template>
<div
  class="card layoutCol" :class="{ zoom: state.zoom }"
  tabindex="0" @keydown.f.exact.prevent="toggleZoom" @keydown.esc.prevent="state.zoom = false">
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
  <div class="content" :class="{ scrollX, scrollY }">
    <slot></slot>
  </div>
</div>
</template>

<style scoped>
.card { padding: 1rem 0 0; background: var(--bg1); border-radius: .2rem; }
.header { flex: 0 0 content; display: flex; margin: 0 1rem; }
.content { flex: 1 1 content; margin: 1rem; overflow: hidden; }

/* .scrollX { overflow-x: auto; } */
/* .scrollY { overflow-y: auto; } */

.scrollX { overflow-x: scroll; margin-bottom: 0; padding-bottom: 1rem; }
.scrollY { overflow-y: auto; margin-right: 0; padding-right: 1rem; }

h2 { flex: 1 1 content; margin: 0; word-break: break-word; }
.buttons { flex: 0 0 content; margin: -.3rem; margin-left: 0; }

.zoom.card { position: absolute; height: inherit; max-height: inherit; aspect-ratio: auto; top: 2rem; right: 2rem; bottom: 2rem; left: 2rem; z-index: 1; }
.zoom.card { border: 2px solid var(--br); }

</style>
