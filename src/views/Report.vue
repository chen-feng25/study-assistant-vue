<template>
  <div class="report-page">
    <PageHeader title="分析报告" />

    <!-- Grade Selection -->
    <div class="select-card">
      <div class="select-header">
        <h3 class="select-title">📋 选择要分析的考试</h3>
        <div class="select-actions">
          <button class="text-btn" @click="selectAll">全选</button>
          <button class="text-btn" @click="deselectAll">取消全选</button>
        </div>
      </div>
      <div v-if="loadingGrades" class="loading-row">
        <span class="spinner"></span> 加载成绩列表...
      </div>
      <div v-else-if="grades.length === 0" class="empty-tip">
        暂无成绩记录，请先去<router-link to="/entry">录入数据</router-link>
      </div>
      <div v-else class="course-list">
        <div v-for="course in groupedCourses" :key="course.name" class="course-group">
          <div class="course-row">
            <label class="course-label">
              <input type="checkbox" :checked="course.checked" @change="toggleCourse(course)" />
              <span class="course-name">{{ course.name }}</span>
              <span class="course-meta">{{ course.items.length }} 次考试 · {{ course.scoreRange }}</span>
            </label>
            <button class="expand-btn" @click="course.expanded = !course.expanded" :title="course.expanded ? '收起' : '展开'">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <polyline v-if="!course.expanded" points="6 9 12 15 18 9" />
                <polyline v-else points="18 15 12 9 6 15" />
              </svg>
            </button>
          </div>
          <div v-if="course.expanded" class="course-exams">
            <label v-for="g in course.items" :key="g.id" class="exam-item" :class="{ checked: selectedIds.includes(g.id) }">
              <input type="checkbox" :value="g.id" v-model="selectedIds" />
              <span>{{ g.exam_type }} · {{ g.score }}/{{ g.total_score }}</span>
              <small>{{ g.exam_date }}</small>
            </label>
          </div>
        </div>
      </div>
      <button class="generate-btn" @click="generate" :disabled="selectedIds.length === 0 || anyLoading">
        <span v-if="anyLoading" class="spinner-sm"></span>
        {{ anyLoading ? '分析中...' : '生成分析报告' }}
      </button>
    </div>

    <!-- Results -->
    <template v-if="showResults">
      <!-- Stats Cards -->
      <div class="stat-cards">
        <div class="stat-card">
          <div v-if="loadingStats" class="spinner-sm"></div>
          <template v-else>
            <div class="num">{{ stats.avgScore ?? '--' }}</div>
            <div class="lbl">平均成绩</div>
          </template>
        </div>
        <div class="stat-card">
          <div v-if="loadingStats" class="spinner-sm"></div>
          <template v-else>
            <div class="num">{{ stats.totalPractice ?? '--' }}</div>
            <div class="lbl">刷题记录</div>
          </template>
        </div>
        <div class="stat-card">
          <div v-if="loadingStats" class="spinner-sm"></div>
          <template v-else>
            <div class="num">{{ stats.unmasteredMistakes ?? '--' }}</div>
            <div class="lbl">待攻克错题</div>
          </template>
        </div>
      </div>

      <GradeTrendChart :grades="filteredGrades" />

      <!-- Report Card -->
      <div class="report-card">
        <div class="card-title">
          📊 AI 学习复盘
          <button v-if="errorReport" class="retry-btn" @click="fetchReport()" title="重试">↻</button>
        </div>
        <div v-if="loadingReport" class="loading-box"><span class="spinner"></span> AI 正在分析中...</div>
        <div v-else-if="errorReport" class="err">{{ errorReport }}</div>
        <p v-else class="report-text">{{ report }}</p>
      </div>
    </template>

    <div v-if="error" class="err">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import PageHeader from '../components/PageHeader.vue'
import GradeTrendChart from '../components/GradeTrendChart.vue'

const uid = () => +sessionStorage.getItem('userId') || 0

// Grade selection
const grades = ref([])
const selectedIds = ref([])
const loadingGrades = ref(false)
const error = ref('')

// Show results after first generate click
const showResults = ref(false)

// Stats
const stats = ref({})
const loadingStats = ref(false)
const errorStats = ref('')

// Report
const report = ref('')
const loadingReport = ref(false)
const errorReport = ref('')

