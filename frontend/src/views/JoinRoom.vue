<template>
  <div class="container">
    <h1>加入投票房间</h1>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>用户名（必填）</label>
        <input
          v-model="username"
          type="text"
          placeholder="请输入用户名"
          required
        />
      </div>
      <div class="form-group">
        <label>请输入房间密码</label>
        <input
          v-model="roomPassword"
          type="password"
          placeholder="请输入房间密码"
          required
        />
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>
      <button type="submit" :disabled="loading">进入房间</button>
      <button type="button" @click="goHome" class="btn-secondary">返回首页</button>
    </form>
  </div>
</template>

<script>
import { getUsername, setUsername } from '../utils/storage'
import { getRoom } from '../utils/api'

export default {
  name: 'JoinRoom',
  data() {
    return {
      username: '',
      roomPassword: '',
      error: '',
      loading: false
    }
  },
  mounted() {
    const savedUsername = getUsername()
    if (savedUsername) {
      this.username = savedUsername
    }
  },
  methods: {
    async handleSubmit() {
      if (!this.username.trim()) {
        this.error = '请输入用户名'
        return
      }

      if (!this.roomPassword.trim()) {
        this.error = '请输入房间密码'
        return
      }

      setUsername(this.username)
      this.error = ''
      this.loading = true

      try {
        const result = await getRoom(this.roomPassword.trim())

        if (result.success) {
          if (result.data.status === 'finished') {
            this.error = '该房间投票已结束'
          } else {
            this.$router.push(`/room/${this.roomPassword.trim()}`)
          }
        } else {
          if (result.error === 'ROOM_NOT_FOUND') {
            this.error = '房间不存在，请检查房间密码是否正确'
          } else {
            this.error = result.message || '加入房间失败'
          }
        }
      } catch (err) {
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
