<template>
  <footer class="footer">
    <p>开发者：凌晨四点钟 | 版本：1.0.0</p>
  </footer>
</template>

<script>
export default {
  name: 'Footer'
}
</script>

<style scoped>
.footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.9);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 14px;
  color: #666;
  z-index: 1000;
}

.footer p {
  margin: 0;
}
</style>
