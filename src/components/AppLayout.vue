<template>
  <div class="app">
    <Sidebar />
    <main class="main">
      <div class="accent-line"></div>
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import Sidebar from './Sidebar.vue'
</script>

<style scoped>
.app { display: flex; min-height: 100vh; }
.main {
  flex: 1; position: relative; overflow: hidden;
  background: linear-gradient(180deg, var(--bg-top) 0%, var(--bg-mid) 40%, var(--bg-end) 100%);
  padding: 32px 38px; display: flex; flex-direction: column;
}
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
</style>
