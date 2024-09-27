<script setup>
import { reactive, computed } from 'vue'

const props = defineProps({
  col: { type: String, required: true },
})

</script>

<template>
<div class="card">
  <h3>{{ props.col }}</h3>
</div>
</template>

<style scoped>
.card { background: white; }
h3 {  }
</style>

