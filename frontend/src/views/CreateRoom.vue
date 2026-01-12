<template>
  <div class="container">
    <h1>创建投票房间</h1>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>用户名</label>
        <input
          v-model="username"
          type="text"
          placeholder="请输入用户名"
          required
        />
      </div>
      <div class="form-group">
        <label>比赛编号</label>
        <input
          v-model="matchId"
          type="text"
          placeholder="请输入Dota2比赛ID"
          @input="handleMatchIdInput"
          required
        />
      </div>
      <div class="form-group">
        <label>房间密码</label>
        <div v-if="copySuccessMessage" class="success-message" style="margin-bottom: 10px; font-size: 14px;">
          {{ copySuccessMessage }}
        </div>
        <div class="password-input-wrapper">
          <input
            :value="roomPassword"
            :type="showPassword ? 'text' : 'password'"
            readonly
            class="password-input readonly"
          />
          <div class="password-actions">
            <button
              type="button"
              @click="generateRoomPassword"
              class="icon-button"
              title="重新生成"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 4 23 10 17 10"></polyline>
                <polyline points="1 20 1 14 7 14"></polyline>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
              </svg>
            </button>
            <button
              type="button"
              @click="togglePasswordVisibility"
              class="icon-button"
              title="显示/隐藏"
            >
              <svg v-if="showPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                <line x1="1" y1="1" x2="23" y2="23"></line>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                <circle cx="12" cy="12" r="3"></circle>
              </svg>
            </button>
            <button
              type="button"
              @click="copyPassword"
              class="icon-button"
              title="复制"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
      <div class="form-group">
        <label>最大投票人数</label>
        <input
          v-model.number="maxVotes"
          type="number"
          min="1"
          placeholder="5"
        />
      </div>
      <div class="form-group">
        <label>每人票数</label>
        <input
          v-model.number="votesPerUser"
          type="number"
          min="1"
          placeholder="1"
        />
      </div>
      <div class="form-group">
        <label style="display: flex; align-items: center; gap: 8px;">
          <input
            v-model="showOnlyWinnerVotes"
            type="checkbox"
            style="width: auto; margin: 0;"
          />
          <span>投票结束后只展示内鬼的得票数</span>
        </label>
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="loading" class="success-message" style="margin-bottom: 15px;">
        ⏳ 房间创建中，请稍候...
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? '创建中...' : '进入房间' }}
      </button>
      <button type="button" @click="goHome" class="btn-secondary" :disabled="loading">返回首页</button>
    </form>
  </div>
</template>

<script>
import { getUsername, setUsername } from '../utils/storage'
import { createRoom } from '../utils/api'

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

export default {
  name: 'CreateRoom',
  data() {
    return {
      username: '',
      matchId: '',
      roomPassword: generateUUID(),
      showPassword: false,
      maxVotes: 5,
      votesPerUser: 1,
      showOnlyWinnerVotes: true,
      error: '',
      loading: false,
      copySuccessMessage: ''
    }
  },
  mounted() {
    const savedUsername = getUsername()
    if (savedUsername) {
      this.username = savedUsername
    }
  },
  methods: {
    generateRoomPassword() {
      this.roomPassword = generateUUID()
    },
    togglePasswordVisibility() {
      this.showPassword = !this.showPassword
    },
    async copyPassword() {
      try {
        await navigator.clipboard.writeText(this.roomPassword)
        this.copySuccessMessage = '✅ 复制成功'
        setTimeout(() => {
          this.copySuccessMessage = ''
        }, 2000)
      } catch (err) {
        // 降级方案：使用传统方法
        const textArea = document.createElement('textarea')
        textArea.value = this.roomPassword
        textArea.style.position = 'fixed'
        textArea.style.opacity = '0'
        document.body.appendChild(textArea)
        textArea.select()
        try {
          document.execCommand('copy')
          this.copySuccessMessage = '✅ 复制成功'
          setTimeout(() => {
            this.copySuccessMessage = ''
          }, 2000)
        } catch (e) {
          // 复制失败
        }
        document.body.removeChild(textArea)
      }
    },
    handleMatchIdInput(event) {
      const value = event.target.value.replace(/\D/g, '')
      this.matchId = value
      event.target.value = value
    },
    async handleSubmit() {
      if (!this.username.trim()) {
        this.error = '请输入用户名'
        return
      }

      if (!this.matchId) {
        this.error = '请输入比赛ID'
        return
      }

      setUsername(this.username)
      this.error = ''
      this.loading = true

      try {
        const data = {
          match_id: parseInt(this.matchId),
          username: this.username,
          max_votes: this.maxVotes || 5,
          votes_per_user: this.votesPerUser || 1,
          show_only_winner_votes: this.showOnlyWinnerVotes !== false
        }

        data.room_password = this.roomPassword.trim()

        const result = await createRoom(data)

        if (result.success && result.data && result.data.room_password) {
          // 确保 room_password 存在后再跳转
          const roomPassword = result.data.room_password
          // 添加短暂延迟，确保后端房间创建完成
          await new Promise(resolve => setTimeout(resolve, 100))
          this.$router.push(`/room/${roomPassword}`)
        } else {
          // 显示详细的错误信息
          const errorMsg = result.message || '创建房间失败'
          if (result.error === 'ROOM_PASSWORD_EXISTS' || result.error === 'ROOM_ALREADY_EXISTS') {
            this.error = '该房间密码已被使用，请更换房间密码或重新生成'
          } else if (result.error === 'INVALID_MATCH_ID') {
            this.error = '无法获取比赛数据，请检查比赛ID是否正确'
          } else {
            this.error = errorMsg
          }
        }
      } catch (err) {
        console.error('创建房间失败:', err)
        this.error = '网络错误，请稍后重试'
      } finally {
        this.loading = false
      }
    },
    goHome() {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input {
  flex: 1;
  padding-right: 80px;
}

.password-input.readonly {
  background-color: #f5f5f5;
  cursor: default;
  width: 100%;
}

.password-actions {
  position: absolute;
  right: 8px;
  display: flex;
  gap: 4px;
  align-items: center;
}

.icon-button {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.3s;
}

.icon-button:hover {
  color: #0366d6;
}

.icon-button svg {
  display: block;
}
</style>
