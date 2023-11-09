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

const render_watermark = ({
  content,
  rotate,
  dense,
  fillStyle,
  font,
  line_height,
  offset_x,
  offset_y,
}) => {
  if (!rotate) rotate = 30
  if (!fillStyle) fillStyle = 'rgba(0, 0, 0, 0.1)'
  if (!font) font = '3rem "Times New Roman"'
  if (!dense) dense = 5
  if (!line_height) line_height = 50
  if (!offset_x) offset_x = 20
  if (!offset_y) offset_y = 10
  const id = 'comp-glo-watermark'
  if (document.getElementById(id) !== null)
    document.body.removeChild(document.getElementById(id))
  const client_width = document.documentElement.clientWidth
  const client_height = document.documentElement.clientHeight
  const can = document.createElement('canvas')
  can.width = client_width / dense
  can.height = client_height / dense
  const cans = can.getContext('2d')
  cans.rotate((rotate * Math.PI) / 180)
  cans.font = font
  cans.fillStyle = fillStyle
  cans.textBaseline = 'Middle'
  cans.textAlign = 'center'
  content.split('\n').map((x, line) => {
    cans.fillText(x, offset_x + can.width / 2, offset_y + line * line_height)
  })

  const div = document.createElement('div')
  div.id = id
  div.style.pointerEvents = 'none'
  div.style.top = `-${client_height / 2}px`
  div.style.left = `-${client_width / 2}px`
  div.style.position = 'fixed'
  div.style.zIndex = 1e8
  div.style.width = `${8 * client_width}px`
  div.style.height = `${8 * client_height}px`
  div.style.background = `url(${can.toDataURL('image/png')}) left top repeat`
  document.body.appendChild(div)
  return id
}
const render_watermark_default = (content) => {
  render_watermark({
    content: content || 'Inkar Suki',
    font: '2rem "Helvetica"',
  })
}
