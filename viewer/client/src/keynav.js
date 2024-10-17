
const navKeys = ['ArrowDown', 'ArrowUp', 'ArrowLeft', 'ArrowRight', 'h', 'j', 'k', 'l', 'g', 'G']
const navKeysInput = ['ArrowDown', 'ArrowUp', 'ArrowLeft', 'ArrowRight']
const optionsSelInclude = '.focusable, input, button'
const optionsSelExclude = '.nofocusgroup, .nofocusgroup *'

let lastG = null

export function handleKeydown(e) {

  if (e.key == 'Tab') {
    setupFocusGroups()
    return
  }

  if (e.ctrlKey || e.metaKey || e.altKey)
    return
  if (e.target.nodeName == 'INPUT' && !navKeysInput.includes(e.key))
    return
  if (!navKeys.includes(e.key))
    return

  // console.log(e)

  const group = e.target.closest('.focusgroup')
  if (!group) return

  const options = getOptions(group)
  let index = options.indexOf(e.target)
  if (index < 0) return

  const columns = group.getAttribute('focusCols')

  if (e.key == 'g' || e.key == 'G') {

    if (e.shiftKey) {
      index = options.length - 1
    } else if (Date.now() - lastG < 200) {
      index = 0
      lastG = null;
    } else {
      lastG = Date.now();
    }

  } else if (columns) {
    let row = Math.floor(index / columns)
    let col = index % columns

    if (e.key == 'ArrowDown' || e.key == 'j')
      row++
    if (e.key == 'ArrowUp' || e.key == 'k')
      row--
    if (e.key == 'ArrowRight' || e.key == 'l')
      col++
    if (e.key == 'ArrowLeft' || e.key == 'h')
      col--

    row = Math.max(0, Math.min(row, Math.ceil(options.length / columns) - 1))
    col = Math.max(0, Math.min(col, columns - 1))
    index = row * columns + col

  } else {

    if (e.key == 'ArrowDown' || e.key == 'j')
      index++
    if (e.key == 'ArrowUp' || e.key == 'k')
      index--
    if (e.key == 'ArrowRight' || e.key == 'l')
      index++
    if (e.key == 'ArrowLeft' || e.key == 'h')
      index--

  }

  index = Math.max(0, Math.min(index, options.length - 1))
  options.map((el, i) => el.tabIndex = (i == index) ? 0 : -1)
  options[index].focus()
}

function setupFocusGroups() {
  const groups = [...document.querySelectorAll('.focusgroup')]
  groups.map(group => {
    const options = getOptions(group)
    const active = options.filter(el => el.tabIndex == 0)
    const index = active.length ? options.indexOf(active[0]) : 0
    options.map((el, i) => el.tabIndex = (i == index) ? 0 : -1)
    // console.log(group, active, index, options)
  })
}

function getOptions(group) {
  return [...group.querySelectorAll(optionsSelInclude)]
      .filter(el => !el.matches(optionsSelExclude))
}
