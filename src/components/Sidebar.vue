<template>
  <nav class="sidebar" :class="{ 'sidebar--mobile': isMobile, 'sidebar--open': mobileOpen, 'sidebar--collapsed': collapsed && !isMobile }">
    <div v-if="isMobile" class="sidebar-top-row">
      <div class="sidebar-top-spacer"></div>
      <button class="sidebar-close" @pointerdown.stop="onClose?.()" aria-label="close">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <router-link to="/" class="logo-link" @click="$emit('nav')">
      <MatchaLogo :size="34" />
      <div v-show="!collapsed || isMobile" class="logo-title">学习档案助理</div>
      <div v-show="!collapsed || isMobile" class="logo-sub">Personal Study Archive</div>
    </router-link>
    <div v-show="!collapsed || isMobile" class="sep"></div>

    <router-link v-for="item in navItems" :key="item.to" :to="item.to" class="nav-item" :class="{ active: $route.path === item.to || (item.to === '/entry' && $route.path === '/entry') }" @click="$emit('nav')">
      <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">
        <path v-if="item.icon==='entry'" d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/>
        <template v-if="item.icon==='report'"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></template>
        <path v-if="item.icon==='chat'" d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
        <template v-if="item.icon==='settings'"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></template>
      </svg>
      <span v-show="!collapsed || isMobile">{{ item.label }}</span>
    </router-link>

    <div v-show="!collapsed || isMobile" class="sidebar-stats">
      <div class="stat-row stat-link" @click="goTab('course')">
        <svg class="stats-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>
        <span>课程</span><span>{{ stats.total_courses ?? '--' }}</span>
      </div>
      <div class="stat-row stat-link" @click="goTab('grade')">
        <svg class="stats-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
        <span>成绩</span><span>{{ stats.total_grades ?? '--' }}</span>
      </div>
      <div class="stat-row stat-link" @click="goTab('practice')">
        <svg class="stats-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
        <span>刷题</span><span>{{ stats.total_practice ?? '--' }}</span>
      </div>
      <div class="stat-row stat-link" @click="goTab('note')">
        <svg class="stats-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        <span>笔记</span><span>{{ stats.total_notes ?? '--' }}</span>
      </div>
      <div class="stat-row stat-link" @click="goTab('mistake')">
        <svg class="stats-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
        <span>错题</span><span>{{ stats.total_mistakes ?? '--' }}<template v-if="stats.unmastered_mistakes"> ({{ stats.unmastered_mistakes }})</template></span>
      </div>
    </div>

    <button class="collapse-btn" @click="$emit('toggleCollapse')" :title="collapsed ? '展开侧栏' : '收起侧栏'">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline v-if="!collapsed" points="15 18 9 12 15 6" />
        <polyline v-else points="9 18 15 12 9 6" />
      </svg>
    </button>

    <div v-show="!collapsed || isMobile" class="sidebar-footer">
      <div class="user-row">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        <span>{{ username }}</span>
      </div>
      <button class="logout-btn" @click="logout">退出</button>
    </div>
  </nav>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import MatchaLogo from './MatchaLogo.vue'

const props = defineProps({
  mobileOpen: { type: Boolean, default: false },
  collapsed: { type: Boolean, default: false },
  onClose: { type: Function, default: null }
})

defineEmits(['nav', 'toggleCollapse', 'close'])

const router = useRouter()
const username = ref(sessionStorage.getItem('username') || '?')

function logout() {
  sessionStorage.removeItem('userId')
  sessionStorage.removeItem('username')
  router.push('/login')
}

const navItems = [
  { to: '/entry', label: '录入数据', icon: 'entry' },
  { to: '/report', label: '分析报告', icon: 'report' },
  { to: '/chat', label: 'AI 问答', icon: 'chat' },
  { to: '/settings', label: '设置', icon: 'settings' },
]

function goTab(tab) {
  router.push({ path: '/entry', query: { tab, view: '1' } })
}

const stats = reactive({
  total_courses: null,
  total_grades: null,
  total_practice: null,
  total_notes: null,
  total_mistakes: null,
  unmastered_mistakes: null,
})

async function fetchStats() {
  const uid = sessionStorage.getItem('userId')
  if (!uid) return
  try {
    const BASE = '/api'
    const r = await fetch(`${BASE}/stats?user_id=${uid}`)
    const d = await r.json()
    if (r.ok) Object.assign(stats, d)
  } catch (e) { /* silent */ }
}

const isMobile = ref(false)
let mediaQuery

