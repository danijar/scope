export function saveStorage(key, value, allowEmpty = false) {
  if (key.length == 0)
    return fallback
  if (value.length === 0 && !allowEmpty)
    return
  let entry = { type: null, value: value }
  if (value instanceof Set)
    entry = { type: 'Set', value: [...value] }
  console.log('saveStorage', key, entry)
  localStorage.setItem(key, JSON.stringify(entry))
}

export function loadStorage(key, fallback) {
  if (key.length == 0)
    return fallback
  const entry = JSON.parse(localStorage.getItem(key))
  if (entry === null)
    return fallback
  if (entry.type === 'Set')
    return new Set(entry.value)
  else if (entry.type === null)
    return entry.value
  else
    throw `invalid storage entry: ${key} ${entry}`
}
