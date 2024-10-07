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

watch(() => state.selected, () => {
  model.value = state.selected
})

const matches = computed(() => {
  let values = [...props.items]
  if (state.pattern == '')
    return values
  // RegExp objects are stateful and can only be used once.
  return values.filter(x => (new RegExp(state.pattern, 'g')).test(x))
})

// const selectedDisplay = computed(() => {
//   const optionsSet = new Set(props.items)
//   return [...state.selected]
//     .map(x => ({ item: x, available: optionsSet.has(x) }))
//     .sort((a, b) => a.item.localeCompare(b.item))
// })
//
// const matchesDisplay = computed(() => {
//   return [...matches.value]
//     .filter(x => !state.selected.has(x))
//     .sort((a, b) => a.localeCompare(b))
// })

const availableEntries = computed(() => {
  const options = new Set(props.items)
  return [...new Set([...props.items, ...state.selected])]
    .sort()
    .map(item => ({
      item: item,
      name: displayName(item),
      selected: state.selected.has(item),
      missing: !options.has(item),
    }))
})

function displayName(item) {
  return item
    .replace(/_/g, '_<wbr>')
    .replace(/\./g, '<wbr>.')
    .replace(/:/g, ':<br>')
}

function select(item) {
  state.selected.add(item)
  emit('select', item)
}

function unselect(item) {
  state.selected.delete(item)
  emit('unselect', item)
}

function toggle(item) {
  if (state.selected.has(item))
    unselect(item)
  else
    select(item)
}

function selectAll() {
  let count = 0
  for (const entry of availableEntries.value) {
    if (entry.selected)
      continue
    select(entry.item)
    count++
    if (count >= 10)
      break
  }
}

function unselectAll() {
  for (const item of state.selected)
    toggle(item)
}

</script>

<template>
<div class="selector">
  <div class="header layoutRow">
    <h2 v-if="props.title.length">{{ props.title }}</h2>
    <Transition>
      <span v-if="props.loading" class="icon spinner">progress_activity</span>
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

    <!-- <ul> -->
    <!--   <li v-for="entry in selectedDisplay" @click="unselect(entry.item)" :class="{ selected: true, missing: !entry.available }"> -->
    <!--     <span class="icon">check_box</span> -->
    <!--     <div v-html="displayName(entry.item)"></div> -->
    <!--   </li> -->
    <!--   <li v-for="item in matchesDisplay" @click="select(item)" class="matched"> -->
    <!--     <span class="icon">check_box_outline_blank</span> -->
    <!--     <div v-html="displayName(item)"></div> -->
    <!--   </li> -->
    <!-- </ul> -->

    <ul>
      <li v-for="entry in availableEntries" @click="toggle(entry.item)"
          :class="{ selected: entry.selected, missing: entry.missing }">
        <span v-if="entry.selected" class="icon">check_box</span>
        <span v-else class="icon">check_box_outline_blank</span>
        <div v-html="entry.name"></div>
      </li>
    </ul>

  </div>
</div>
</template>

<style scoped>
.selector { display: flex; flex-direction: column; }

.header { flex: 0 0 content; padding-right: 1rem; }
h2 { flex: 1 0 content; margin: 0 .2rem .4rem; font-size: 1.3rem; font-weight: 500; color: var(--fg2); }
.spinner { color: var(--fg3); margin-right: -.2rem; }

.inputs { flex: 0 0 content; align-items: center; padding: 0 .5rem .3rem 0; }

label .icon { color: var(--fg3); }
input { flex: 1 1 content; margin: 0 .3rem; padding: .2rem; font-family: monospace; border: none; color: 999; }
input::placeholder { color: 999; }
input:focus { outline: none; }

.list { flex: 1 1 content; overflow: scroll; }
ul { list-style: none; padding: 0; margin: 0 0 .5rem; }

li { display: flex; align-items: center; cursor: pointer; line-height: 1; font-family: monospace; border-radius: .2rem; }
li div { display: 1 1 content; padding: .3rem; white-space: nowrap; }
li:hover { background: var(--bg2); }

.missing { color: var(--fg3); }

</style>
