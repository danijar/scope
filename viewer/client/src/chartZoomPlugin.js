import { getRelativePosition } from 'chart.js/helpers'


export const ZoomPlugin = {

  id: 'zoom',

  events: ['mousemove', 'mousedown', 'mouseup', 'mouseout'],

  afterInit: function(chart, args, options) {
    chart.zoom = {
      options: options,
      canvasPos: null,
      dataPos: null,
      dragStart: null,
      dragging: false,
      updating: false,
      prevMouseUp: 0,
      prevMouseDown: 0,
      mouseUpListener: null,
    }
    for (const event of this.events)
      if (chart.options.events.indexOf(event) < 0)
        chart.options.events.push(event)
    chart.zoom.mouseUpListener = (e) => { this.stopDrag(chart) }
    document.addEventListener('mouseup', chart.zoom.mouseUpListener)
  },

  afterDestroy: function(chart) {
    document.removeEventListener('mouseup', chart.zoom.mouseUpListener)
  },

  afterEvent: function(chart, args) {

    // if (args.event.type != 'mousemove')
    //   console.log(args.event.type)

    if (args.event.type == 'mousemove') {
      this.move(chart, getRelativePosition(args.event, chart))
    }

    if (args.event.type == 'mousedown') {
      this.move(chart, getRelativePosition(args.event, chart))
      const now = Date.now()
      if (!(now - chart.zoom.prevMouseDown < 100)) {
        chart.zoom.dragStart = chart.zoom.dataPos.x
        chart.zoom.dragging = true
        chart.zoom.prevMouseDown = now
      }
    }

    if (args.event.type == 'mouseup') {
      this.move(chart, getRelativePosition(args.event, chart))
      const now = Date.now()
      if (now - chart.zoom.prevMouseUp < 500)
        this.reset(chart)
      else if (chart.zoom.dragging)
        this.stopDrag(chart)
      chart.zoom.dragging = false
      chart.zoom.prevMouseUp = now
    }

    if (args.event.type == 'mouseout') {
      if (chart.zoom.onLeave)
        chart.zoom.onLeave()
    }

  },

  afterDraw: function(chart, args) {

    if (chart.zoom.dataPos === null)
      return

    const { x: scaleX, y: scaleY } = this.scales(chart)
    const pixelX = scaleX.getPixelForValue(chart.zoom.dataPos.x)
    const minY = scaleY.getPixelForValue(scaleY.min)
    const maxY = scaleY.getPixelForValue(scaleY.max)

    if (chart.zoom.dragging) {
      const startX = scaleX.getPixelForValue(chart.zoom.dragStart)
      chart.ctx.beginPath()
      chart.ctx.rect(startX, minY, pixelX - startX, maxY - minY)
      chart.ctx.lineWidth = 1
      chart.ctx.strokeStyle = 'rgba(127,127,127,0.8)'
      chart.ctx.fillStyle = 'rgba(127,127,127,0.1)'
      chart.ctx.fill()
      chart.ctx.fillStyle = ''
      chart.ctx.stroke()
      chart.ctx.closePath()
    } else {
      chart.ctx.beginPath()
      chart.ctx.moveTo(pixelX, minY)
      chart.ctx.lineWidth = 1
      chart.ctx.strokeStyle = 'rgba(127,127,127,0.8)'
      chart.ctx.lineTo(pixelX, maxY)
      chart.ctx.stroke()
    }

    return true
  },

  move: function(chart, canvasPos) {
    const { x: scaleX, y: scaleY } = this.scales(chart)
    let dataX = scaleX.getValueForPixel(canvasPos.x)
    let dataY = scaleY.getValueForPixel(canvasPos.y)
    dataX = Math.max(scaleX.min, Math.min(dataX, scaleX.max))
    dataY = Math.max(scaleY.min, Math.min(dataY, scaleY.max))
    chart.zoom.canvasPos = canvasPos
    chart.zoom.dataPos = { x: dataX, y: dataY }
    this.updateOnce(chart)
    if (chart.zoom.options.onMove)
      chart.zoom.options.onMove(chart.zoom.dataPos)
  },

  zoom: function(chart, minX, maxX) {
    chart.zoom.dragging = false
    if (minX === maxX) {
      this.updateOnce(chart)
      return
    }
    chart.options.scales.x.min = minX
    chart.options.scales.x.max = maxX
    this.updateOnce(chart)
    this.move(chart, chart.zoom.canvasPos)
    if (chart.zoom.options.onZoom)
      chart.zoom.options.onZoom(minX, maxX)
  },

  reset: function(chart) {
    chart.zoom.dragging = false
    delete chart.options.scales.x.min
    delete chart.options.scales.x.max
    this.updateOnce(chart)
    this.move(chart, chart.zoom.canvasPos)
    if (chart.zoom.options.onReset)
      chart.zoom.options.onReset()
  },

  updateOnce: function(chart) {
    if (chart.zoom.updating)
      return
    chart.zoom.updating = true
    chart.update('none')
    chart.zoom.updating = false
  },

  stopDrag: function(chart) {
    if (!chart.zoom.dragging)
      return
    chart.zoom.dragging = false
    const dragStop = chart.zoom.dataPos.x
    const zoomMin = Math.min(chart.zoom.dragStart, dragStop)
    const zoomMax = Math.max(chart.zoom.dragStart, dragStop)
    this.zoom(chart, zoomMin, zoomMax)
  },

  scales: function(chart) {
    return {
      x: chart.scales.x,
      y: chart.scales.y
    }
  },

}
