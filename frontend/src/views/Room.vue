<template>
  <div class="container">
    <h1>投票房间</h1>

    <!-- 加载中状态 -->
    <div v-if="!roomStatus && !error" style="text-align: center; padding: 40px;">
      <p>正在加载房间信息...</p>
    </div>

    <!-- 错误状态 -->
    <div v-if="error && !roomStatus" class="error-message" style="margin: 20px 0;">
      {{ error }}
      <div style="margin-top: 20px;">
        <button @click="loadRoomInfo" class="btn-secondary">重试</button>
        <button @click="goHome" class="btn-secondary" style="margin-left: 10px;">返回首页</button>
      </div>
    </div>

    <!-- 未开始投票状态 -->
    <div v-if="roomStatus === 'init'">
      <div class="form-group">
        <p><strong>房间 ID：</strong>{{ roomId }}</p>
        <p><strong>比赛 ID：</strong>{{ matchId }}</p>
        <p><strong>房间创建者：</strong>{{ creatorUsername }}</p>
      </div>
      <h2>失败方玩家：</h2>
      <ul class="heroes-list">
        <li v-for="(hero, index) in heroes" :key="index" class="hero-item">
          {{ index + 1 }}. {{ hero.nickname }} - {{ hero.hero_name }}
        </li>
      </ul>
      <div v-if="!isCreator" style="margin: 20px 0; padding: 15px; background: #fff3cd; border-radius: 6px; border: 1px solid #ffc107;">
        <p style="margin: 0; color: #856404;">等待房间创建者开始投票...</p>
      </div>
      <button
        v-if="isCreator"
        @click="handleStartVoting"
        :disabled="loading"
      >
        开始投票
      </button>
      <div v-if="error" class="error-message">{{ error }}</div>
      <button @click="goHome" class="btn-secondary">返回首页</button>
    </div>

    <!-- 投票中状态 -->
    <div v-if="roomStatus === 'voting'">
      <div class="form-group" style="margin-bottom: 20px;">
        <p><strong>房间 ID：</strong>{{ roomId }}</p>
        <p><strong>比赛 ID：</strong>{{ matchId }}</p>
      </div>
      <div v-if="userRemainingVotes > 0">
        <h2>请进行第 {{ userVotedCount + 1 }} 次投票（共需投 {{ votesPerUser }} 票）</h2>
        <p style="text-align: center; margin: 20px 0; font-size: 18px;">
          请在键盘输入 1 - 5 进行投票
        </p>
      </div>
      <div v-else>
        <div class="success-message">✅ 你已完成投票</div>
      </div>

      <h2>失败方玩家列表：</h2>
      <ul class="heroes-list">
        <li
          v-for="(hero, index) in heroes"
          :key="index"
          class="hero-item"
        >
          {{ index + 1 }}. {{ hero.nickname }} - {{ hero.hero_name }}
        </li>
      </ul>

      <div v-if="votedUsernames.length > 0" style="margin: 20px 0;">
        <strong>已投票用户：</strong>{{ votedUsernames.join('、') }}
      </div>

      <div v-if="voteMessage" :class="voteMessageType === 'success' ? 'success-message' : 'error-message'">
        {{ voteMessage }}
      </div>

      <div class="vote-progress">
        当前投票进度：{{ currentVotes }} / {{ maxVotes }}
      </div>

      <button @click="goHome" class="btn-secondary">返回首页</button>
    </div>

    <!-- 投票完成状态 -->
    <div v-if="roomStatus === 'finished'" class="animation-fade-in">
      <div class="form-group" style="margin-bottom: 20px;">
        <p><strong>房间 ID：</strong>{{ roomId }}</p>
        <p><strong>比赛 ID：</strong>{{ matchId }}</p>
      </div>
      <h2 class="animation-blink">🎉 投票已结束</h2>
      <h2>投票结果：</h2>
      <div class="results">
        <div
          v-for="(hero, index) in heroes"
          :key="index"
          class="result-item"
          :class="{ winner: isWinner(index + 1) }"
        >
          <span>{{ hero.nickname }}（{{ hero.hero_name }}）</span>
          <span v-if="showOnlyWinnerVotes">
            <strong v-if="isWinner(index + 1)">{{ votes[index + 1] || 0 }} 票</strong>
            <strong v-else style="opacity: 0.3;">--</strong>
          </span>
          <span v-else>
            <strong>{{ votes[index + 1] || 0 }} 票</strong>
          </span>
        </div>
      </div>
      <h2 style="margin-top: 30px; color: #dc3545;">
        <span v-if="winnerNames.length === 1">🐭 内鬼是：{{ winnerNames[0] }}</span>
        <span v-else>🐭 内鬼是（并列）：{{ winnerNames.join('、') }}</span>
      </h2>
      <button @click="goHome" class="btn-secondary" style="margin-top: 20px;">返回首页</button>
    </div>
  </div>
