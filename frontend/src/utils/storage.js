/**
 * LocalStorage工具函数
 */

export function getUsername() {
  return localStorage.getItem('username') || ''
}

export function setUsername(username) {
  localStorage.setItem('username', username)
}

export function getUserFingerprint() {
  let fingerprint = localStorage.getItem('user_fingerprint')
  if (!fingerprint) {
    fingerprint = generateUUID()
    localStorage.setItem('user_fingerprint', fingerprint)
  }
  return fingerprint
}

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}