const anyLoading = computed(() =>
  loadingStats.value || loadingReport.value
)

// Filtered grades based on current selection
const filteredGrades = computed(() => {
  if (!showResults.value) return []
  const gids = getGids()
  if (!gids) return grades.value
  return grades.value.filter(g => gids.includes(g.id))
})

onMounted(async () => {
  loadingGrades.value = true
  try {
    grades.value = await api.getGrades(uid())
    selectedIds.value = grades.value.map(g => g.id)
  } catch (e) {
    error.value = '加载成绩列表失败: ' + e.message
  } finally {
    loadingGrades.value = false
  }
})

function selectAll() { selectedIds.value = grades.value.map(g => g.id) }
function deselectAll() { selectedIds.value = [] }

// Group grades by course
const groupedCourses = computed(() => {
  const map = {}
  for (const g of grades.value) {
    const name = g.course_name || '未分类'
    if (!map[name]) map[name] = []
    map[name].push(g)
  }
  return Object.entries(map).map(([name, items]) => {
    items.sort((a, b) => (a.exam_date || '').localeCompare(b.exam_date || ''))
    const scores = items.map(i => i.score / i.total_score * 100)
    const min = Math.min(...scores).toFixed(0)
    const max = Math.max(...scores).toFixed(0)
    return {
      name,
      items,
      expanded: false,
      checked: items.every(i => selectedIds.value.includes(i.id)),
      scoreRange: min === max ? `${min}分` : `${min}-${max}分`,
    }
  })
})

function toggleCourse(course) {
  const ids = course.items.map(i => i.id)
  if (course.checked) {
    selectedIds.value = selectedIds.value.filter(id => !ids.includes(id))
  } else {
    const set = new Set(selectedIds.value)
    ids.forEach(id => set.add(id))
    selectedIds.value = [...set]
  }
}

function getGids() {
  // Only pass grade_ids if not all selected (optimization: null = all)
  if (selectedIds.value.length === 0 || selectedIds.value.length === grades.value.length) return null
  return selectedIds.value
}

function generate() {
  if (selectedIds.value.length === 0) return
  showResults.value = true
  const gids = getGids()
  fetchStats(gids)
  fetchReport(gids)
}

async function fetchStats(gids) {
  loadingStats.value = true; errorStats.value = ''
  try {
    const s = await api.getStats(uid(), gids)
    const grades_for_avg = grades.value.filter(g => gids ? gids.includes(g.id) : true)
    const total = grades_for_avg.reduce((sum, g) => sum + (g.score / g.total_score * 100), 0)
    s.avgScore = grades_for_avg.length ? (total / grades_for_avg.length).toFixed(1) : null
    s.totalPractice = s.total_practice
    s.unmasteredMistakes = s.unmastered_mistakes
    stats.value = s
  } catch (e) { errorStats.value = e.message }
  finally { loadingStats.value = false }
}

async function fetchReport(gids) {
  loadingReport.value = true; errorReport.value = ''
  try {
    const r = await api.getReport(uid(), gids)
    report.value = r.report || ''
  } catch (e) { errorReport.value = e.message }
  finally { loadingReport.value = false }
}
</script>

<style scoped>
.report-page { position: relative; z-index: 1; }

