<template>
  <svg :width="size" :height="size" viewBox="0 0 100 100" fill="none">
    <path d="M50 25 L50 75 M50 25 L22 17 L22 67 L50 75 M50 25 L78 17 L78 67 L50 75" stroke="#a0c888" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M50 50 Q58 40 50 32 Q42 40 50 50Z" fill="#8ab860" opacity="0.5"/>
    <line x1="50" y1="50" x2="50" y2="75" stroke="#8ab860" stroke-width="1" opacity="0.4"/>
  </svg>
</template>
<script setup>
defineProps({ size: { type: Number, default: 34 } })
</script>
