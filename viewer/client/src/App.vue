<script setup>

import { reactive, computed, watch, onMounted, ref, toRef } from 'vue'
import { saveStorage, loadStorage } from './storage.js'
import store from './store.js'

import Selector from './Selector.vue'
import Card from './Card.vue'
import CardFloat from './CardFloat.vue'
import CardVideo from './CardVideo.vue'
import CardText from './CardText.vue'

const columns = ref(loadStorage('columns', 3))

watch(() => columns, x => saveStorage('columns', x.value), { deep: true })

function toggleLayout() {
  columns.value = columns.value % 5 + 1
}

</script>

<template>
<div class="app layoutCol">
  <div class="header layoutRow">
    <h1>Scope</h1>
    <span class="fill"></span>
    <span class="btn icon" @click="store.refresh">refresh</span>
    <span class="btn icon" @click="toggleLayout">settings</span>
  </div>
  <div class="content layoutRow">

    <div class="left layoutCol">
      <Selector
        :items="store.availableMets.value" v-model="store.selMets.value"
        :loading="!!store.pendingRuns.value.size" title="Metrics" class="selector" />
    </div>

    <div class="center">
      <div class="cards">
        <template v-for="card in store.availableCards.value" :key="card.met">
          <CardFloat
            v-if="card.ext == 'float'"
            :name="card.name" :cols="card.cols" class="card" />
          <CardText
            v-else-if="card.ext == 'txt'"
            :name="card.name" :cols="card.cols" class="card" />
          <CardVideo
            v-else-if="['mp4', 'webm'].includes(card.ext)"
            :name="card.name" :cols="card.cols" class="card" />
          <Card v-else :name="card.name" class="card">
            Unknown metric type: {{ card.ext }}</Card>
        </template>
      </div>
    </div>

    <div class="right layoutCol">
      <Selector
        :items="store.availableExps.value" v-model="store.selExps.value"
        :loading="!!store.pendingEids.value" title="Experiments" class="selector" />
      <Selector
        :items="store.availableRuns.value" v-model="store.selRuns.value"
        :loading="!!store.pendingExps.value.size" title="Runs" class="selector" />
    </div>
  </div>

  <!-- <div class="footer"> -->
  <!--   DEBUG: -->
  <!--   pending: {{ store.pendingExps }} -->
  <!--   cache: {{ Object.keys(store.cachedExps.value) }} -->
  <!--   {{ Object.keys(store.availableCols.value).sort() }} -->
  <!-- </div> -->

</div>
</template>

<style scoped>

.app { height: 100vh; width: 100vw; }
.header { flex: 0 0 content; align-items: center; padding: 1rem; border-bottom: 2px solid #eee; }
.footer { flex: 0 0 3rem; align-items: center; padding: 1rem; border-top: 2px solid #eee; }
.content { flex: 1 1; }

.center { flex: 1 1 20rem; overflow: auto; background: #eee; }
.left, .right { flex: 0 1 20rem; max-width: 20%; }

.header h1 { font-size: 1.8rem; font-weight: 500; color: #000; padding-left: 1.3em; line-height: 1em; background: url(/logo.png) no-repeat; background-size: contain; user-select: none; }
.header .btn { margin-left: .5rem; }

.selector { flex: 1 1 0; overflow: hidden; padding: 1rem 0 0 1rem; }

.cards { --columns: v-bind(columns); width: 100%; display: grid; grid-template-columns: repeat(var(--columns), 1fr); gap: 1rem; overflow: auto; padding: 1rem; }
.card { height: 30rem; max-height: 80vh; border: 1px solid #ddd; }

</style>
