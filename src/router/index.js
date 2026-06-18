import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: () => import('../views/Login.vue'), meta: { title: '登录' } },
  { path: '/entry', component: () => import('../views/Entry.vue'), meta: { title: '录入数据', nav: 'entry' } },
  { path: '/report', component: () => import('../views/Report.vue'), meta: { title: '分析报告', nav: 'report' } },
  { path: '/chat', component: () => import('../views/Chat.vue'), meta: { title: 'AI 问答', nav: 'chat' } },
]

export default createRouter({ history: createWebHistory('/'), routes })