</template>

<script>
import { getUserFingerprint, getUsername } from '../utils/storage'
import { getRoom, startVoting, vote } from '../utils/api'

export default {
  name: 'Room',
  data() {
    return {
      roomId: '',
      matchId: '',
      roomStatus: '',
      creatorUsername: '',
      creatorFingerprint: '',
      heroes: [],
      maxVotes: 5,
      votesPerUser: 1,
      currentVotes: 0,
      votes: {},
      userVotedPlayers: [],
      userRemainingVotes: 0,
      votedUsernames: [],
      voteMessage: '',
      voteMessageType: '',
      loading: false,
      error: '',
      pollInterval: null,
      showOnlyWinnerVotes: true
    }
  },
  computed: {
    isCreator() {
      return this.creatorFingerprint === getUserFingerprint()
    },
    userVotedCount() {
      return this.userVotedPlayers.length
    },
    winnerName() {
      if (!this.votes || Object.keys(this.votes).length === 0) {
        return ''
      }
      let maxVotes = 0
      const winnerIndexes = []
      for (const [index, voteCount] of Object.entries(this.votes)) {
        const count = parseInt(voteCount)
        if (count > maxVotes) {
          maxVotes = count
          winnerIndexes.length = 0
          winnerIndexes.push(parseInt(index))
        } else if (count === maxVotes && maxVotes > 0) {
          winnerIndexes.push(parseInt(index))
        }
      }
      if (winnerIndexes.length > 0) {
        const winnerNames = winnerIndexes.map(index => {
          const winnerHero = this.heroes[index - 1]
          return winnerHero ? winnerHero.nickname : `玩家${index}`
        })
        return winnerNames.join('、')
      }
      return ''
    },
    winnerNames() {
      if (!this.votes || Object.keys(this.votes).length === 0) {
        return []
      }
      let maxVotes = 0
      const winnerIndexes = []
      for (const [index, voteCount] of Object.entries(this.votes)) {
        const count = parseInt(voteCount)
        if (count > maxVotes) {
          maxVotes = count
          winnerIndexes.length = 0
          winnerIndexes.push(parseInt(index))
        } else if (count === maxVotes && maxVotes > 0) {
          winnerIndexes.push(parseInt(index))
        }
      }
      if (winnerIndexes.length > 0) {
        return winnerIndexes.map(index => {
          const winnerHero = this.heroes[index - 1]
          return winnerHero ? winnerHero.nickname : `玩家${index}`
        })
      }
      return []
    }
  },
  watch: {
    // 监听路由参数变化，当 room_id 变化时重新加载数据
    '$route.params.room_id': {
      handler(newRoomId) {
        if (newRoomId) {
          // 检查是否设置了用户名，如果没有则重定向到首页
          const username = getUsername()
          if (!username || !username.trim()) {
            this.$router.push('/')
            return
          }
          this.roomId = newRoomId
          this.error = ''
          this.loadRoomInfo()
        }
      },
      immediate: true
    }
  },
  mounted() {
    // 检查是否设置了用户名，如果没有则重定向到首页
    const username = getUsername()
    if (!username || !username.trim()) {
      this.$router.push('/')
      return
    }
    // 如果路由参数存在，确保 roomId 已设置（watch 会处理加载）
    if (!this.roomId && this.$route.params.room_id) {
      this.roomId = this.$route.params.room_id
    }
    if (this.roomId) {
      this.setupKeyboardListener()
      this.startPolling()
    } else {
      this.error = '房间 ID 不能为空'
    }
  },
  beforeUnmount() {
    this.removeKeyboardListener()
    this.stopPolling()
  },
  methods: {
    async loadRoomInfo() {
      if (!this.roomId) {
        this.error = '房间 ID 不能为空'
        return
      }

      this.error = ''
      try {
        const result = await getRoom(this.roomId)
        if (result.success && result.data) {
          const data = result.data
          this.matchId = data.match_id
          this.roomStatus = data.status
          this.creatorUsername = data.creator_username
          this.heroes = data.heroes || []
          this.maxVotes = data.max_votes
          this.votesPerUser = data.votes_per_user
          this.currentVotes = data.current_votes
          this.creatorFingerprint = data.creator_fingerprint || ''
          this.showOnlyWinnerVotes = data.show_only_winner_votes !== false

          if (data.status === 'finished') {
            this.votes = data.votes || {}
            this.stopPolling()
          } else if (data.status === 'voting') {
            this.userVotedPlayers = data.user_voted_players || []
            this.userRemainingVotes = this.votesPerUser - this.userVotedPlayers.length
            this.votedUsernames = data.voted_usernames || []
            // 如果状态变为 voting，确保轮询已启动
            if (!this.pollInterval) {
              this.startPolling()
            }
          }
        } else {
          const errorMsg = result.message || '加载房间信息失败'
          if (result.error === 'ROOM_NOT_FOUND' || result.error === 'SERVER_ERROR' || result.error === 'HTTP_ERROR') {
            // 房间不存在或服务器错误，重定向到首页
            this.$router.push('/')
            return
          } else {
            this.error = errorMsg
            this.roomStatus = null
          }
        }
      } catch (err) {
        console.error('加载房间信息失败:', err)
        // 如果是网络错误或服务器错误，重定向到首页
        this.$router.push('/')
      }
    },
    async handleStartVoting() {
      if (!this.roomId) {
        this.error = '房间 ID 不能为空'
        return
      }

      this.loading = true
      this.error = ''
      try {
        const result = await startVoting(this.roomId)
        if (result.success) {
          // 开始投票成功后，重新加载房间信息
          await this.loadRoomInfo()
        } else {
          // 显示错误信息
          const errorMsg = result.message || '开始投票失败'
          if (result.error === 'ROOM_NOT_FOUND') {
            this.error = `房间不存在（房间 ID: ${this.roomId}）`
          } else if (result.error === 'PERMISSION_DENIED') {
            this.error = '只有房间创建者可以开始投票'
          } else {
            this.error = errorMsg
          }
        }
      } catch (err) {
        console.error('开始投票失败:', err)
        this.error = '网络错误，请检查网络连接后重试'
      } finally {
        this.loading = false
      }
    },
    async handleVote(playerIndex) {
      if (this.userRemainingVotes <= 0) {
        return
      }

      if (this.userVotedPlayers.includes(playerIndex)) {
        this.voteMessage = '不能重复投票给同一玩家'
        this.voteMessageType = 'error'
        setTimeout(() => {
          this.voteMessage = ''
        }, 3000)
        return
      }

      try {
        const username = getUsername()
        const result = await vote(this.roomId, playerIndex, username)
        if (result.success) {
          const data = result.data
          this.userVotedPlayers = data.user_voted_players || []
          this.userRemainingVotes = data.user_remaining_votes || 0
          this.currentVotes = data.current_votes
          await this.loadRoomInfo()

          if (data.finished) {
            this.voteMessage = '✅ 投票成功，投票已结束'
            this.voteMessageType = 'success'
            setTimeout(async () => {
              await this.loadRoomInfo()
            }, 1000)
          } else {
            this.voteMessage = '✅ 投票成功'
            if (this.userRemainingVotes > 0) {
              this.voteMessage += `，还需投 ${this.userRemainingVotes} 票`
            }
            this.voteMessageType = 'success'
            setTimeout(() => {
              this.voteMessage = ''
            }, 3000)
          }
        } else {
          this.voteMessage = result.message || '投票失败'
          this.voteMessageType = 'error'
          setTimeout(() => {
            this.voteMessage = ''
          }, 3000)
        }
      } catch (err) {
        this.voteMessage = '网络错误，请稍后重试'
        this.voteMessageType = 'error'
        setTimeout(() => {
          this.voteMessage = ''
        }, 3000)
      }
    },
    setupKeyboardListener() {
      document.addEventListener('keydown', this.onKeyDown)
    },
    removeKeyboardListener() {
      document.removeEventListener('keydown', this.onKeyDown)
    },
    onKeyDown(event) {
      if (this.roomStatus !== 'voting' || this.userRemainingVotes <= 0) {
        return
      }

      const key = event.key
      const playerIndex = parseInt(key)

      if (playerIndex >= 1 && playerIndex <= 5) {
        this.handleVote(playerIndex)
      }
    },
    startPolling() {
      this.pollInterval = setInterval(() => {
        if (this.roomStatus === 'voting') {
          this.loadRoomInfo()
        }
      }, 2000)
    },
    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },
    isWinner(playerIndex) {
      if (!this.votes || Object.keys(this.votes).length === 0) {
        return false
      }
      const maxVotes = Math.max(...Object.values(this.votes))
      return this.votes[playerIndex] === maxVotes && maxVotes > 0
    },
    goHome() {
      this.$router.push('/')
    }
  }
}
</script>
