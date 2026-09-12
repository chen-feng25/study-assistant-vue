<template>
  <div class="login-page">
    <div class="login-card">
      <MatchaLogo :size="44" />
      <h1 class="serif">学习档案助理</h1>
      <form @submit.prevent="submit">
        <input v-model="username" class="form-input" placeholder="用户名" />
        <input v-model="password" class="form-input" type="password" placeholder="密码" />
        <input v-if="mode==='register'" v-model="confirm" class="form-input" type="password" placeholder="确认密码" />
        <button type="submit" class="login-btn" :disabled="loading">{{ mode === 'login' ? '登录' : '注册' }}</button>
      </form>
      <div v-if="error" class="login-error">{{ error }}</div>
      <div class="link-text" @click="toggleMode">{{ mode === 'login' ? '没有账号？去注册 →' : '← 已有账号？去登录' }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import MatchaLogo from '../components/MatchaLogo.vue'

const router = useRouter()
const mode = ref('login')
const username = ref('')
const password = ref('')
const confirm = ref('')
const loading = ref(false)
const error = ref('')

function toggleMode() { mode.value = mode.value === 'login' ? 'register' : 'login'; error.value = '' }

async function submit() {
  if (!username.value || !password.value) { error.value = '请填写用户名和密码'; return }
  if (mode.value === 'register' && password.value !== confirm.value) { error.value = '两次密码不一致'; return }
  loading.value = true; error.value = ''
  try {
    const fn = mode.value === 'login' ? api.login : api.register
    const data = await fn(username.value, password.value)
    if (data.ok) {
      sessionStorage.setItem('userId', data.user_id)
      sessionStorage.setItem('username', data.username || username.value)
      router.push('/entry')
    } else {
      error.value = data.error || '操作失败'
    }
  } catch (e) { error.value = e.message } finally { loading.value = false }
}
</script>

<style scoped>
.login-page { display: flex; align-items: center; justify-content: center; min-height: 100vh; position: relative; z-index: 1; }
.login-card { background: var(--card-bg); border-radius: 14px; padding: 34px 28px; border: 1px solid var(--card-border); width: 340px; text-align: center; box-shadow: 0 4px 24px var(--shadow); animation: heroUp 0.6s ease-out; }
.login-card h1 { font-size: 1.3rem; color: var(--title); margin: 10px 0 20px; }
.form-input { padding: 10px 14px; border-radius: 8px; border: 1.5px solid #d8e6d0; background: white; font-size: 0.82rem; color: var(--text); outline: none; font-family: inherit; width: 100%; margin-bottom: 10px; transition: border-color 0.25s; display: block; box-sizing: border-box; }
.form-input:focus { border-color: var(--matcha); box-shadow: 0 0 0 3px rgba(138,184,96,0.1); }
.login-btn { padding: 10px 0; border-radius: 10px; border: none; cursor: pointer; background: linear-gradient(135deg, var(--tea), var(--matcha)); color: #fff; font-weight: 600; font-size: 0.85rem; font-family: inherit; width: 100%; transition: all 0.25s; margin-top: 4px; }
.login-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(106,154,64,0.25); }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.login-error { color: #d04040; font-size: 0.78rem; margin-top: 10px; }
.link-text { font-size: 0.72rem; color: var(--muted); margin-top: 14px; cursor: pointer; }
.link-text:hover { color: var(--tea); }

@media (max-width: 767px) {
  .login-card { width: 100%; max-width: 340px; padding: 28px 22px; }
}
</style>
