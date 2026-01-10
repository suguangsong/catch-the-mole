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
        <label>房间 ID（可自定义）</label>
        <input
          v-model="roomId"
          type="text"
          placeholder="留空将自动生成"
        />
        <button
          type="button"
          @click="generateRoomId"
          style="margin-top: 8px; padding: 8px 16px; font-size: 14px; width: auto;"
          class="btn-secondary"
        >
          重新生成房间ID
        </button>
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
      roomId: generateUUID(),
      maxVotes: 5,
      votesPerUser: 1,
      showOnlyWinnerVotes: true,
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
    generateRoomId() {
      this.roomId = generateUUID()
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

        if (this.roomId.trim()) {
          data.room_id = this.roomId.trim()
        }

        const result = await createRoom(data)

        if (result.success && result.data && result.data.room_id) {
          // 确保 room_id 存在后再跳转
          const roomId = result.data.room_id
          // 添加短暂延迟，确保后端房间创建完成
          await new Promise(resolve => setTimeout(resolve, 100))
          this.$router.push(`/room/${roomId}`)
        } else {
          // 显示详细的错误信息
          const errorMsg = result.message || '创建房间失败'
          if (result.error === 'ROOM_ALREADY_EXISTS') {
            this.error = '该房间 ID 已被使用，请更换房间 ID 或重新生成'
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
