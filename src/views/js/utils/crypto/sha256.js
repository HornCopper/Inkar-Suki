const CryptoJS = require('crypto-js')
function sha256(data) {
  return CryptoJS.SHA256(data).toString()
}
