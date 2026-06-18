<template>
  <nav class="sidebar">
    <router-link to="/" class="logo-link">
      <MatchaLogo :size="34" />
      <div class="logo-title">学习档案助理</div>
      <div class="logo-sub">Personal Study Archive</div>
    </router-link>
    <div class="sep"></div>

    <router-link v-for="item in navItems" :key="item.to" :to="item.to" class="nav-item" :class="{ active: $route.path === item.to || (item.to === '/entry' && $route.path === '/entry') }">
      <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">
        <path v-if="item.icon==='entry'" d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/>
        <template v-if="item.icon==='report'"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></template>
        <path v-if="item.icon==='chat'" d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
      </svg>
      <span>{{ item.label }}</span>
    </router-link>

    <div class="sidebar-stats">
      <div class="stat-row"><svg class="stats-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg><span>课程</span><span>3</span></div>
      <div class="stat-row"><svg class="stats-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg><span>成绩</span><span>15</span></div>
      <div class="stat-row"><svg class="stats-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg><span>刷题</span><span>48</span></div>
      <div class="stat-row"><svg class="stats-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><span>笔记</span><span>12</span></div>
      <div class="stat-row"><svg class="stats-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg><span>错题</span><span>7 (3)</span></div>
    </div>
    <div class="sidebar-footer">v1.0 · 知识归档</div>
  </nav>
</template>

<script setup>
import MatchaLogo from './MatchaLogo.vue'
const navItems = [
  { to: '/entry', label: '录入数据', icon: 'entry' },
  { to: '/report', label: '分析报告', icon: 'report' },
  { to: '/chat', label: 'AI 问答', icon: 'chat' },
]
</script>

<style scoped>
.sidebar { width: 205px; min-height: 100vh; flex-shrink: 0; background: linear-gradient(180deg, var(--sidebar-start) 0%, var(--sidebar-mid) 45%, var(--sidebar-start) 100%); color: var(--sidebar-text); font-size: 0.78rem; display: flex; flex-direction: column; padding: 24px 14px; animation: sidebarIn 0.6s ease-out both; }
.logo-link { text-align: center; margin-bottom: 14px; text-decoration: none; display: block; }
.logo-link:hover { opacity: 0.85; }
.logo-title { font-weight: 700; color: var(--sidebar-active); font-size: 0.9rem; margin-top: 2px; }
.logo-sub { font-size: 0.55rem; color: #9aae8a; }
.sep { height: 0.5px; background: rgba(200, 224, 192, 0.2); margin: 6px 0 12px; }
.nav-item { padding: 9px 11px; border-radius: 7px; margin: 2px 0; cursor: pointer; color: var(--sidebar-dim); transition: all 0.25s; display: flex; align-items: center; gap: 9px; text-decoration: none; animation: navSlide 0.4s ease-out backwards; }
.nav-item:nth-child(2){animation-delay:0.1s} .nav-item:nth-child(3){animation-delay:0.2s} .nav-item:nth-child(4){animation-delay:0.3s}
.nav-item.active { background: rgba(255,255,255,0.08); color: var(--sidebar-active); border-left: 2px solid var(--matcha); padding-left: 9px; }
.nav-item:not(.active):hover { background: rgba(255,255,255,0.04); color: rgba(200,224,192,0.75); }
.nav-icon { width: 18px; height: 18px; flex-shrink: 0; }
.sidebar-stats { margin-top: 12px; font-size: 0.62rem; color: #9aae8a; }
.stat-row { display: flex; align-items: center; justify-content: space-between; padding: 3px 4px; gap: 6px; }
.stats-icon { width: 12px; height: 12px; flex-shrink: 0; opacity: 0.6; }
.sidebar-footer { margin-top: auto; text-align: center; font-size: 0.55rem; color: #809070; }
</style>
