<template>
  <div class="settings-page">
    <PageHeader title="设置" />

    <div class="settings-card">
      <div class="setting-title">
        <svg class="setting-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        <span>DeepSeek API Key</span>
      </div>
      <p class="setting-desc">AI 问答、AI 报告 / 诊断 / 学习计划都需要它。Key 会保存在服务器端 .env 文件里，不会回传显示。</p>

      <div class="status-row">
        <span>当前状态：</span>
        <span v-if="hasKey" class="tag-ok">已配置</span>
        <span v-else class="tag-bad">未配置</span>
      </div>

      <input v-model="apiKey" class="form-input" type="password" placeholder="粘贴你的 DeepSeek API Key（sk-...）" />
      <button class="btn" :disabled="loading || !apiKey.trim()" @click="save">{{ loading ? '保存中...' : '保存' }}</button>

      <div v-if="msg" class="msg" :class="{ err: msgErr }">{{ msg }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
import PageHeader from '../components/PageHeader.vue'

const apiKey = ref('')
const hasKey = ref(false)
const loading = ref(false)
const msg = ref('')
const msgErr = ref(false)

async function loadStatus() {
  try {
    const d = await api.getApiKeyStatus()
    hasKey.value = !!d.has_key
  } catch (e) { /* silent */ }
}

async function save() {
  const key = apiKey.value.trim()
  if (!key) return
  loading.value = true; msg.value = ''; msgErr.value = false
  try {
    await api.saveApiKey(key)
    hasKey.value = true
    apiKey.value = ''
    msg.value = '已保存，AI 功能现在可用了'
  } catch (e) { msg.value = e.message; msgErr.value = true }
  finally { loading.value = false }
}

onMounted(loadStatus)
</script>

<style scoped>
.settings-page { position: relative; z-index: 1; max-width: 560px; }
.settings-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 22px; display: flex; flex-direction: column; gap: 12px; }
.setting-title { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 0.9rem; color: var(--title); }
.setting-icon { width: 18px; height: 18px; color: var(--tea); }
.setting-desc { color: var(--muted); font-size: 0.76rem; line-height: 1.6; margin: 0; }
.status-row { display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text); }
.form-input { padding: 10px 14px; border-radius: 8px; border: 1.5px solid #d8e6d0; background: var(--card-bg); font-size: 0.82rem; color: var(--text); outline: none; font-family: inherit; transition: border-color 0.25s; }
.form-input:focus { border-color: var(--matcha); box-shadow: 0 0 0 3px rgba(138,184,96,0.1); }
.btn { padding: 10px 24px; border-radius: 10px; border: none; cursor: pointer; background: linear-gradient(135deg, var(--tea), var(--matcha)); color: #fff; font-weight: 600; font-size: 0.82rem; font-family: inherit; transition: all 0.25s; align-self: flex-start; }
.btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(106,154,64,0.25); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.msg { padding: 8px 12px; border-radius: 8px; font-size: 0.78rem; background: rgba(138,184,96,0.12); color: var(--tea); }
.msg.err { background: rgba(200,80,60,0.08); color: #d04040; }
.tag-ok { color: var(--tea); font-size: 0.78rem; font-weight: 600; }
.tag-bad { color: #d04040; font-size: 0.78rem; font-weight: 600; }
</style>
