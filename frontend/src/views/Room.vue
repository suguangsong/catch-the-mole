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

    <!-- 房间信息（所有状态共用） -->
    <div class="room-info-section">
      <div class="form-group">
        <p><strong>房间 ID：</strong>{{ displayRoomId }}</p>
        <p><strong>比赛 ID：</strong>{{ matchId }}</p>
        <p v-if="roomStatus === 'init'"><strong>房间创建者：</strong>{{ creatorUsername }}</p>
        <div v-if="isCreator" style="margin-top: 15px;">
          <button
            @click="handleGenerateOrder"
            :disabled="loading"
            class="btn-secondary"
            style="background-color: #28a745; color: white;"
          >
            随机生成发言或BP顺序
          </button>
        </div>
        <div v-if="playerOrder && playerOrder.length > 0" style="margin-top: 15px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
          <h3 style="margin-top: 0; margin-bottom: 10px; font-size: 16px;">
            发言或BP顺序
            <span v-if="orderGenerationCount > 0" style="font-size: 14px; color: #666; font-weight: normal;">
              （第{{ orderGenerationCount }}次生成）
            </span>
          </h3>
          <ol style="margin: 0; padding-left: 20px;">
            <li v-for="(orderIndex, idx) in playerOrder" :key="idx" style="margin-bottom: 5px;">
              {{ getHeroNameByIndex(orderIndex) }}
            </li>
          </ol>
        </div>
        <div class="password-display-wrapper" style="margin-top: 10px;">
          <label>房间密码：</label>
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
                @click="togglePasswordVisibility"
                class="icon-button"
                title="显示/隐藏密码"
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
                @click="copyRoomPassword"
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
      </div>
    </div>

    <!-- 未开始投票状态 -->
    <div v-if="roomStatus === 'init' && !userStartedVoting">
      <h2>失败方玩家：</h2>
      <ul class="heroes-list">
        <li v-for="(hero, index) in heroes" :key="index" class="hero-item">
          {{ index + 1 }}. {{ hero.nickname }} - {{ hero.hero_name }}
        </li>
      </ul>
      <button
        @click="handleStartVoting"
        :disabled="loading"
      >
        开始投票
      </button>
      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="isCreator" style="margin-top: 20px;">
        <button
          @click="handleResetVoting"
          :disabled="loading"
          class="btn-secondary"
          style="background-color: #dc3545; color: white;"
        >
          重置投票
        </button>
      </div>
      <button @click="goHome" class="btn-secondary">返回首页</button>
    </div>

    <!-- 投票中状态 -->
    <div v-if="(roomStatus === 'voting' || (roomStatus === 'init' && userStartedVoting))">
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

      <div v-if="isCreator" style="margin-top: 20px;">
        <button
          @click="handleResetVoting"
          :disabled="loading"
          class="btn-secondary"
          style="background-color: #dc3545; color: white;"
        >
          重置投票
        </button>
      </div>

      <button @click="goHome" class="btn-secondary">返回首页</button>
    </div>

    <!-- 投票完成状态 -->
    <div v-if="roomStatus === 'finished'" class="animation-fade-in">
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
      <div v-if="isCreator" style="margin-top: 20px;">
        <button
          @click="handleResetVoting"
          :disabled="loading"
          class="btn-secondary"
          style="background-color: #dc3545; color: white;"
        >
          重置投票
        </button>
      </div>
      <button @click="goHome" class="btn-secondary" style="margin-top: 20px;">返回首页</button>
    </div>
  </div>
</template>

<script>
import { getUserFingerprint, getUsername } from '../utils/storage'
import { getRoom, startVoting, vote, resetVoting, generatePlayerOrder } from '../utils/api'

