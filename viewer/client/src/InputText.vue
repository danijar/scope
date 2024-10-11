<script setup>

import { reactive, computed, watch } from 'vue'

const model = defineModel({ type: String, required: true })

const props = defineProps({
  label: { type: String, default: '' },
  title: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  insetIcon: { type: String, default: '' },
  labelIcon: { type: String, default: '' },
  align: { type: String, default: 'left' },
})

const state = reactive({
  binsize: null,
})

</script>

<template>
<label class="layoutRow">
  <p class="label" v-if="props.label">
    <span v-if="props.labelIcon" class="icon">{{ props.labelIcon }}</span>
    {{ props.label }}
  </p>
  <div class="field layoutRow">
    <span v-if="props.insetIcon" class="icon">{{ props.insetIcon }}</span>
    <input
      v-model="model"
      :title="props.title"
      :placeholder="props.placeholder" />
  </div>
</label>
</template>

<style scoped>

.label { flex: 1 1; margin: .3rem 0; display: flex; align-items: center; user-select: none; }

.field {
  flex: 1 1;
  color: var(--fg3);
  background: var(--bg2);
  border: none;
  padding: .35rem .4rem .25rem;
  border-radius: .5rem;
}

input { border: none; background: transparent; margin: 0; padding: 0 .3rem; }
input { color: var(--fg2); }
input::placeholder { color: var(--fg3); }
input:focus { outline: none; }

input { text-align: v-bind(props.align); }

.label .icon { margin: -.3rem .5rem -.3rem 0; }
.field .icon { font-size: 1.2em; color: var(--fg3); }

</style>

