import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: () => import('../views/Login.vue'), meta: { title: '登录', guest: true } },
  { path: '/entry', component: () => import('../views/Entry.vue'), meta: { title: '录入数据', nav: 'entry', requiresAuth: true } },
  { path: '/report', component: () => import('../views/Report.vue'), meta: { title: '分析报告', nav: 'report', requiresAuth: true } },
  { path: '/chat', component: () => import('../views/Chat.vue'), meta: { title: 'AI 问答', nav: 'chat', requiresAuth: true } },
  { path: '/settings', component: () => import('../views/Settings.vue'), meta: { title: '设置', nav: 'settings', requiresAuth: true } },
]

const router = createRouter({ history: createWebHistory('/'), routes })

router.beforeEach((to, from, next) => {
  const isLoggedIn = !!sessionStorage.getItem('userId')
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
  } else if (to.meta.guest && isLoggedIn) {
    next('/entry')
  } else {
    next()
  }
})

export default router
