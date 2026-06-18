<template>
  <div class="report-page">
    <PageHeader title="分析报告" />
    <div class="stat-cards">
      <div class="stat-card"><div class="num">{{ stats.avgScore || '--' }}</div><div class="lbl">平均成绩</div></div>
      <div class="stat-card"><div class="num">{{ stats.totalPractice || '--' }}</div><div class="lbl">刷题总数</div></div>
      <div class="stat-card"><div class="num">{{ stats.unmasteredMistakes || '--' }}</div><div class="lbl">待攻克错题</div></div>
    </div>
    <div v-if="report" class="report-card">
      <div class="report-title">AI 学习建议</div>
      <p class="report-text">{{ report }}</p>
    </div>
    <div v-if="error" class="err">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
import PageHeader from '../components/PageHeader.vue'

const uid = () => +localStorage.getItem('userId') || 0
const stats = ref({})
const report = ref('')
const error = ref('')

onMounted(async () => {
  try {
    stats.value = await api.getStats(uid())
    const r = await api.getReport(uid())
    report.value = r.report || r.content || ''
  } catch (e) { error.value = e.message }
})
</script>

<style scoped>
.report-page { position: relative; z-index: 1; }
.stat-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 18px; }
.stat-card { background: var(--card-bg); border-radius: 10px; padding: 16px; border: 1px solid var(--card-border); text-align: center; animation: cardUp 0.5s ease-out both; }
.stat-card:nth-child(1){animation-delay:0.1s} .stat-card:nth-child(2){animation-delay:0.2s} .stat-card:nth-child(3){animation-delay:0.3s}
.stat-card .num { font-size: 1.6rem; font-weight: 700; color: var(--tea); }
.stat-card .lbl { font-size: 0.68rem; color: var(--muted); margin-top: 4px; }
.report-card { background: var(--card-bg); border-radius: 12px; border: 1px solid var(--card-border); padding: 18px; animation: cardUp 0.5s ease-out 0.4s both; }
.report-title { font-size: 0.85rem; color: var(--title); font-weight: 600; margin-bottom: 8px; }
.report-text { font-size: 0.78rem; color: var(--text); line-height: 1.8; }
.err { color: #d04040; font-size: 0.82rem; }
</style>
