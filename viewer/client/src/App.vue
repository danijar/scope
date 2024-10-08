<script setup>

import { reactive, computed, watch, onMounted, ref, toRef } from 'vue'
import { saveStorage, loadStorage } from './storage.js'
import store from './store.js'

import Selector from './Selector.vue'
import Card from './Card.vue'
import CardFloat from './CardFloat.vue'
import CardVideo from './CardVideo.vue'
import CardText from './CardText.vue'

const options = reactive(loadStorage('options', {
  columns: 3,
  dark: false,
}))

watch(() => options, x => saveStorage('options', x), { deep: true })

function toggleLayout() {
  options.columns = options.columns % 5 + 1
}

</script>

<template>
<div class="app layoutCol" :class="{ dark: options.dark }">
  <div class="header layoutRow">
    <span class="logo"></span>
    <h1>Scope</h1>
    <span class="fill"></span>
    <span class="btn icon" @click="store.refresh" title="Refresh">refresh</span>
    <span class="btn icon" @click="toggleLayout" title="Change layout">view_column</span>
    <span class="btn icon" @click="options.dark = true" v-if="!options.dark" title="Dark mode">dark_mode</span>
    <span class="btn icon" @click="options.dark = false" v-if="options.dark" title="Light mode">light_mode</span>
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

.app { height: 100vh; width: 100vw; background: var(--bg1); color: var(--fg1); }
.header { flex: 0 0 content; align-items: center; padding: 1rem; border-bottom: 2px solid var(--bg2); user-select: none; }
.footer { flex: 0 0 3rem; align-items: center; padding: 1rem; border-top: 2px solid var(--bg2); }
.content { flex: 1 1; }

.center { flex: 1 1 20rem; overflow: auto; background: var(--bg2); }
.left, .right { flex: 0 1 20rem; max-width: 20%; }

.header .logo { display: inline-block; padding-left: 1.3em; width: 1em; height: 1em; font-size: 1.8rem; background: url(/logo.png) no-repeat; background-size: contain; }
.header h1 { font-size: 1.8rem; font-weight: 500; line-height: 1; }
.header .btn { margin-left: .5rem; }

.selector { flex: 1 1 0; overflow: hidden; padding: 1rem 0 0 1rem; }

.cards { --columns: v-bind(options.columns); width: 100%; display: grid; grid-template-columns: repeat(var(--columns), 1fr); gap: 1rem; overflow: auto; padding: 1rem; }
.card { height: 30rem; max-height: 80vh; border: 1px solid var(--bg3); }

</style>
