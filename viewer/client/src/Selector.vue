<script setup>
import { defineProps, reactive, computed, ref } from 'vue'

const props = defineProps({
  items: { type: Array, required: true },
})

const state = reactive({
  selected: new Set(),
  pattern: '',
})

const matches = computed(() => {
  let values = [...props.items]
  if (state.pattern != '') {
    const regex = new RegExp(state.pattern, 'g')
    values = values.filter(x => regex.test(x))
  }
  return values.reverse()
})

const selected2 = computed(() => {
  return [...state.selected].sort()
})

function select(item) {
  state.selected.add(item)
}

function unselect(item) {
  state.selected.delete(item)
}

</script>

<template>
<div>
  <input v-model="state.pattern" />
  <span>{{ state.pattern }}</span>
  <h2>Selected</h2>
  <ul>
    <li v-for="item in selected2" @click="unselect(item)">{{ item }}</li>
  </ul>
  <h2>Items</h2>
  <ul>
    <li v-for="item in matches" @click="select(item)">{{ item }}</li>
  </ul>
</div>
</template>

<style scoped>
</style>
