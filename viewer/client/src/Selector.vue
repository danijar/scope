<script setup>

import { reactive, computed, watch } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  items: { type: Array, required: true },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['select', 'unselect'])

const model = defineModel({ type: Set, required: true })

const state = reactive({
  selected: model.value,
  pattern: '',
})

// watch(props.items, x => {
//   const options = new Set(x)
//   for (const item of [...state.selected])
//     if (!options.has(item))
//       state.selected.remove(item)
// })

watch(() => state.selected, () => {
  model.value = state.selected
})

const matches = computed(() => {
  let values = [...props.items]
  if (state.pattern != '') {
    const regex = new RegExp(state.pattern, 'g')
    values = values.filter(x => regex.test(x))
  }
  values = values.filter(x => x)
  return values.reverse()
})

const selectedDisplay = computed(() => {
  return [...state.selected].sort()
})

const matchesDisplay = computed(() => {
  return [...matches.value].filter(x => !state.selected.has(x))
})

function select(item) {
  state.selected.add(item)
  emit('select', item)
}

function unselect(item) {
  state.selected.delete(item)
  emit('unselect', item)
}

function selectAll() {
  let count = 0
  for (const item of matchesDisplay.value) {
    select(item)
    count++
    if (count >= 10)
      break
  }
}

function unselectAll() {
  for (const item of state.selected)
    unselect(item)
}

</script>

<template>
<div class="selector">
  <div class="header layoutRow">
    <h2 v-if="props.title.length">{{ props.title }}</h2>
    <Transition>
      <span v-if="props.loading" class="icon">more_horiz</span>
    </Transition>
  </div>
  <div class="inputs layoutRow">
    <label class="layoutRow">
      <span class="icon">search</span>
      <input v-model="state.pattern" placeholder="Search" />
    </label>
    <span class="btn icon" @click="selectAll" title="Select 10 more">check</span>
    <span class="btn icon" @click="unselectAll" title="Unselect all">close</span>
  </div>
  <div class="list">
    <ul v-if="selectedDisplay.length">
      <li v-for="item in selectedDisplay" @click="unselect(item)" class="selected">
        <span class="icon">check_box</span>
        <div>{{ item }}</div>
      </li>
    </ul>
    <ul v-if="matchesDisplay.length" >
      <li v-for="item in matchesDisplay" @click="select(item)" class="matched">
        <span class="icon">check_box_outline_blank</span>
        <div>{{ item }}</div>
      </li>
    </ul>
  </div>
</div>
</template>

<style scoped>
.selector { display: flex; flex-direction: column; }

.header { flex: 0 0 content; padding-right: 1rem; }
h2 { flex: 1 0 content; margin: 0 .2rem .4rem; font-size: 1.3rem; font-weight: 500; color: #333; }

.inputs { flex: 0 0 content; align-items: center; padding: 0 .5rem .3rem 0; /* border-bottom: 1px solid #ddd; */ }

label .icon { color: #999; }
input { flex: 1 1 content; margin: 0 .3rem; padding: .2rem; font-family: monospace; border: none; color: #888; }
input::placeholder { color: #888; }
input:focus { outline: none; }

.list { flex: 1 1 content; overflow: scroll; }
ul { list-style: none; padding: 0; margin: 0 0 .5rem; }

li { display: flex; align-items: center; cursor: pointer; line-height: 0.95; font-family: monospace; border-radius: .2rem; }
li div { display: 1 1 content; display: inline-block; padding: .2rem; line-height: 0.95; white-space: nowrap; word-break: break-all; }
li:hover { background: #eee; }

/*
.selected { margin: .3rem 0; }
.selected span { background: #ddd; }
.selected:hover span { background: #ccc; }
.matched:hover span { background: #eee; }
*/

</style>
