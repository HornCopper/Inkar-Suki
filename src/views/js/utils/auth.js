import Cookies from 'js-cookie'

const TokenKey = 'Admin-Token'

function getToken() {
  return Cookies.get(TokenKey)
}

function setToken(token) {
  return Cookies.set(TokenKey, token)
}

function removeToken() {
  return Cookies.remove(TokenKey)
}
