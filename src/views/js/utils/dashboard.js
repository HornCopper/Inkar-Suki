const rgbIndex = ['r', 'g', 'b']
/**
 * #ff00ff to {r:,g:,b:}
 *
 * @export
 * @param {*} rgbHEX
 * @returns
 */
function hexTorgb(rgbHEX) {
  const r = {}
  for (let i = 0; i < rgbIndex.length; i++) {
    const index = i * 2 + 1
    r[rgbIndex[i]] = hexToint(rgbHEX.slice(index, index + 2))
  }
  return r
}
function hexToint(hex) {
  return parseInt(`0x${hex}`)
}
const hex_convert = (v) => {
  if (!v) v = 0
  v &= 0xff
  return v.toString(16)
}
function rgbToHex(r, g, b) {
  return `#${hex_convert(r)}${hex_convert(g)}${hex_convert(b)}`
}

const series_color = ['#aa00ff', '#0d47a1', '#00c853'] // 紫 蓝 绿
/**
 * 构造追加y轴和series的新 item
 * @option：当前option
 * @index：第几个series
 * @seriesName：当前series name
 * @data：当前series data
 * */
const appendSeriesYAxisItem = ({
  option,
  index,
  seriesName,
  data,
  yAxis_option,
  series_option,
  formatter,
}) => {
  yAxis_option = yAxis_option || {}
  series_option = series_option || {}
  let _color = series_color[index]
  let leftYNum = option.yAxis.filter((sub) => sub.position === 'left').length
  let rightYNum = option.yAxis.filter((sub) => sub.position === 'right').length
  let currentPosition = index % 2 === 0 ? 'left' : 'right'
  const yAxis_opt = Object.assign(
    {
      type: 'value',
      position: currentPosition,
      offset: (currentPosition === 'left' ? leftYNum : rightYNum) * 90,
      name: seriesName,
      nameLocation: 'end',
      splitLine: {
        show: false,
      },
      nameTextStyle: {
        color: _color,
      },
      axisLine: {
        onZero: false,
        lineStyle: {
          color: _color,
        },
      },
      axisLabel: {
        show: true,
        color: _color,
        formatter:
          formatter ||
          ((params) => {
            return params.toFixed(0)
          }),
      },
    },
    yAxis_option
  )
  option.yAxis.push(yAxis_opt)
  const series_opt = Object.assign(
    {
      symbolSize: 2,
      name: seriesName,
      type: 'line',
      data: data,
      yAxisIndex: index,
      itemStyle: {
        color: _color,
      },
      lineStyle: {
        width: 2,
        color: _color,
      },
    },
    series_option
  )
  option.series.push(series_opt)
}
const rotate_with_translate = ({ ctx, rotate, x, y }) => {
  r = (rotate * Math.PI) / 180
  if (x || y) ctx.translate(x, y)
  ctx.rotate(r)
  if (x || y) ctx.translate(-x, -y)
}
const render_watermark = ({
  content,
  rotate,
  dense,
  fillStyle,
  font,
  line_height,
  offset_x,
  offset_y,
  background_style,
}) => {
  if (!rotate) rotate = 30
  if (!fillStyle) fillStyle = 'rgba(0, 0, 0, 0.1)'
  if (!font) font = '3rem "Times New Roman"'
  if (!dense) dense = 5
  if (!line_height) line_height = 50
  if (!offset_x) offset_x = 0
  if (!offset_y) offset_y = 0
  if (!background_style) background_style = ' left top repeat'
  // const id = 'comp-glo-watermark'
  // if (document.getElementById(id) !== null)
  //   document.body.removeChild(document.getElementById(id))
  const client_width = document.getElementById('app').clientWidth
  const client_height = document.getElementById('app').clientHeight
  const can = document.createElement('canvas')
  can.width = client_width / dense
  can.height = client_height / dense
  const ctx = can.getContext('2d')

  rotate_with_translate({ ctx, rotate, x: can.width / 2, y: can.height / 2 })

  ctx.font = font
  ctx.fillStyle = fillStyle
  ctx.textBaseline = 'Middle'
  ctx.textAlign = 'center'
  // ctx.fillRect(0, 0, can.width, can.height)
  content.split('\n').map((x, line) => {
    ctx.fillText(x, can.width / 2, can.height / 2 + line * line_height)
  })

  const div = document.createElement('div')
  // div.id = id
  div.id = `g-canv-${Math.random()}`
  div.style.pointerEvents = 'none'
  div.style.top = `${offset_y}px`
  div.style.left = `${offset_x}px`
  div.style.position = 'fixed'
  div.style.zIndex = 1e8
  div.style.width = `${client_width}px`
  div.style.height = `${client_height}px`
  div.style.background = `url(${can.toDataURL('image/png')})${background_style}`
  document.body.appendChild(div)
  return div.id
}
const render_watermark_default = (content) => {
  const client_width = document.getElementById('app').clientWidth
  const client_height = document.getElementById('app').clientHeight
  const default_config = {
    content: content || 'Inkar Suki',
    font: '2rem "Helvetica"',
    background_style: ' left top repeat',
    fillStyle: 'rgba(0, 0, 0, 0.2)',
  }

  const pos = { x: 0, y: 0 }
  const r = () => {
    pos.x += Math.random()
    if (pos.x > 1) pos.x -= 1
    pos.y += Math.random()
    if (pos.y > 1) pos.y -= 1
  }
  const s = () => {
    r()
    const { x: rx, y: ry } = pos
    render_watermark(
      Object.assign(default_config, {
        background_style: ' left top no-repeat',
        offset_x: rx * client_width * 0.9,
        offset_y: ry * client_height * 0.9,
        rotate: (Math.random() - 0.5) * 180,
      })
    )
  }
  new Array(3).fill(0).map((x) => s())
}
const render_watermark_default_fullscreen = (content) => {
  render_watermark({
    content: content || 'Inkar Suki',
    font: '2rem "Helvetica"',
  })
}
