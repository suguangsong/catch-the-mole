/**
 * API请求工具函数
 */
import { getUserFingerprint } from './storage'

const API_BASE = '/api'

function getHeaders() {
  return {
    'Content-Type': 'application/json',
    'X-User-Fingerprint': getUserFingerprint()
  }
}

export async function createRoom(data) {
  const response = await fetch(`${API_BASE}/rooms`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data)
  })
  return response.json()
}

export async function getRoom(roomId) {
  const headers = getHeaders()
  const response = await fetch(`${API_BASE}/rooms/${roomId}`, {
    headers
  })
  if (!response.ok) {
    // 如果响应不成功，尝试解析 JSON，如果失败则返回错误对象
    try {
      return await response.json()
    } catch (e) {
      return {
        success: false,
        error: 'HTTP_ERROR',
        message: `请求失败: ${response.status} ${response.statusText}`
      }
    }
  }
  return response.json()
}

export async function startVoting(roomId) {
  const response = await fetch(`${API_BASE}/rooms/${roomId}/start`, {
    method: 'POST',
    headers: getHeaders()
  })
  return response.json()
}

export async function vote(roomId, playerIndex, username) {
  const response = await fetch(`${API_BASE}/rooms/${roomId}/vote`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({
      player_index: playerIndex,
      username: username || ''
    })
  })
  return response.json()
}

export async function resetVoting(roomId) {
  const response = await fetch(`${API_BASE}/rooms/${roomId}/reset`, {
    method: 'POST',
    headers: getHeaders()
  })
  return response.json()
}

export async function generatePlayerOrder(roomId) {
  const response = await fetch(`${API_BASE}/rooms/${roomId}/generate-order`, {
    method: 'POST',
    headers: getHeaders()
  })
  return response.json()
}
