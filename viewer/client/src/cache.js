import { ref, watch, computed, shallowRef } from 'vue'


export function reactiveCache(func) {

  const cache = ref({})
  const loading = ref({})

  function add(key, refresh = false) {
    if ((key in cache.value || key in loading.value) && !refresh)
      return
    cancel(key)
    const result = func(key)
    if (result instanceof Promise) {
      result.canceled = false
      loading.value[key] = value
      result.then(value => { if (!result.canceled) cache.value[key] = shallowRef(value) })
      result.finally(() => { if (!result.canceled) loading.value.delete(key) })
    } else {
      cache.value[key] = shallowRef(result)
    }
  }

  function remove(key) {
    cancel(key)
    if (key in cache.value)
      delete cache.value[key]
  }

  function setTo(keys, refresh = false) {
    const requested = new Set([...keys])
    const existing = [...Object.keys(cache.value), ...Object.keys(loading.value)]
    for (const key of existing)
      if (!requested.has(key))
        remove(key)
    for (const key of keys)
      add(key, refresh)
  }

  function refresh() {
    const existing = [...Object.keys(cache.value), ...Object.keys(loading.value)]
    for (const key of existing)
      add(key, true)
  }

  function cancel(key) {
    if (!(key in loading.value))
      return
    loading.value[key].canceled = true
    delete loading.value[key]
  }

  cache.loading = loading
  cache.add = add
  cache.remove = remove
  cache.setTo = setTo
  cache.refresh = refresh
  cache.cancel = cancel

  return cache
}
