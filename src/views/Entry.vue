<template>
  <div class="entry-page">
    <PageHeader title="录入学习数据" />

    <div class="tab-bar">
      <button v-for="t in tabs" :key="t.id" class="tab" :class="{ active: activeTab === t.id }" @click="activeTab = t.id">
        <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
          <circle v-if="t.id==='grade'" cx="12" cy="8" r="5"/><polyline v-if="t.id==='grade'" points="3 21 3 17.5 7.5 13 11 15.5 16 10 21 14"/>
          <polyline v-if="t.id==='practice'" points="16 18 22 12 16 6"/><polyline v-if="t.id==='practice'" points="8 6 2 12 8 18"/>
          <path v-if="t.id==='note'" d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline v-if="t.id==='note'" points="14 2 14 8 20 8"/>
          <circle v-if="t.id==='mistake'" cx="12" cy="12" r="10"/><line v-if="t.id==='mistake'" x1="12" y1="8" x2="12" y2="12"/><line v-if="t.id==='mistake'" x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {{ t.label }}
      </button>
    </div>

    <div v-if="msg" class="msg" :class="{ err: msgErr }">{{ msg }}</div>

    <!-- Grade form -->
    <form v-if="activeTab==='grade'" @submit.prevent="submitGrade" class="entry-form">
      <div class="form-row"><input v-model="g.course" class="fi" placeholder="课程名称 *" required><input v-model.number="g.score" class="fi" type="number" placeholder="得分" required></div>
      <div class="form-row"><input v-model.number="g.total" class="fi" type="number" placeholder="满分" value="100"><select v-model="g.type" class="fi"><option v-for="o in ['作业','小测','期中','期末','模拟','其他']" :key="o">{{ o }}</option></select></div>
      <input v-model="g.date" class="fi" type="date" required>
      <input v-model="g.notes" class="fi" placeholder="备注（可选）">
      <button class="btn" :disabled="loading">提交成绩</button>
    </form>

    <!-- Practice form -->
    <form v-if="activeTab==='practice'" @submit.prevent="submitPractice" class="entry-form">
      <div class="form-row"><input v-model="p.course" class="fi" placeholder="关联课程（可选）"><select v-model="p.platform" class="fi"><option v-for="o in ['LeetCode','牛客','AcWing','洛谷','Codeforces','其他','']" :key="o">{{ o || '选择平台' }}</option></select></div>
      <div class="form-row"><input v-model="p.topic" class="fi" placeholder="专题/章节"><input v-model.number="p.count" class="fi" type="number" placeholder="做题数量 *" required></div>
      <div class="form-row"><input v-model.number="p.correct" class="fi" type="number" placeholder="正确数量"><input v-model.number="p.duration" class="fi" type="number" placeholder="耗时（分钟）"></div>
      <input v-model="p.date" class="fi" type="date" required>
      <input v-model="p.notes" class="fi" placeholder="备注（可选）">
      <button class="btn" :disabled="loading">提交刷题记录</button>
    </form>

    <!-- Note form -->
    <form v-if="activeTab==='note'" @submit.prevent="submitNote" class="entry-form">
      <div class="form-row"><input v-model="n.course" class="fi" placeholder="关联课程（可选）"><input v-model="n.title" class="fi" placeholder="笔记标题 *" required></div>
      <textarea v-model="n.content" class="fi" placeholder="笔记内容 *" rows="4" required></textarea>
      <input v-model="n.date" class="fi" type="date" required>
      <button class="btn" :disabled="loading">保存笔记</button>
    </form>

    <!-- Mistake form -->
    <form v-if="activeTab==='mistake'" @submit.prevent="submitMistake" class="entry-form">
      <div class="form-row"><input v-model="m.course" class="fi" placeholder="关联课程（可选）"><select v-model="m.mastered" class="fi"><option :value="0">未掌握</option><option :value="1">已掌握</option></select></div>
      <input v-model="m.question" class="fi" placeholder="题目描述 *" required>
      <input v-model="m.wrong" class="fi" placeholder="错误原因">
      <input v-model="m.solution" class="fi" placeholder="正确解法">
      <input v-model="m.date" class="fi" type="date" required>
      <button class="btn" :disabled="loading">记录错题</button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { api } from '../api'
import PageHeader from '../components/PageHeader.vue'

const tabs = [
  { id: 'grade', label: '成绩录入' },
  { id: 'practice', label: '刷题记录' },
  { id: 'note', label: '学习笔记' },
  { id: 'mistake', label: '错题记录' },
]
const activeTab = ref('grade')
const loading = ref(false)
const msg = ref(''); const msgErr = ref(false)

const uid = () => +localStorage.getItem('userId') || 0
const today = () => new Date().toISOString().slice(0, 10)

const g = reactive({ course:'', score:85, total:100, type:'期中', date:today(), notes:'' })
const p = reactive({ course:'', platform:'', topic:'', count:10, correct:8, duration:60, date:today(), notes:'' })
const n = reactive({ course:'', title:'', content:'', date:today() })
const m = reactive({ course:'', question:'', wrong:'', solution:'', mastered:0, date:today() })

function show(msgText, isErr) { msg.value = msgText; msgErr.value = isErr; setTimeout(()=>msg.value='',3000) }

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
.tab-bar { display: flex; gap: 4px; margin-bottom: 18px; }
.tab { padding: 7px 14px; border-radius: 8px; font-size: 0.76rem; cursor: pointer; border: none; color: var(--muted); background: transparent; transition: all 0.25s; font-weight: 500; font-family: inherit; display: flex; align-items: center; gap: 6px; }
.tab.active { background: var(--card-bg); color: var(--title); font-weight: 600; box-shadow: 0 1px 6px var(--shadow); }
.tab:not(.active):hover { color: var(--text); }
.tab-icon { width: 16px; height: 16px; flex-shrink: 0; }
.entry-form { display: flex; flex-direction: column; gap: 10px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.fi { padding: 9px 12px; border-radius: 8px; border: 1.5px solid #d8e6d0; background: var(--card-bg); font-size: 0.78rem; color: var(--text); outline: none; font-family: inherit; transition: border-color 0.25s; }
.fi:focus { border-color: var(--matcha); box-shadow: 0 0 0 3px rgba(138,184,96,0.1); }
textarea.fi { resize: vertical; }
.btn { padding: 10px 28px; border-radius: 10px; border: none; cursor: pointer; background: linear-gradient(135deg, var(--tea), var(--matcha)); color: #fff; font-weight: 600; font-size: 0.82rem; font-family: inherit; transition: all 0.25s; align-self: flex-start; }
.btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(106,154,64,0.25); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.msg { margin-bottom: 12px; padding: 8px 14px; border-radius: 8px; font-size: 0.78rem; background: rgba(138,184,96,0.12); color: var(--tea); }
.msg.err { background: rgba(200,80,60,0.08); color: #d04040; }
</style>
