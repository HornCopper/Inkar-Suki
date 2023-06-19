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
  if (!v)v = 0
  v &= 0xff
  return v.toString(16)
}
function rgbToHex (r, g, b) {
  return `#${hex_convert(r)}${hex_convert(g)}${hex_convert(b)}`
}
