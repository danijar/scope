<script setup>
import { reactive, computed, watch } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  items: { type: Array, required: true },
})

const emit = defineEmits(['select', 'unselect'])

const model = defineModel({ type: Set, required: true })

const state = reactive({
  selected: model.value,
  pattern: '',
})

watch(state.selected, () => {
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

</script>

<template>
<div class="selector">
  <h2 v-if="props.title.length">{{ props.title }}</h2>
  <label class="search">
    <span class="icon">search</span>
    <input v-model="state.pattern" placeholder="Search" />
  </label>
  <div class="list">
    <ul v-if="selectedDisplay.length">
      <li v-for="item in selectedDisplay" @click="unselect(item)" class="selected"><span>{{ item }}</span></li>
    </ul>
    <ul v-if="matchesDisplay.length" >
      <li v-for="item in matchesDisplay" @click="select(item)"><span>{{ item }}</span></li>
    </ul>
  </div>
</div>
</template>

<style scoped>
.selector { display: flex; flex-direction: column; }

h2 { flex: 0 1 content; margin: 0 .2rem .4rem; font-size: 1.3rem; font-weight: 500; color: #333; }

.search .icon { font-size: 1.4rem; color: #aaa; margin: 0 .1rem .1rem 0; }
.search input { flex: 0 0 content; margin: 0; padding: .2rem; font-family: monospace; border: none; border-radius: .2rem .2rem 0 0; color: #777; }
.search input::placeholder { color: #777; }
.search input:focus { outline: none; }

.list { flex: 1 1 content; overflow: scroll; }
ul { list-style: none; padding: 0; margin: .5rem 0; }
ul + ul { padding-top: 0; }

li { cursor: default; font-family: monospace; }
li span { display: inline-block; padding: .2rem .2rem; line-height: 0.95; white-space: nowrap; /* background: #fff; */ border-radius: .2rem; }
li:hover span { background: #eee; }
li.selected { margin: .3rem 0; }
li.selected span { background: #ddd; }
li.selected:hover span { background: #ccc; }
</style>
