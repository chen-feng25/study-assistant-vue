<template>
  <div class="page-header">
    <div class="dot"></div>
    <h2 class="serif">{{ title }}</h2>
  </div>
</template>
<script setup>
defineProps({ title: String })
</script>
<style scoped>
.page-header { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; position: relative; z-index: 1; }
.page-header h2 { font-size: 1.15rem; color: var(--title); font-weight: 700; letter-spacing: 1px; }
.dot { width: 6px; height: 6px; border-radius: 50%; background: var(--matcha); opacity: 0.7; }
</style>
