<template>
  <div class="app" :class="{ 'app--mobile': isMobile }">
    <div v-if="isMobile && sidebarOpen" class="overlay" @click="closeSidebar"></div>
    <Sidebar v-if="showSidebar" :mobileOpen="sidebarOpen" :collapsed="sidebarCollapsed" :onClose="closeSidebar" @nav="closeSidebar" @toggleCollapse="sidebarCollapsed = !sidebarCollapsed" />
    <main class="main" :class="{ 'main--mobile': isMobile }">
      <div class="accent-line"></div>
      <button v-if="isMobile" class="hamburger" @click="openSidebar" aria-label="菜单">
        <span></span><span></span><span></span>
      </button>
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import Sidebar from './Sidebar.vue'

const router = useRouter()
const showSidebar = ref(false)

router.afterEach((to) => {
  showSidebar.value = !!sessionStorage.getItem('userId') && to.path !== '/login'
})
const isMobile = ref(false)
const sidebarOpen = ref(false)
const sidebarCollapsed = ref(false)

let mediaQuery
onMounted(() => {
  mediaQuery = window.matchMedia('(max-width: 767px)')
  isMobile.value = mediaQuery.matches
  mediaQuery.addEventListener('change', onMediaChange)
})

onUnmounted(() => {
  mediaQuery?.removeEventListener('change', onMediaChange)
})

router.afterEach(() => { sidebarOpen.value = false })

function onMediaChange(e) {
  isMobile.value = e.matches
  if (!e.matches) sidebarOpen.value = false
}

function openSidebar() { sidebarOpen.value = true }
function closeSidebar() { sidebarOpen.value = false }
</script>

<style scoped>
.app { display: flex; min-height: 100vh; }
.app--mobile { position: relative; }

.overlay {
  position: fixed; inset: 0; z-index: 150;
  background: rgba(0,0,0,0.35);
  animation: fadeIn 0.25s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

.main {
  flex: 1; position: relative; overflow: hidden;
  background: linear-gradient(180deg, var(--bg-top) 0%, var(--bg-mid) 40%, var(--bg-end) 100%);
  padding: 32px 38px; display: flex; flex-direction: column;
}
.main--mobile { padding: 60px 18px 18px; }

.main::before {
  content: ''; position: absolute; inset: 0; pointer-events: none; z-index: 0; opacity: 0.4;
  background:
    radial-gradient(ellipse at 15% 25%, rgba(138,184,96,0.06) 0%, transparent 45%),
    radial-gradient(ellipse at 80% 65%, rgba(138,184,96,0.04) 0%, transparent 40%),
    repeating-linear-gradient(45deg, rgba(138,184,96,0.01) 0px, rgba(138,184,96,0.01) 2px, transparent 2px, transparent 8px);
}

.accent-line {
  position: absolute; top: 0; left: 10%; right: 10%; height: 1.2px; z-index: 1;
  background: linear-gradient(90deg, transparent, rgba(106,154,64,0.3), transparent);
  animation: lineStretch 0.8s ease-out 0.15s both;
}

/* ── Hamburger ── */
.hamburger {
  position: absolute; top: 12px; left: 14px; z-index: 10;
  width: 40px; height: 40px; padding: 10px 8px;
  background: var(--card-bg); border: 1px solid var(--card-border);
  border-radius: 8px; cursor: pointer;
  display: flex; flex-direction: column; justify-content: center; gap: 5px;
}
.hamburger span {
  display: block; height: 1.5px; background: var(--accent);
  border-radius: 1px; transition: all 0.2s;
}
</style>
