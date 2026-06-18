<template>
  <div class="chat-page">
    <PageHeader title="AI 智能问答" />
    <div class="chat-area">
      <div v-for="(m, i) in messages" :key="i" class="chat-msg" :class="m.role">{{ m.content }}</div>
      <div v-if="loading" class="chat-msg ai">思考中...</div>
      <div v-if="error" class="err">{{ error }}</div>
    </div>
    <form class="chat-input-row" @submit.prevent="send">
      <input v-model="input" class="form-input" placeholder="输入你的问题……" />
      <button class="btn" :disabled="loading || !input.trim()">发送</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { api } from '../api'
import PageHeader from '../components/PageHeader.vue'

const input = ref('')
const messages = ref([])
const loading = ref(false)
const error = ref('')

async function send() {
  const msg = input.value.trim()
  if (!msg) return
  messages.value.push({ role: 'user', content: msg })
  input.value = ''
  loading.value = true; error.value = ''
  try {
    const data = await api.chat(msg, messages.value.slice(0, -1))
    messages.value.push({ role: 'ai', content: data.reply || '抱歉，没有回复' })
  } catch (e) { error.value = e.message } finally { loading.value = false }
}
</script>

<style scoped>
.chat-page { position: relative; z-index: 1; display: flex; flex-direction: column; flex: 1; }
.chat-area { flex: 1; display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px; overflow-y: auto; }
.chat-msg { padding: 10px 14px; border-radius: 10px; font-size: 0.78rem; max-width: 80%; line-height: 1.6; white-space: pre-wrap; }
.chat-msg.user { background: rgba(138,184,96,0.1); align-self: flex-end; color: var(--text); }
.chat-msg.ai { background: var(--card-bg); border: 1px solid var(--card-border); align-self: flex-start; color: var(--text); }
.chat-input-row { display: flex; gap: 8px; }
.form-input { flex: 1; padding: 10px 14px; border-radius: 10px; border: 1.5px solid #d8e6d0; background: var(--card-bg); font-size: 0.82rem; color: var(--text); outline: none; font-family: inherit; transition: border-color 0.25s; }
.form-input:focus { border-color: var(--matcha); box-shadow: 0 0 0 3px rgba(138,184,96,0.1); }
.btn { padding: 10px 24px; border-radius: 10px; border: none; cursor: pointer; background: linear-gradient(135deg, var(--tea), var(--matcha)); color: #fff; font-weight: 600; font-size: 0.82rem; font-family: inherit; transition: all 0.25s; flex-shrink: 0; }
.btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(106,154,64,0.25); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.err { color: #d04040; font-size: 0.78rem; padding: 6px 12px; }
</style>
