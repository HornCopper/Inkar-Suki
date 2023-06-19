// translate router.meta.title, be used in breadcrumb sidebar tagsview
function generateTitle(title) {
  // const isft = title === 'zhft'
  // if (isft) {
  //   title = 'zh'
  // }
  const hasKey = this.$te('route.' + title)

  if (hasKey) {
    // $t :this method from vue-i18n, inject in @/lang/index.js
    const translatedTitle = this.$t('route.' + title)
    // if(isft)
    return translatedTitle
  } else {
    if (this.$te(title)) {
      return this.$t(title)
    }
  }
  return title
}
