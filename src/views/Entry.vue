<template>
  <div class="entry-page">
    <PageHeader :title="viewMode ? '已有记录' : '录入学习数据'" />

    <div class="top-bar">
      <div class="tab-bar">
        <button v-for="t in tabs" :key="t.id" class="tab" :class="{ active: activeTab === t.id }" @click="activeTab = t.id">
          <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
            <path v-if="t.id==='course'" d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path v-if="t.id==='course'" d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/>
            <circle v-if="t.id==='grade'" cx="12" cy="8" r="5"/><polyline v-if="t.id==='grade'" points="3 21 3 17.5 7.5 13 11 15.5 16 10 21 14"/>
            <polyline v-if="t.id==='practice'" points="16 18 22 12 16 6"/><polyline v-if="t.id==='practice'" points="8 6 2 12 8 18"/>
            <path v-if="t.id==='note'" d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline v-if="t.id==='note'" points="14 2 14 8 20 8"/>
            <circle v-if="t.id==='mistake'" cx="12" cy="12" r="10"/><line v-if="t.id==='mistake'" x1="12" y1="8" x2="12" y2="12"/><line v-if="t.id==='mistake'" x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {{ t.label }}
        </button>
      </div>
      <button class="mode-toggle" @click="toggleMode">
        {{ viewMode ? '+ 录入' : '查看' }}
      </button>
    </div>

    <div v-if="msg" class="msg" :class="{ err: msgErr }">
      {{ msg }}
      <router-link v-if="!msgErr" to="/report" class="msg-link">查看分析报告</router-link>
    </div>

    <!-- ===== VIEW MODE ===== -->
    <template v-if="viewMode">
      <div v-if="loadingRecords" class="loading-row"><span class="spinner"></span> 加载中...</div>

      <template v-else-if="activeTab==='course'">
        <div v-if="courses.length" class="records-table">
          <div class="rec-row rec-head"><span>课程名称</span><span>成绩数</span><span>最高分</span><span>最低分</span><span>最近考试</span></div>
          <div v-for="c in courses" :key="c.name" class="rec-row">
            <span class="rec-course">{{ c.name }}</span>
            <span>{{ c.count }}</span>
            <span class="rec-score">{{ c.max }}</span>
            <span>{{ c.min }}</span>
            <span>{{ c.latest }}</span>
          </div>
        </div>
        <div v-else class="empty-tip">暂无课程</div>
      </template>

      <template v-else-if="activeTab==='grade'">
        <div v-if="records.grades?.length" class="records-table">
          <div class="rec-row rec-head">
            <span>课程</span><span>类型</span><span>分数</span><span>日期</span><span>备注</span>
          </div>
          <div v-for="r in records.grades" :key="r.id" class="rec-row">
            <span class="rec-course">{{ r.course_name }}</span>
            <span>{{ r.exam_type }}</span>
            <span class="rec-score">{{ r.score }}/{{ r.total_score }}</span>
            <span>{{ r.exam_date }}</span>
            <span class="rec-note">{{ r.notes || '-' }}</span>
          </div>
        </div>
        <div v-else class="empty-tip">暂无成绩记录</div>
      </template>

      <template v-else-if="activeTab==='practice'">
        <div v-if="records.practices?.length" class="records-table">
          <div class="rec-row rec-head">
            <span>课程</span><span>平台</span><span>题量</span><span>正确率</span><span>日期</span>
          </div>
          <div v-for="r in records.practices" :key="r.id" class="rec-row">
            <span class="rec-course">{{ r.course_name || '通用' }}</span>
            <span>{{ r.platform || '-' }}</span>
            <span>{{ r.problem_count }}</span>
            <span class="rec-score">{{ r.problem_count ? (r.correct_count / r.problem_count * 100).toFixed(0) + '%' : '-' }}</span>
            <span>{{ r.practice_date }}</span>
          </div>
        </div>
        <div v-else class="empty-tip">暂无刷题记录</div>
      </template>

      <template v-else-if="activeTab==='note'">
        <div v-if="records.notes?.length" class="note-list">
          <div v-for="r in records.notes" :key="r.id" class="note-card">
            <div class="note-head">
              <strong>{{ r.title }}</strong>
              <span class="note-course">{{ r.course_name || '通用' }}</span>
              <small>{{ r.note_date }}</small>
            </div>
            <p class="note-body">{{ r.content }}</p>
          </div>
        </div>
        <div v-else class="empty-tip">暂无笔记</div>
      </template>

      <template v-else-if="activeTab==='mistake'">
        <div v-if="records.mistakes?.length" class="records-table">
          <div class="rec-row rec-head">
            <span>课程</span><span>题目</span><span>状态</span><span>日期</span>
          </div>
          <div v-for="r in records.mistakes" :key="r.id" class="rec-row rec-row--click" @click="openMistake(r)" title="点击查看详情">
            <span class="rec-course">{{ r.course_name || '通用' }}</span>
            <span class="rec-desc">{{ r.problem_description?.slice(0, 40) }}{{ r.problem_description?.length > 40 ? '...' : '' }}</span>
            <span :class="r.mastered ? 'tag-ok' : 'tag-bad'">{{ r.mastered ? '已掌握' : '未掌握' }}</span>
            <span>{{ r.mistake_date }}</span>
          </div>
        </div>
        <div v-else class="empty-tip">暂无错题</div>
      </template>
    </template>

    <!-- ===== ENTRY MODE ===== -->
    <template v-else>
      <form v-if="activeTab==='course'" @submit.prevent="submitCourse" class="entry-form">
        <input v-model="cEntry.name" class="fi" placeholder="课程名称 *" required>
        <button class="btn" :disabled="loading">添加课程</button>
      </form>

      <form v-if="activeTab==='grade'" @submit.prevent="submitGrade" class="entry-form">
        <div class="form-row"><input v-model="g.course" class="fi" placeholder="课程名称 *" required><input v-model.number="g.score" class="fi" type="number" placeholder="得分" required></div>
        <div class="form-row"><input v-model.number="g.total" class="fi" type="number" placeholder="满分" value="100"><select v-model="g.type" class="fi"><option v-for="o in ['作业','小测','期中','期末','模拟','其他']" :key="o">{{ o }}</option></select></div>
        <input v-model="g.date" class="fi" type="date" required>
        <input v-model="g.notes" class="fi" placeholder="备注（可选）">
        <button class="btn" :disabled="loading">提交成绩</button>
      </form>

      <form v-if="activeTab==='practice'" @submit.prevent="submitPractice" class="entry-form">
        <div class="form-row"><input v-model="p.course" class="fi" placeholder="关联课程（可选）"><select v-model="p.platform" class="fi"><option v-for="o in ['LeetCode','牛客','AcWing','洛谷','Codeforces','其他','']" :key="o">{{ o || '选择平台' }}</option></select></div>
        <div class="form-row"><input v-model="p.topic" class="fi" placeholder="专题/章节"><input v-model.number="p.count" class="fi" type="number" placeholder="做题数量 *" required></div>
        <div class="form-row"><input v-model.number="p.correct" class="fi" type="number" placeholder="正确数量"><input v-model.number="p.duration" class="fi" type="number" placeholder="耗时（分钟）"></div>
        <input v-model="p.date" class="fi" type="date" required>
        <input v-model="p.notes" class="fi" placeholder="备注（可选）">
        <button class="btn" :disabled="loading">提交刷题记录</button>
      </form>

      <form v-if="activeTab==='note'" @submit.prevent="submitNote" class="entry-form">
        <div class="form-row"><input v-model="n.course" class="fi" placeholder="关联课程（可选）"><input v-model="n.title" class="fi" placeholder="笔记标题 *" required></div>
        <textarea v-model="n.content" class="fi" placeholder="笔记内容 *" rows="4" required></textarea>
        <input v-model="n.date" class="fi" type="date" required>
        <button class="btn" :disabled="loading">保存笔记</button>
      </form>

      <form v-if="activeTab==='mistake'" @submit.prevent="submitMistake" class="entry-form">
        <div class="form-row"><input v-model="m.course" class="fi" placeholder="关联课程（可选）"><select v-model="m.mastered" class="fi"><option :value="0">未掌握</option><option :value="1">已掌握</option></select></div>
        <input v-model="m.question" class="fi" placeholder="题目描述 *" required>
        <input v-model="m.wrong" class="fi" placeholder="错误原因">
        <input v-model="m.solution" class="fi" placeholder="正确解法">
        <input v-model="m.date" class="fi" type="date" required>
        <button class="btn" :disabled="loading">记录错题</button>
      </form>
    </template>

    <!-- 错题详情弹窗 -->
    <div v-if="selectedMistake" class="modal-mask" @click.self="selectedMistake = null">
      <div class="modal-card">
        <div class="modal-head">
          <span class="modal-title">错题详情</span>
          <button class="modal-close" @click="selectedMistake = null" aria-label="关闭">✕</button>
        </div>
        <div class="modal-body">
          <div class="mi-row"><span class="mi-label">课程</span><span>{{ selectedMistake.course_name || '通用' }}</span></div>
          <div class="mi-row"><span class="mi-label">日期</span><span>{{ selectedMistake.mistake_date }}</span></div>
          <div class="mi-row"><span class="mi-label">状态</span><span :class="selectedMistake.mastered ? 'tag-ok' : 'tag-bad'">{{ selectedMistake.mastered ? '已掌握' : '未掌握' }}</span></div>
          <div class="mi-block">
            <div class="mi-label">题目描述</div>
            <p class="mi-text">{{ selectedMistake.problem_description }}</p>
          </div>
          <div class="mi-block" v-if="selectedMistake.reason">
            <div class="mi-label">错误原因</div>
            <p class="mi-text">{{ selectedMistake.reason }}</p>
          </div>
          <div class="mi-block" v-if="selectedMistake.correct_answer">
            <div class="mi-label">正确解法</div>
            <p class="mi-text">{{ selectedMistake.correct_answer }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import PageHeader from '../components/PageHeader.vue'

const route = useRoute()
const router = useRouter()

const tabs = [
  { id: 'course', label: '课程' },
  { id: 'grade', label: '成绩' },
  { id: 'practice', label: '刷题' },
  { id: 'note', label: '笔记' },
  { id: 'mistake', label: '错题' },
]
const validTabs = tabs.map(t => t.id)
const activeTab = ref(validTabs.includes(route.query.tab) ? route.query.tab : 'grade')
const viewMode = ref(route.query.view === '1')

watch(activeTab, (val) => {
  router.replace({ query: { tab: val, ...(viewMode.value ? { view: '1' } : {}) } })
})

watch(() => route.query.tab, (val) => {
  if (validTabs.includes(val)) activeTab.value = val
})

watch(() => route.query.view, (val) => {
  viewMode.value = val === '1'
  if (viewMode.value) fetchRecords()
})

function toggleMode() {
  viewMode.value = !viewMode.value
  router.replace({ query: { tab: activeTab.value, ...(viewMode.value ? { view: '1' } : {}) } })
  if (viewMode.value) fetchRecords()
}

// --- Records view ---
const records = ref({ grades: [], practices: [], notes: [], mistakes: [] })
const loadingRecords = ref(false)
const selectedMistake = ref(null)
function openMistake(r) { selectedMistake.value = r }

async function fetchRecords() {
  loadingRecords.value = true
  try {
    records.value = await api.getRecords(uid())
  } catch (e) { /* silent */ }
  finally { loadingRecords.value = false }
}

const courses = computed(() => {
  const map = {}
  for (const g of (records.value.grades || [])) {
    const n = g.course_name || 'unknown'
    if (!map[n]) map[n] = []
    map[n].push(g)
  }
  return Object.entries(map).map(([name, items]) => {
    const scores = items.map(i => i.score / i.total_score * 100)
    items.sort((a, b) => (a.exam_date || '').localeCompare(b.exam_date || ''))
    return {
      name,
      count: items.length,
      max: Math.max(...scores).toFixed(0) + '%',
      min: Math.min(...scores).toFixed(0) + '%',
      latest: items[items.length - 1].exam_date || '-',
    }
  })
})

onMounted(() => {
  if (viewMode.value) fetchRecords()
})

// --- Entry forms ---
const loading = ref(false)
const msg = ref(''); const msgErr = ref(false)

const uid = () => +sessionStorage.getItem('userId') || 0
const today = () => new Date().toISOString().slice(0, 10)

const cEntry = reactive({ name:'' })
const g = reactive({ course:'', score:85, total:100, type:'期中', date:today(), notes:'' })
const p = reactive({ course:'', platform:'', topic:'', count:10, correct:8, duration:60, date:today(), notes:'' })
const n = reactive({ course:'', title:'', content:'', date:today() })
const m = reactive({ course:'', question:'', wrong:'', solution:'', mastered:0, date:today() })

function show(msgText, isErr) { msg.value = msgText; msgErr.value = isErr; setTimeout(()=>msg.value='',3000) }

async function submitCourse() {
  if (!cEntry.name.trim()) { show('请填写课程名称', true); return }
  loading.value = true
  try { await api.addCourse(cEntry.name.trim(), uid()); show('课程已添加', false); cEntry.name='' } catch(e) { show(e.message, true) } finally { loading.value = false }
}

async function submitGrade() {
  if (!g.course) { show('请填写课程名称', true); return }
  loading.value = true
  try { await api.addGrade({ user_id: uid(), course_name: g.course, score: g.score, total_score: g.total, exam_type: g.type, exam_date: g.date, notes: g.notes }); show('成绩已录入', false); g.course=''; g.notes='' } catch(e) { show(e.message, true) } finally { loading.value = false }
}
async function submitPractice() {
  if (!p.count) { show('请填写做题数量', true); return }
  loading.value = true
  try { await api.addPractice({ user_id: uid(), course: p.course, platform: p.platform, topic: p.topic, count: p.count, correct: p.correct, duration: p.duration, date: p.date, notes: p.notes }); show('刷题记录已保存', false); p.course=''; p.topic='' } catch(e) { show(e.message, true) } finally { loading.value = false }
}
async function submitNote() {
  if (!n.title || !n.content) { show('请填写标题和内容', true); return }
  loading.value = true
  try { await api.addNote({ user_id: uid(), course: n.course, title: n.title, content: n.content, date: n.date }); show('笔记已保存', false); n.title=''; n.content=''; n.course='' } catch(e) { show(e.message, true) } finally { loading.value = false }
}
async function submitMistake() {
  if (!m.question) { show('请填写题目描述', true); return }
  loading.value = true
  try { await api.addMistake({ user_id: uid(), course: m.course, question: m.question, wrong_reason: m.wrong, correct_solution: m.solution, mastered: m.mastered, date: m.date }); show('错题已记录', false); m.question=''; m.wrong=''; m.solution=''; m.course='' } catch(e) { show(e.message, true) } finally { loading.value = false }
}
</script>

<style scoped>
.entry-page { position: relative; z-index: 1; }

.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; gap: 8px; }

