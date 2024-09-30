function saveStorage(key, value) {

  if (value.length === 0)
    return  // TODO

  let entry = { type: null, value: value }

  if (value instanceof Set)
    entry = { type: 'Set', value: [...value] }

  console.log('saveStorage', key, entry)

  localStorage.setItem(key, JSON.stringify(entry))
}

function loadStorage(key, fallback) {
  const entry = JSON.parse(localStorage.getItem(key))
  if (entry === null) {
    // console.log('loadStorage (fallback)', key, fallback)
    return fallback
  }

  // console.log('loadStorage', key, entry)

  if (entry.type === 'Set')
    return new Set(entry.value)
  else if (entry.type === null)
    return entry.value
  else
    throw `invalid storage entry: ${key} ${entry}`
}

export {
  saveStorage,
  loadStorage
}
