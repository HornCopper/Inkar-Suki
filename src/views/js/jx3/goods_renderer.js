const self = {}
/**
 * 渲染某一个单独的Text标签成Span或链接
 * @param {*} school_id
 * @returns
 */
function renderItemHtml(item) {
  let content = item.text
  let style = ``
  let link = null
  content = content.replace(/\\n/g, '<br />').replace(/\\/g, '')
  if ([item.r, item.g, item.b].every((v) => v != undefined && v > 0)) {
    style = `color: rgb(${item.r}, ${item.g}, ${item.b});`
  } else if (item.font != undefined && item.font != 100) {
    // const fonts = require('../assets/data/game_font.json')
    // for (let color in fonts) {
    //   if (fonts[color].includes(item.font)) {
    //     style = `color: ${color};`
    //     break
    //   }
    // }
  }
  if (self.ignoreColor) {
    style = ''
  }
  return `<span style="${style}">${content}</span>`
}
/**
 * 将image标签转换为HTML标签
 */
function renderImageHtml(Text) {
  // <image>path="fromiconid" frame=1241 w=29 h=29 </image>
  let matches = Text.match(/<image>(.*?)<\/image>/gims)
  if (!matches) return Text
  for (let match of matches) {
    let icon_id = match.match(/frame=(\d+)/i)?.[1]
    let w = parseInt(match.match(/w=(\d+)/i)?.[1]) / 1.12
    let h = parseInt(match.match(/h=(\d+)/i)?.[1]) / 1.12
    let src = `https://icon.jx3box.com/icon/${icon_id}.png`
    let html = `<img src="${src}" style="width: ${w}px; height: ${h}px; margin-bottom: -5px" />`
    Text = Text.replace(match, html)
  }
  return Text
}
/**
 * 将一段游戏内文本转换为Html
 * @param {Object[]} texts 标签对象
 */
function renderTextHtml(Text) {
  let result = Text
  result = self.renderImageHtml(result)
  const matches = Text.match(/<Text>(.*?)<\/text>/gims)
  if (!matches) return Text
  for (let match of matches) {
    let text = extractTextContent(match)
    let html = self.renderItemHtml(text[0])
    result = result.replace(match, html)
  }
  return result
}
/**
 * 获取形如<BUFF 110 1 desc>, <ENCHANT 100>的资源字段并转换
 */
async function renderBuffResource() {
  const matches = self.html?.match(/<BUFF (\d+) (\d+) (.*?)>/gim)
  if (!matches) return
  let resourceKeys = []
  let replaceMap = {}
  //先统计需要的资源，减少请求数量
  for (let match of matches) {
    let [token, id, level, type] = match.match(/<BUFF (\d+) (\d+) (.*?)>/i)
    resourceKeys.push(`${id}_${level}`)
    if (level != 0) resourceKeys.push(`${id}_0`)
    replaceMap[token] = [id, level, type]
  }
  await getAllResources('buff', resourceKeys, self.client)
  for (let replace in replaceMap) {
    let [id, level, type] = replaceMap[replace]
    // 持续时间
    if (type === 'time') {
      let interval
      let buff = self.getResource('buff', id, level)
      if (buff['Interval']) interval = buff['Interval']
      else interval = self.getResource('buff', id, 0)['Interval']
      if (!interval) {
        console.log(replace, escapeHTML(replace))
        self.html = self.html.replace(replace, escapeHTML(replace))
        continue
      }
      let time = interval / 16
      if (time > 60) {
        time = Math.floor(time / 60) + '分钟'
      } else {
        time = time + '秒'
      }
      self.html = self.html.replace(replace, escapeHTML(time))
      continue
    }
    // buff描述
    if (type === 'desc') {
      let buff = self.getResource('buff', id, level)
      let desc = buff['Desc']
      if (!desc) desc = self.getResource('buff', id, 0)['Desc']
      if (!desc) {
        self.html = self.html.replace(replace, escapeHTML(replace))
        continue
      }
      // buff的描述里面可能会混着一些buff的属性啥的
      let _matches = desc.match(/<BUFF ([0-9a-zA-Z]+)>/gi)
      if (_matches) {
        for (let _m of _matches) {
          let [_, _attr] = _m.match(/<BUFF ([0-9a-zA-Z]+)>/i)
          for (let i = 1; i < 15; i++) {
            if (buff[`BeginAttrib${i}`] == _attr) {
              desc = desc.replace(_m, buff[`BeginValue${i}A`])
            }
          }
        }
      }
      self.html = self.html.replace(replace, desc)
    }
  }
}
async function renderEnchantResource() {
  const matches = self.html.match(/<ENCHANT (\d+)>/gim)
  if (!matches) return
  let resourceKeys = []
  let replaceMap = {}
  for (let match of matches) {
    let enchant_id = match.match(/<ENCHANT (\d+)>/i)[1]
    resourceKeys.push(enchant_id)
    replaceMap[match] = enchant_id
  }
  await self.getAllResources('enchant', resourceKeys, self.client)
  for (let replace in replaceMap) {
    try {
      let enchant_id = replaceMap[replace]
      let enchant = self.getResource('enchant', enchant_id)
      let time = enchant.Time
      if (time) time = `，持续${parseInt(time) / 60}分钟。`
      let result = `${enchant.AttriName}${time ? time : ''}`
      self.html = self.html.replace(replace, result)
    } catch (e) {
      console.log(e)
      self.html = self.html.replace(replace, escapeHTML(replace))
    }
  }
}
function renderResource() {
  renderBuffResource()
  renderEnchantResource()
}
async function getAllResources(type, ids) {
  let resources = await getResourceFromNode(type, ids, self.client)
  let data = resources.data
  if (data.length === undefined) data = [data]
  if (type == 'buff') {
    for (let item of data) {
      let buff_token = `${item.BuffID}_${item.Level}`
      sessionStorage.setItem(
        `buff-${self.client}-${buff_token}`,
        JSON.stringify(item)
      )
    }
  } else if (type == 'enchant') {
    for (let item of data) {
      let enchant_token = `${item.ID}`
      sessionStorage.setItem(
        `enchant-${self.client}-${enchant_token}`,
        JSON.stringify(item)
      )
    }
  }
}
function getResource(type, id, level) {
  let token = `${id}`
  if (type == 'buff') {
    token = `${id}_${level}`
  }
  let resource = sessionStorage.getItem(`${type}-${self.client}-${token}`)
  if (resource) return JSON.parse(resource)
  return null
}

self.renderItemHtml = renderItemHtml
self.renderImageHtml = renderImageHtml
self.renderTextHtml = renderTextHtml
self.renderBuffResource = renderBuffResource
self.renderEnchantResource = renderEnchantResource
self.renderResource = renderResource
self.getAllResources = getAllResources
self.getResource = getResource