<template>
  <div class="dashboard-widget">
    <v-card v-if="!config?.attrs?.border" flat>
      <v-card-text class="pa-0">
        <div class="dashboard-content">
          <!-- 加载中状态 -->
          <div v-if="loading" class="d-flex justify-center align-center py-4">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
          </div>

          <!-- 数据内容 -->
          <div v-else>
            <!-- 数据图表 -->
            <div v-if="chartData" class="chart-container">
              <v-chart class="chart" :option="chartOptions" autoresize />
            </div>

            <!-- 数据列表 -->
            <v-list v-if="items.length" density="compact" class="py-0">
              <v-list-item v-for="(item, index) in items" :key="index" :title="item.title" :subtitle="item.subtitle">
                <template v-slot:prepend>
                  <v-avatar :color="getStatusColor(item.status)" size="small">
                    <v-icon size="small" color="white">{{ getStatusIcon(item.status) }}</v-icon>
                  </v-avatar>
                </template>
                <template v-slot:append v-if="item.value">
                  <span class="text-caption">{{ item.value }}</span>
                </template>
              </v-list-item>
            </v-list>
          </div>
        </div>
      </v-card-text>
    </v-card>

    <!-- 带边框的卡片 -->
    <v-card v-else>
      <v-card-item>
        <v-card-title>{{ config?.attrs?.title || '仪表板组件' }}</v-card-title>
        <v-card-subtitle v-if="config?.attrs?.subtitle">{{ config.attrs.subtitle }}</v-card-subtitle>
      </v-card-item>

      <v-card-text>
        <!-- 加载中状态 -->
        <div v-if="loading" class="d-flex justify-center align-center py-4">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>

        <!-- 数据内容 -->
        <div v-else>
          <!-- 数据图表 -->
          <div v-if="chartData" class="chart-container">
            <v-chart class="chart" :option="chartOptions" autoresize />
          </div>

          <!-- 数据列表 -->
          <v-list v-if="items.length" density="compact" class="rounded pa-0">
            <v-list-item v-for="(item, index) in items" :key="index" :title="item.title" :subtitle="item.subtitle">
              <template v-slot:prepend>
                <v-avatar :color="getStatusColor(item.status)" size="small">
                  <v-icon size="small" color="white">{{ getStatusIcon(item.status) }}</v-icon>
                </v-avatar>
              </template>
              <template v-slot:append v-if="item.value">
                <span class="text-caption">{{ item.value }}</span>
              </template>
            </v-list-item>
          </v-list>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'

// 注册ECharts组件
try {
  use([CanvasRenderer, LineChart, PieChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent])
} catch (e) {
  console.warn('ECharts components registration failed', e)
}

// 接收仪表板配置
const props = defineProps({
  config: {
    type: Object,
    default: () => ({}),
  },
  allowRefresh: {
    type: Boolean,
    default: true,
  },
})

// 组件状态
const loading = ref(true)
const items = ref([])
const chartData = ref(null)
let refreshTimer = null

// 获取状态图标
function getStatusIcon(status) {
  const icons = {
    'success': 'mdi-check-circle',
    'warning': 'mdi-alert',
    'error': 'mdi-alert-circle',
    'info': 'mdi-information',
    'running': 'mdi-play-circle',
    'pending': 'mdi-clock-outline',
    'completed': 'mdi-check-circle-outline',
  }
  return icons[status] || 'mdi-help-circle'
}

// 获取状态颜色
function getStatusColor(status) {
  const colors = {
    'success': 'success',
    'warning': 'warning',
    'error': 'error',
    'info': 'info',
    'running': 'primary',
    'pending': 'secondary',
    'completed': 'success',
  }
  return colors[status] || 'grey'
}

// 图表选项
const chartOptions = computed(() => {
  if (!chartData.value) return {}

  const { type, data } = chartData.value

  if (type === 'line') {
    return {
      tooltip: {
        trigger: 'axis',
      },
      xAxis: {
        type: 'category',
        data: data.xAxis,
        axisLabel: {
          color: '#888',
        },
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          color: '#888',
        },
      },
      series: data.series.map(series => ({
        name: series.name,
        type: 'line',
        smooth: true,
        data: series.data,
        areaStyle: { opacity: 0.1 },
      })),
    }
  }

  if (type === 'pie') {
    return {
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)',
      },
      series: [
        {
          name: data.name,
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2,
          },
          label: {
            show: false,
            position: 'center',
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '12',
              fontWeight: 'bold',
            },
          },
          labelLine: {
            show: false,
          },
          data: data.items,
        },
      ],
    }
  }

  return {}
})

// 获取仪表板数据
async function fetchDashboardData() {
  if (!props.allowRefresh) return

  loading.value = true

  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 随机决定显示饼图或折线图
    const showPie = Math.random() > 0.5

    if (showPie) {
      // 饼图数据
      chartData.value = {
        type: 'pie',
        data: {
          name: '文件分布',
          items: [
            { value: Math.floor(Math.random() * 50) + 30, name: '电影' },
            { value: Math.floor(Math.random() * 40) + 20, name: '电视剧' },
            { value: Math.floor(Math.random() * 30) + 10, name: '动漫' },
            { value: Math.floor(Math.random() * 20) + 5, name: '纪录片' },
          ],
        },
      }
    } else {
      // 折线图数据
      const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      chartData.value = {
        type: 'line',
        data: {
          xAxis: days,
          series: [
            {
              name: '下载量',
              data: days.map(() => Math.floor(Math.random() * 10) + 1),
            },
            {
              name: '完成量',
              data: days.map(() => Math.floor(Math.random() * 8) + 1),
            },
          ],
        },
      }
    }

    // 生成列表数据
    const statuses = ['success', 'warning', 'error', 'info', 'running', 'pending', 'completed']
    items.value = Array.from({ length: 5 }, (_, i) => {
      const status = statuses[Math.floor(Math.random() * statuses.length)]
      return {
        title: `项目 ${i + 1}`,
        subtitle: `上次更新: ${new Date().toLocaleTimeString()}`,
        status,
        value: Math.floor(Math.random() * 100) + '%',
      }
    })
  } catch (error) {
    console.error('获取仪表板数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 设置定时刷新
function setupRefreshTimer() {
  if (props.allowRefresh) {
    // 每30秒刷新一次
    refreshTimer = setInterval(() => {
      fetchDashboardData()
    }, 30000)
  }
}

// 初始化
onMounted(() => {
  fetchDashboardData()
  setupRefreshTimer()
})

// 清理
onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>