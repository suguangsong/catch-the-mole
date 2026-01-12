<template>
  <div class="app-wrapper">
    <router-view />
    <Footer />
  </div>
</template>

<script>
import Footer from './components/Footer.vue'

export default {
  name: 'App',
  components: {
    Footer
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  overflow-x: hidden;
  overflow-y: auto;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #333;
  margin: 0;
  padding: 0;
}

#app {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  padding-bottom: 70px;
  box-sizing: border-box;
}

.app-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: calc(100vh - 90px);
}

.container {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 100%;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #667eea;
  font-size: 2.5em;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
  color: #764ba2;
  font-size: 1.5em;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #667eea;
}

button {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-top: 10px;
}

button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

button:active {
  transform: translateY(0);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: #6c757d;
  margin-top: 10px;
}

.error-message {
  color: #dc3545;
  margin-top: 10px;
  padding: 10px;
  background: #f8d7da;
  border-radius: 6px;
  border: 1px solid #f5c6cb;
}

.success-message {
  color: #155724;
  margin-top: 10px;
  padding: 10px;
  background: #d4edda;
  border-radius: 6px;
  border: 1px solid #c3e6cb;
}

.heroes-list {
  list-style: none;
  margin: 20px 0;
}

.hero-item {
  padding: 12px;
  margin: 8px 0;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #667eea;
}

.hero-item.voted {
  opacity: 0.6;
  background: #e9ecef;
}

.vote-progress {
  text-align: center;
  margin: 20px 0;
  font-size: 18px;
  color: #667eea;
  font-weight: 600;
}

.results {
  margin-top: 30px;
}

.result-item {
  padding: 15px;
  margin: 10px 0;
  background: #f8f9fa;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-item.winner {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  font-weight: 600;
  font-size: 1.1em;
}

.animation-fade-in {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animation-blink {
  animation: blink 1s ease-in-out 3;
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}
</style>