export default {
  name: 'Room',
  data() {
    return {
      roomId: '',
      roomPassword: '',
      displayRoomId: '',
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
      userStartedVoting: false,
      voteMessage: '',
      voteMessageType: '',
      loading: false,
      error: '',
      pollInterval: null,
      showOnlyWinnerVotes: true,
      showPassword: false,
      copySuccessMessage: '',
      playerOrder: null,
      orderGenerationCount: 0,
      pollCount: 0
    }
  },
  computed: {
    isCreator() {
      const creatorFp = String(this.creatorFingerprint || '').trim()
      const userFp = String(getUserFingerprint() || '').trim()
      if (!creatorFp || !userFp) {
        return false
      }
      return creatorFp === userFp
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
      handler(newRoomPassword) {
        if (newRoomPassword) {
          // 检查是否设置了用户名，如果没有则重定向到首页
          const username = getUsername()
          if (!username || !username.trim()) {
            this.$router.push('/')
            return
          }
          this.roomPassword = newRoomPassword
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
    // 如果路由参数存在，确保 roomPassword 已设置（watch 会处理加载）
    if (!this.roomPassword && this.$route.params.room_id) {
      this.roomPassword = this.$route.params.room_id
    }
    if (this.roomPassword) {
      this.setupKeyboardListener()
      this.startPolling()
    } else {
      this.error = '房间密码不能为空'
    }
  },
  beforeUnmount() {
    this.removeKeyboardListener()
    this.stopPolling()
  },
  methods: {
    async loadRoomInfo() {
      if (!this.roomPassword) {
        this.error = '房间密码不能为空'
        return
      }

      this.error = ''
      try {
        const result = await getRoom(this.roomPassword)
        if (result.success && result.data) {
          const data = result.data
          this.roomId = data.room_id || ''
          this.displayRoomId = data.room_id || ''
          this.roomPassword = data.room_password || this.roomPassword
          this.matchId = data.match_id
          this.roomStatus = data.status
          this.creatorUsername = data.creator_username
          this.heroes = data.heroes || []
          this.maxVotes = data.max_votes
          this.votesPerUser = data.votes_per_user
          this.currentVotes = data.current_votes
          this.creatorFingerprint = data.creator_fingerprint || ''
          this.showOnlyWinnerVotes = data.show_only_winner_votes !== false
          this.playerOrder = data.player_order || null
          this.orderGenerationCount = data.order_generation_count || 0

          if (data.status === 'finished') {
            this.votes = data.votes || {}
            // 投票结束后不停止轮询，以便检测重置投票后的状态变化
            // 轮询会继续运行，但只在状态不是 finished 时加载信息
          } else {
            // init 和 voting 状态都显示投票界面
            this.userVotedPlayers = data.user_voted_players || []
            this.userRemainingVotes = this.votesPerUser - this.userVotedPlayers.length
            this.votedUsernames = data.voted_usernames || []
            this.userStartedVoting = data.user_started_voting || false
            // 确保轮询已启动（包括从 finished 状态恢复的情况）
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
      if (!this.roomPassword) {
        this.error = '房间密码不能为空'
        return
      }

      if (this.userStartedVoting) {
        return
      }

      this.loading = true
      this.error = ''
      try {
        const result = await startVoting(this.roomPassword)
        if (result.success) {
          // 开始投票成功后，更新本地状态并重新加载房间信息
          this.userStartedVoting = true
          await this.loadRoomInfo()
        } else {
          // 显示错误信息
          const errorMsg = result.message || '开始投票失败'
          if (result.error === 'ROOM_NOT_FOUND') {
            this.error = '房间不存在'
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
      if (!this.userStartedVoting) {
        this.voteMessage = '请先点击开始投票'
        this.voteMessageType = 'error'
        setTimeout(() => {
          this.voteMessage = ''
        }, 3000)
        return
      }

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
        const result = await vote(this.roomPassword, playerIndex, username)
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
      if (!this.userStartedVoting || this.userRemainingVotes <= 0) {
        return
      }

      const key = event.key
      const playerIndex = parseInt(key)

      if (playerIndex >= 1 && playerIndex <= 5) {
        this.handleVote(playerIndex)
      }
    },
    startPolling() {
      // 如果轮询已经在运行，先停止
      if (this.pollInterval) {
        this.stopPolling()
      }
      this.pollCount = 0
      this.pollInterval = setInterval(() => {
        // 如果状态是 finished，降低轮询频率（每5次轮询检查一次，即10秒）
        // 这样可以检测到从 finished 状态恢复到 init 状态的情况
        if (this.roomStatus === 'finished') {
          this.pollCount++
          if (this.pollCount >= 5) {
            this.pollCount = 0
            this.loadRoomInfo()
          }
        } else {
          // 非 finished 状态正常轮询（每2秒）
          this.pollCount = 0
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
    togglePasswordVisibility() {
      this.showPassword = !this.showPassword
    },
    async copyRoomPassword() {
      try {
        await navigator.clipboard.writeText(this.roomPassword)
        this.copySuccessMessage = '✅ 复制成功'
        setTimeout(() => {
          this.copySuccessMessage = ''
        }, 2000)
      } catch (err) {
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
    async handleResetVoting() {
      if (!this.isCreator) {
        this.error = '只有房主可以重置投票'
        return
      }

      if (!this.roomPassword) {
        this.error = '房间密码不能为空'
        return
      }

      if (!confirm('确定要重置投票吗？这将清除所有投票状态，所有人的页面将恢复到刚进入房间时的状态。')) {
        return
      }

      this.loading = true
      this.error = ''
      try {
        const result = await resetVoting(this.roomPassword)
        if (result.success) {
          // 重置成功后重新加载房间信息
          await this.loadRoomInfo()
          this.voteMessage = '✅ 投票已重置'
          this.voteMessageType = 'success'
          setTimeout(() => {
            this.voteMessage = ''
          }, 3000)
        } else {
          const errorMsg = result.message || '重置投票失败'
          if (result.error === 'UNAUTHORIZED') {
            this.error = '只有房主可以重置投票'
          } else {
            this.error = errorMsg
          }
        }
      } catch (err) {
        console.error('重置投票失败:', err)
        this.error = '网络错误，请稍后重试'
      } finally {
        this.loading = false
      }
    },
    async handleGenerateOrder() {
      if (!this.isCreator) {
        this.error = '只有房主可以生成排序'
        return
      }

      if (!this.roomPassword) {
        this.error = '房间密码不能为空'
        return
      }

      this.loading = true
      this.error = ''
      try {
        const result = await generatePlayerOrder(this.roomPassword)
        if (result.success) {
          // 生成成功后重新加载房间信息以获取最新排序
          await this.loadRoomInfo()
          this.voteMessage = '✅ 排序已生成'
          this.voteMessageType = 'success'
          setTimeout(() => {
            this.voteMessage = ''
          }, 3000)
        } else {
          const errorMsg = result.message || '生成排序失败'
          if (result.error === 'UNAUTHORIZED') {
            this.error = '只有房主可以生成排序'
          } else {
            this.error = errorMsg
          }
        }
      } catch (err) {
        console.error('生成排序失败:', err)
        this.error = '网络错误，请稍后重试'
      } finally {
        this.loading = false
      }
    },
    getHeroNameByIndex(index) {
      if (!this.heroes || this.heroes.length === 0) {
        return `玩家${index}`
      }
      const hero = this.heroes[index - 1]
      if (hero) {
        return `${index}. ${hero.nickname} - ${hero.hero_name}`
      }
      return `玩家${index}`
    },
    goHome() {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 600px;
  width: 100%;
  box-sizing: border-box;
}

.room-info-section {
  margin-bottom: 20px;
}

.password-display-wrapper {
  margin-top: 10px;
}

.password-display-wrapper label {
  display: block;
  margin-bottom: 5px;
  font-weight: normal;
}

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input.readonly {
  background-color: #f5f5f5;
  cursor: default;
  flex: 1;
  padding-right: 80px;
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
