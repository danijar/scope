<script setup>
import { reactive, computed } from 'vue'

const props = defineProps({
  path: { type: String, required: true },
})

</script>

<template>
<div class="card">
  <h3>{{ props.path }}</h3>
</div>
</template>

<style scoped>
.card { flex: 1 1 20rem; background: white; }
h3 {  }
</style>