onMounted(() => {
  mediaQuery = window.matchMedia('(max-width: 767px)')
  isMobile.value = mediaQuery.matches
  mediaQuery.addEventListener('change', (e) => { isMobile.value = e.matches })
  fetchStats()
})

onUnmounted(() => {
  mediaQuery?.removeEventListener('change', () => {})
})
</script>

<style scoped>
.sidebar { width: 205px; min-height: 100vh; flex-shrink: 0; background: linear-gradient(180deg, var(--sidebar-start) 0%, var(--sidebar-mid) 45%, var(--sidebar-start) 100%); color: var(--sidebar-text); font-size: 0.78rem; display: flex; flex-direction: column; padding: 24px 14px; animation: sidebarIn 0.6s ease-out both; transition: width 0.25s ease; }

.sidebar--collapsed {
  width: 62px; padding: 24px 10px; align-items: center;
}
.sidebar--collapsed .nav-item { justify-content: center; padding: 9px 0; }

.sidebar--mobile {
  position: fixed; top: 0; bottom: 0; z-index: 200;
  left: -240px;
  transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 4px 0 20px rgba(0,0,0,0.2);
  width: 240px; padding: 24px 14px; align-items: stretch;
}
.sidebar--mobile.sidebar--open {
  left: 0;
}

.sidebar-top-row { display: flex; align-items: center; margin-bottom: 8px; }
.sidebar-top-spacer { flex: 1; }
.sidebar-close {
  background: rgba(255,255,255,0.06); border: none;
  color: rgba(200,224,192,0.5); cursor: pointer;
  width: 44px; height: 44px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  touch-action: manipulation; -webkit-tap-highlight-color: transparent;
  flex-shrink: 0;
}
.sidebar-close:hover { color: var(--sidebar-active); background: rgba(255,255,255,0.1); }

.logo-link { text-align: center; margin-bottom: 14px; text-decoration: none; display: block; }
.logo-link:hover { opacity: 0.85; }
.logo-title { font-weight: 700; color: var(--sidebar-active); font-size: 0.9rem; margin-top: 2px; }
.logo-sub { font-size: 0.55rem; color: #9aae8a; }
.sep { height: 0.5px; background: rgba(200, 224, 192, 0.2); margin: 6px 0 12px; }
.nav-item { padding: 9px 11px; border-radius: 7px; margin: 2px 0; cursor: pointer; color: var(--sidebar-dim); transition: all 0.25s; display: flex; align-items: center; gap: 9px; text-decoration: none; animation: navSlide 0.4s ease-out backwards; min-height: 44px; }
.nav-item:nth-child(2){animation-delay:0.1s} .nav-item:nth-child(3){animation-delay:0.2s} .nav-item:nth-child(4){animation-delay:0.3s}
.nav-item.active { background: rgba(255,255,255,0.08); color: var(--sidebar-active); border-left: 2px solid var(--matcha); padding-left: 9px; }
.nav-item:not(.active):hover { background: rgba(255,255,255,0.04); color: rgba(200,224,192,0.75); }
.nav-icon { width: 18px; height: 18px; flex-shrink: 0; }
.sidebar-stats { margin-top: 12px; font-size: 0.62rem; color: #9aae8a; }
.stat-row { display: flex; align-items: center; justify-content: space-between; padding: 3px 4px; gap: 6px; }
.stat-link { text-decoration: none; color: inherit; border-radius: 4px; transition: background 0.15s; cursor: pointer; }
.stat-link:hover { background: rgba(255,255,255,0.04); color: var(--sidebar-active); }
.stats-icon { width: 12px; height: 12px; flex-shrink: 0; opacity: 0.6; }

.collapse-btn {
  margin-top: auto; margin-bottom: 4px; align-self: center;
  background: none; border: none; cursor: pointer; color: rgba(200,224,192,0.35);
  padding: 6px; border-radius: 6px; transition: all 0.2s;
  display: flex; align-items: center; justify-content: center;
}
.collapse-btn:hover { color: rgba(200,224,192,0.7); background: rgba(255,255,255,0.04); }

.sidebar-footer { margin-top: 4px; font-size: 0.6rem; color: #809070; display: flex; align-items: center; justify-content: space-between; gap: 4px; }
.user-row { display: flex; align-items: center; gap: 4px; overflow: hidden; }
.user-row span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 90px; }
.logout-btn { background: none; border: none; color: rgba(200,224,192,0.3); cursor: pointer; font-size: 0.55rem; font-family: inherit; padding: 1px 4px; border-radius: 3px; transition: all 0.15s; }
.logout-btn:hover { color: #d04040; background: rgba(200,80,60,0.06); }
</style>