.tab-bar { display: flex; gap: 4px; }
.tab { padding: 7px 14px; border-radius: 8px; font-size: 0.76rem; cursor: pointer; border: none; color: var(--muted); background: transparent; transition: all 0.25s; font-weight: 500; font-family: inherit; display: flex; align-items: center; gap: 6px; }
.tab.active { background: var(--card-bg); color: var(--title); font-weight: 600; box-shadow: 0 1px 6px var(--shadow); }
.tab:not(.active):hover { color: var(--text); }
.tab-icon { width: 16px; height: 16px; flex-shrink: 0; }

.mode-toggle { padding: 5px 14px; border-radius: 8px; font-size: 0.74rem; cursor: pointer; border: 1px solid var(--card-border); background: var(--card-bg); color: var(--tea); font-family: inherit; transition: all 0.2s; white-space: nowrap; }
.mode-toggle:hover { border-color: var(--matcha); background: rgba(138,184,96,0.06); }

.entry-form { display: flex; flex-direction: column; gap: 10px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.fi { padding: 9px 12px; border-radius: 8px; border: 1.5px solid #d8e6d0; background: var(--card-bg); font-size: 0.78rem; color: var(--text); outline: none; font-family: inherit; transition: border-color 0.25s; }
.fi:focus { border-color: var(--matcha); box-shadow: 0 0 0 3px rgba(138,184,96,0.1); }
textarea.fi { resize: vertical; }
.btn { padding: 10px 28px; border-radius: 10px; border: none; cursor: pointer; background: linear-gradient(135deg, var(--tea), var(--matcha)); color: #fff; font-weight: 600; font-size: 0.82rem; font-family: inherit; transition: all 0.25s; align-self: flex-start; }
.btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(106,154,64,0.25); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.msg { margin-bottom: 12px; padding: 8px 14px; border-radius: 8px; font-size: 0.78rem; background: rgba(138,184,96,0.12); color: var(--tea); display: flex; align-items: center; gap: 12px; }
.msg.err { background: rgba(200,80,60,0.08); color: #d04040; }
.msg-link { color: var(--tea); font-weight: 600; text-decoration: underline; white-space: nowrap; }
.msg-link:hover { color: var(--matcha); }

/* Records view */
.records-table { border-radius: 10px; overflow: hidden; border: 1px solid var(--card-border); font-size: 0.76rem; }
.rec-row { display: grid; grid-template-columns: 1.2fr 0.7fr 0.7fr 1fr 1fr; gap: 6px; padding: 8px 12px; align-items: center; border-bottom: 1px solid rgba(200,224,192,0.08); background: var(--card-bg); }
.rec-row:last-child { border-bottom: none; }
.rec-head { background: rgba(138,184,96,0.04); color: var(--tea); font-weight: 600; font-size: 0.72rem; }
.rec-course { color: var(--text); font-weight: 500; }
.rec-score { font-weight: 600; color: var(--tea); }
.rec-note { color: var(--muted); font-size: 0.7rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rec-desc { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.note-list { display: flex; flex-direction: column; gap: 10px; }
.note-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 10px; padding: 12px; }
.note-head { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.note-head strong { color: var(--text); font-size: 0.82rem; }
.note-course { color: var(--tea); font-size: 0.7rem; background: rgba(138,184,96,0.08); padding: 1px 8px; border-radius: 4px; }
.note-head small { color: var(--muted); margin-left: auto; font-size: 0.7rem; }
.note-body { font-size: 0.76rem; color: var(--muted); line-height: 1.6; margin: 0; white-space: pre-wrap; }

.tag-ok { color: var(--tea); font-size: 0.7rem; font-weight: 500; }
.tag-bad { color: #d04040; font-size: 0.7rem; font-weight: 500; }

.empty-tip { color: var(--muted); font-size: 0.82rem; padding: 16px 0; }
.loading-row { display: flex; align-items: center; gap: 8px; color: var(--muted); font-size: 0.78rem; padding: 12px 0; }

.spinner { width: 18px; height: 18px; border: 2px solid var(--card-border); border-top-color: var(--matcha); border-radius: 50%; animation: spin 0.6s linear infinite; flex-shrink: 0; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }

.rec-row--click { cursor: pointer; transition: background 0.15s; }
.rec-row--click:hover { background: rgba(138,184,96,0.06); }

.modal-mask { position: fixed; inset: 0; z-index: 300; background: rgba(15,23,42,0.5); display: flex; align-items: center; justify-content: center; padding: 20px; animation: modalFade 0.2s ease-out; }
.modal-card { width: 100%; max-width: 560px; max-height: 85vh; overflow-y: auto; background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; box-shadow: 0 20px 60px rgba(0,0,0,0.35); }
.modal-head { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid var(--card-border); }
.modal-title { font-weight: 700; font-size: 0.95rem; color: var(--title); }
.modal-close { background: none; border: none; cursor: pointer; color: var(--muted); font-size: 1rem; padding: 4px 8px; border-radius: 6px; }
.modal-close:hover { color: var(--text); background: rgba(255,255,255,0.06); }
.modal-body { padding: 16px 20px 20px; display: flex; flex-direction: column; gap: 12px; }
.mi-row { display: flex; gap: 12px; font-size: 0.78rem; }
.mi-label { flex-shrink: 0; width: 72px; color: var(--muted); }
.mi-block { display: flex; flex-direction: column; gap: 6px; }
.mi-block .mi-label { width: auto; }
.mi-text { margin: 0; font-size: 0.8rem; line-height: 1.7; color: var(--text); white-space: pre-wrap; background: rgba(255,255,255,0.03); border: 1px solid var(--card-border); border-radius: 8px; padding: 10px 12px; }
@keyframes modalFade { from { opacity: 0; } to { opacity: 1; } }

@media (max-width: 767px) {
  .tab-bar { overflow-x: auto; -webkit-overflow-scrolling: touch; flex-wrap: nowrap; }
  .tab { flex-shrink: 0; white-space: nowrap; }
  .form-row { grid-template-columns: 1fr; }
  .rec-row { grid-template-columns: 1fr 0.7fr 0.7fr 1fr; }
  .rec-note { display: none; }
  .rec-head .rec-note { display: none; }
}
</style>