/* Grade Selection */
.select-card {
  background: var(--card-bg); border-radius: 12px;
  border: 1px solid var(--card-border); padding: 16px; margin-bottom: 18px;
  animation: cardUp 0.5s ease-out both;
}
.select-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.select-title { font-size: 0.85rem; color: var(--title); font-weight: 600; margin: 0; }
.select-actions { display: flex; gap: 8px; }
.text-btn { background: none; border: none; color: var(--tea); font-size: 0.72rem; cursor: pointer; padding: 2px 8px; border-radius: 4px; font-family: inherit; transition: background 0.2s; }
.text-btn:hover { background: rgba(138,184,96,0.08); }
.course-list { display: flex; flex-direction: column; gap: 2px; max-height: 360px; overflow-y: auto; margin-bottom: 12px; }
.course-group { border-radius: 8px; overflow: hidden; }
.course-group:hover { background: rgba(138,184,96,0.03); }
.course-row { display: flex; align-items: center; padding: 6px 4px; }
.course-label { display: flex; align-items: center; gap: 10px; flex: 1; cursor: pointer; font-size: 0.8rem; }
.course-label input[type="checkbox"] { accent-color: var(--matcha); width: 15px; height: 15px; flex-shrink: 0; cursor: pointer; }
.course-name { font-weight: 600; color: var(--text); min-width: 80px; }
.course-meta { color: var(--muted); font-size: 0.7rem; }
.expand-btn { background: none; border: none; cursor: pointer; color: var(--muted); padding: 4px; border-radius: 4px; display: flex; align-items: center; transition: all 0.2s; }
.expand-btn:hover { color: var(--tea); background: rgba(138,184,96,0.06); }
.course-exams { padding: 2px 0 6px 28px; display: flex; flex-direction: column; gap: 2px; }
.exam-item { display: flex; align-items: center; gap: 10px; padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 0.74rem; transition: background 0.15s; }
.exam-item:hover { background: rgba(138,184,96,0.04); }
.exam-item.checked { background: rgba(138,184,96,0.06); }
.exam-item input[type="checkbox"] { accent-color: var(--matcha); width: 14px; height: 14px; flex-shrink: 0; cursor: pointer; }
.exam-item span { color: var(--muted); }
.exam-item small { color: var(--muted); opacity: 0.6; margin-left: auto; }
.generate-btn {
  width: 100%; padding: 10px; border-radius: 10px; border: none; cursor: pointer;
  background: linear-gradient(135deg, var(--tea), var(--matcha)); color: #fff;
  font-weight: 600; font-size: 0.84rem; font-family: inherit;
  transition: all 0.25s; display: flex; align-items: center; justify-content: center; gap: 8px;
}
.generate-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(106,154,64,0.25); }
.generate-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Stats */
.stat-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 18px; }
.stat-card {
  background: var(--card-bg); border-radius: 10px; padding: 16px;
  border: 1px solid var(--card-border); text-align: center;
  animation: cardUp 0.5s ease-out both; display: flex; align-items: center; justify-content: center; min-height: 64px;
}
.stat-card:nth-child(1){animation-delay:0.1s} .stat-card:nth-child(2){animation-delay:0.2s} .stat-card:nth-child(3){animation-delay:0.3s}
.stat-card .num { font-size: 1.6rem; font-weight: 700; color: var(--tea); }
.stat-card .lbl { font-size: 0.68rem; color: var(--muted); margin-top: 4px; }

/* Report Cards */
.report-card {
  background: var(--card-bg); border-radius: 12px; border: 1px solid var(--card-border);
  padding: 18px; margin-bottom: 14px; animation: cardUp 0.5s ease-out both;
}
.card-title {
  font-size: 0.85rem; color: var(--title); font-weight: 600; margin-bottom: 8px;
  display: flex; align-items: center; gap: 8px;
}
.report-text { font-size: 0.78rem; color: var(--text); line-height: 1.8; white-space: pre-wrap; }
.loading-box { display: flex; align-items: center; gap: 10px; color: var(--muted); font-size: 0.78rem; padding: 8px 0; }
.err { color: #d04040; font-size: 0.78rem; padding: 6px 0; }
.loading-row { display: flex; align-items: center; gap: 8px; color: var(--muted); font-size: 0.76rem; }
.empty-tip { font-size: 0.78rem; color: var(--muted); padding: 8px 0; }
.empty-tip a { color: var(--tea); }

.retry-btn {
  background: none; border: 1px solid var(--card-border); border-radius: 50%;
  width: 22px; height: 22px; cursor: pointer; color: var(--tea); font-size: 0.8rem;
  display: inline-flex; align-items: center; justify-content: center;
  transition: all 0.2s; margin-left: 6px;
}
.retry-btn:hover { background: rgba(138,184,96,0.1); border-color: var(--matcha); }

/* Spinner */
.spinner, .spinner-sm {
  width: 18px; height: 18px; border: 2px solid var(--card-border);
  border-top-color: var(--matcha); border-radius: 50%;
  animation: spin 0.6s linear infinite; flex-shrink: 0;
}
.spinner-sm { width: 14px; height: 14px; border-width: 2px; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 767px) {
  .stat-cards { grid-template-columns: repeat(3, 1fr); gap: 8px; }
  .stat-card { padding: 12px 8px; min-height: 56px; }
  .stat-card .num { font-size: 1.3rem; }
  .course-name { min-width: auto; }
}
</style>
