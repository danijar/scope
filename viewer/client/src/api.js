
export async function getExpids(storeFn, loadingRef) {
  loadingRef.value = true
  storeFn((await (await fetch('/api/exps')).json())['exps'])
  loadingRef.value = false
}

export async function getExps(ids, storeFn, loadingRef) {
  if (!ids.length)
    return
  loadingRef.value = true
  await Promise.all(ids.map(id => getExp(id).then(storeFn)))
  loadingRef.value = false
}

export async function getRuns(ids, storeFn, loadingRef) {
  if (!ids.length)
    return
  loadingRef.value = true
  await Promise.all(ids.map(id => getRun(id).then(storeFn)))
  loadingRef.value = false
}

async function getExp(expid) {
  const exp = await (await fetch(`/api/exp/${expid}`)).json()
  exp.id = expid
  return exp
}

async function getRun(runid) {
  const run = await (await fetch(`/api/run/${runid}`)).json()
  run.id = runid
  return run
}
