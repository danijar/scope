<script setup>

import { reactive, computed, watch, onMounted } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  status: { type: String, default: '' },
})

const state = reactive({
  zoom: false,
})

</script>

<template>
<div class="card" :class="{ zoom: state.zoom }">
  <div class="header">
    <span class="btnZoom btn icon" @click="state.zoom = !state.zoom">fullscreen</span>
    <h2>{{ props.name }}</h2>
    <span v-if="props.status">{{ props.status }}</span>
  </div>
  <div class="content">
    <slot></slot>
  </div>
</div>
</template>

<style scoped>
.card { max-height: 20rem; overflow: hidden; display: flex; flex-direction: column; padding: 1rem 0; background: white; border-radius: .2rem; border: 1px solid #ddd; }
.header { padding: 0 1rem 1rem; }
.content { width: 100%; overflow-x: hidden; overflow-y: auto; padding: 0 1rem 1rem; }

h3 { margin: 0; }

.btnZoom { float: right; }
.zoom.card { position: absolute; max-height: inherit; top: 2rem; right: 2rem; bottom: 2rem; left: 2rem; z-index: 1; }

</style>
