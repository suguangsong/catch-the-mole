<template>
  <div class="container">
    <h1>抓畜</h1>
    <h2>谁是内鬼？</h2>
    <button @click="goToCreate">创建投票房间</button>
    <button @click="goToJoin" class="btn-secondary">加入投票房间</button>
  </div>
</template>

<script>
export default {
  name: 'Home',
  methods: {
    goToCreate() {
      this.$router.push('/create')
    },
    goToJoin() {
      this.$router.push('/join')
    }
  }
}
</script>
