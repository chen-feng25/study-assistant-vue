<template>
  <div class="chart-card">
    <div class="card-title">📈 成绩趋势</div>
    <div class="chart-wrap">
      <canvas ref="canvasRef"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  grades: { type: Array, required: true },
})

const canvasRef = ref(null)
let chartInstance = null

const COURSE_COLORS = [
  '#8ab860', '#c86848', '#4a6db5', '#d4a044', '#6db5a4',
  '#b56d8a', '#5b8ab8', '#a48a5e', '#8a6db5', '#b58a6d',
]

function buildChart(grades) {
  if (!canvasRef.value || !grades.length) return

  // Group by course, sort by date
  const byCourse = {}
  for (const g of grades) {
    const name = g.course_name || '未分类'
    if (!byCourse[name]) byCourse[name] = []
    byCourse[name].push(g)
  }
  for (const arr of Object.values(byCourse)) {
    arr.sort((a, b) => (a.exam_date || '').localeCompare(b.exam_date || ''))
  }

  // Gather all unique dates for x-axis
  const dateSet = new Set()
  for (const g of grades) {
    if (g.exam_date) dateSet.add(g.exam_date)
  }
  const allDates = [...dateSet].sort()

  const datasets = Object.entries(byCourse).map(([course, items], i) => {
    const dateMap = {}
    for (const item of items) {
      dateMap[item.exam_date] = item.score != null ? (item.score / item.total_score * 100).toFixed(1) : null
    }
    return {
      label: course,
      data: allDates.map(d => dateMap[d] ?? null),
      borderColor: COURSE_COLORS[i % COURSE_COLORS.length],
      backgroundColor: COURSE_COLORS[i % COURSE_COLORS.length] + '20',
      tension: 0.35,
      fill: false,
      pointRadius: 4,
      pointHoverRadius: 6,
      spanGaps: true,
    }
  })

  chartInstance = new Chart(canvasRef.value, {
    type: 'line',
    data: { labels: allDates, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 12,
            boxHeight: 12,
            padding: 16,
            font: { size: 11, family: 'inherit' },
            color: '#809070',
          },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y} 分`,
          },
        },
      },
      scales: {
        y: {
          min: 0,
          max: 100,
          ticks: { stepSize: 20, font: { size: 10 }, color: '#809070' },
          grid: { color: 'rgba(200,224,192,0.15)' },
        },
        x: {
          ticks: { font: { size: 10 }, color: '#809070', maxRotation: 45 },
          grid: { display: false },
        },
      },
    },
  })
}

onMounted(() => {
  if (props.grades.length) buildChart(props.grades)
})

watch(() => props.grades, (newVal) => {
  if (chartInstance) { chartInstance.destroy(); chartInstance = null }
  if (newVal?.length) buildChart(newVal)
}, { deep: true })

onUnmounted(() => {
  if (chartInstance) chartInstance.destroy()
})
</script>

<style scoped>
.chart-card {
  background: var(--card-bg); border-radius: 12px;
  border: 1px solid var(--card-border); padding: 18px; margin-bottom: 14px;
  animation: cardUp 0.5s ease-out both;
}
.chart-wrap {
  position: relative; width: 100%; height: 260px;
}
</style>
