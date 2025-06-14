<template>
  <div class="container">
    <div class="left-panel">
      <h1>Medical<br />Assistant RAG</h1>
    </div>
    <div class="right-panel">
      <div class="login-box">
        <h2>Login</h2>
        <form @submit.prevent="handleLogin">
          <input v-model="email" type="email" placeholder="Enter your email..." required />
          <button type="submit" :disabled="loading">
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>
          <p v-if="error" class="error">{{ error }}</p>
        </form>
        <p>Not registered? <router-link to="/register">Register now</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      email: '',
      error: null,
      loading: false
    }
  },
  methods: {
    async handleLogin() {
      this.error = null
      this.loading = true
      try {
        await this.$store.dispatch('login', { email: this.email })
        await this.$store.dispatch('init')
        this.$router.push('/chat/new')
      } catch (err) {
        this.error = err.message || 'Login failed'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.container {
  display: flex;
  height: 100vh;
  width: 100%;
}

.left-panel {
  background-color: #121212;
  color: white;
  width: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.left-panel h1 {
  font-size: 3rem;
  font-weight: bold;
  text-align: center;
  line-height: 1.3;
}

.right-panel {
  background-color: #2c2c2c;
  width: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-box {
  background-color: #ffffff;
  padding: 2rem;
  border-radius: 10px;
  width: 100%;
  max-width: 320px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  
}

.login-box h2 {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
}

.login-box input[type="email"] {

  padding: 0.8rem;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
}

.login-box button {
  width: 100%;
  padding: 0.8rem;
  font-size: 1rem;
  background-color: #4a48ff;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.login-box button:hover:not(:disabled) {
  background-color: #3735d0;
}

.login-box button:disabled {
  background-color: #888;
  cursor: not-allowed;
}

.login-box p {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #333;
}

.login-box .error {
  color: red;
  margin-top: 0.5rem;
}

.login-box a {
  color: #4a48ff;
  text-decoration: none;
}

.login-box a:hover {
  text-decoration: underline;
}
</style>
