<script setup>

import { reactive, computed, watch } from 'vue'
import { saveStorage, loadStorage } from './storage.js'
import InputText from './InputText.vue'

const props = defineProps({
  title: { type: String, default: '' },
  items: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  reverse: { type: Boolean, default: false },
  storageKey: { type: String, default: '' },
})

const emit = defineEmits(['select', 'unselect'])

const model = defineModel({ type: Set, required: true })

const state = reactive({
  selected: model.value,
  pattern: loadStorage(props.storageKey, ''),
})

watch(() => state.selected, () => { model.value = state.selected })

watch(() => state.pattern, x => saveStorage(props.storageKey, x, true))

const itemsSorted = computed(() => {
  const sorted = props.items.sort()
  return props.reverse ? sorted.toReversed() : sorted
})

const itemsSet = computed(() => {
  return new Set(props.items)
})

const availableEntries = computed(() => {
  const missing = [...state.selected]
    .filter(item => !(itemsSet.value.has(item)))
  // RegExp objects are stateful and can only be used once.
  const pattern = state.pattern || '.*'
  const available = itemsSorted.value
    .filter(item => state.selected.has(item) || (new RegExp(pattern, 'g')).test(item))
  return [...missing, ...available].map(item => ({
    item: item,
    name: displayName(item),
    selected: state.selected.has(item),
    missing: !itemsSet.value.has(item),
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
<div class="selector layoutCol focusgroup">
  <div class="header layoutRow">
    <h2 v-if="props.title.length">{{ props.title }}</h2>
    <Transition>
      <span v-if="props.loading" class="icon spinner">progress_activity</span>
    </Transition>
  </div>
  <div class="inputs layoutRow">
    <InputText v-model="state.pattern" class="input nofocusgroup" insetIcon="search"/>
    <button class="btn icon" @click="selectAll" title="Select 10 more">check</button>
    <button class="btn icon" @click="unselectAll" title="Unselect all">close</button>
  </div>
  <div class="list layoutCol">
    <div v-for="entry in availableEntries">
      <button class="entry smooth"
           :class="{ selected: entry.selected, missing: entry.missing }"
           @click="toggle(entry.item)"
           @keydown.space.exact.prevent="toggle(entry.item)"
           @keydown.enter.exact.prevent="toggle(entry.item)">
        <span v-if="entry.selected" class="icon filled">check_box</span>
        <span v-else class="icon">check_box_outline_blank</span>
        <span v-html="entry.name" class="name"></span>
      </button>
    </div>
  </div>
</div>
</template>

<style scoped>
.selector { display: flex; flex-diregtion: column; }

.header { flex: 0 0 content; padding-right: 1rem; }
h2 { flex: 1 0 content; margin: 0 .1rem .5rem; }
.spinner { margin-right: -.15rem; }

.inputs { flex: 0 0 content; align-items: center; padding: 0 .5rem .4rem 0; }
.input { margin-right: .3rem; }

.list { flex: 1 1 content; overflow-y: auto; margin: 0 0 1rem; padding: 0 1rem 0 0; }

.entry { display: inline-flex; align-items: center; cursor: pointer; line-height: 1; font-family: monospace; border-radius: .4rem; color: var(--fg2); padding: .2rem .3rem .2rem .1rem; }
.entry:hover, .entry:focus { background: var(--bg2); outline: none; }
.name { padding-left: .3rem; word-break: break-word; }

.missing { color: var(--fg3); }

</style>
