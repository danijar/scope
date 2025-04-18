<script setup>

import { reactive, computed, watch, onMounted, ref, toRef } from 'vue'
import { saveStorage, loadStorage } from './storage.js'
import store from './store.js'
import { handleKeydown } from './keynav.js'

import Selector from './Selector.vue'
import Options from './Options.vue'
import Card from './Card.vue'
import CardFloat from './CardFloat.vue'
import CardText from './CardText.vue'
import CardImage from './CardImage.vue'
import CardVideo from './CardVideo.vue'

const settings = reactive(loadStorage('settings', {
  columns: 3,
  dark: false,
}))

watch(() => settings, x => saveStorage('settings', x), { deep: true })

function toggleLayout() {
  settings.columns = settings.columns % 5 + 1
}

const keyboardMode = ref(false)

// The listener needs to be global, because the app element is not focused on
// page load, before the user focuses an element.
document.addEventListener('keydown', (e) => {
  if (e.key == 'Tab')
    keyboardMode.value = true
  handleKeydown(e)
})
document.addEventListener('mousedown', (e) => {
  keyboardMode.value = false
})

</script>

<template>
<div class="app layoutCol" :class="{ dark: settings.dark, keyboardMode: keyboardMode }">
  <div class="header layoutRow focusgroup">
    <span class="logo"></span>
    <h1>Scope</h1>
    <span class="fill"></span>
    <button class="btn icon" @click="store.refresh" title="Refresh">refresh</button>
    <button class="btn icon" @click="toggleLayout" title="Change layout">view_column</button>
    <button
      class="btn icon" @click="settings.dark = !settings.dark"
      :title="settings.dark ? 'Light mode' : 'Dark mode'">
      {{ settings.dark ? 'light_mode' : 'dark_mode' }}</button>
  </div>
  <div class="content layoutRow">

    <div class="right layoutCol">
      <Selector
        :items="store.availableExps.value" v-model="store.selExps.value" :reverse="true"
        :loading="!!store.pendingEids.value" storageKey="selectorFolders"
        title="Folders" class="selector" />
      <Selector
        :items="store.availableRuns.value" v-model="store.selRuns.value"
        :loading="!!store.pendingExps.value.size" storageKey="selectorRuns"
        title="Runs" class="selector" />
    </div>

    <div class="left layoutCol">
      <Selector
        :items="store.availableMets.value" v-model="store.selMets.value"
        :loading="!!store.pendingRuns.value.size" storageKey="selectorMets"
        title="Metrics" class="selector" />
      <Options class="options"/>
      <!-- <div class="spacer"></div> -->
    </div>

    <div class="center">
      <div class="cards focusgroup" :focusCols="settings.columns">
        <template v-for="card in store.availableCards.value" :key="card.name">
          <CardFloat
            v-if="card.ext == 'float'"
            :name="card.name" :cols="card.cols" class="card" />
          <CardText
            v-else-if="card.ext == 'txt'"
            :name="card.name" :cols="card.cols" class="card" />
          <CardImage
            v-else-if="['png', 'jpg', 'jpeg'].includes(card.ext)"
            :name="card.name" :cols="card.cols" class="card" />
          <CardVideo
            v-else-if="['mp4', 'webm'].includes(card.ext)"
            :name="card.name" :cols="card.cols" class="card" />
          <Card v-else :name="card.name" class="card">
            Unknown metric type: {{ card.ext }}</Card>
        </template>
      </div>
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
.header { flex: 0 0 content; align-items: center; padding: 1rem; user-select: none; }
.footer { flex: 0 0 3rem; align-items: center; padding: 1rem; }
.content { flex: 1 1; }

.center { flex: 1 1 20rem; overflow: auto; background: var(--bg3); }
.left, .right { flex: 0 1 20rem; max-width: 20%; }

.left { order: 1; }
.center { order: 2; }
.right { order: 3; }

.header .logo { display: inline-block; padding-left: 1.3em; width: 1em; height: 1em; font-size: 1.8rem; background: url(/logo.png) no-repeat; background-size: contain; }
.header h1 { font-size: 1.8rem; font-weight: 500; line-height: 1; }
.header .btn { margin-left: .5rem; }

.selector { flex: 1 1 0; overflow: hidden; padding: 1rem 0 0 1rem; }
.options { flex: 1 1 0; padding: 1rem; }
.spacer { flex: 1 1 0; }

.cards { --columns: v-bind(settings.columns); width: 100%; display: grid; grid-template-columns: repeat(var(--columns), 1fr); gap: 1rem; overflow: auto; padding: 1rem; padding-top: .8rem; }
.card { height: 30rem; max-height: 80vh; border-radius: .5rem; }

.header, .selector, .options { border-bottom: .2rem solid var(--bg3); }

</style>
