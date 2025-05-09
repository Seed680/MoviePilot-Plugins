<template>
  <div class="plugin-page">
    <v-card>
      <v-card-item>
        <v-card-title>{{ title }}</v-card-title>
        <template #append>
          <v-btn icon color="primary" variant="text" @click="notifyClose">
            <v-icon left>mdi-close</v-icon>
          </v-btn>
        </template>
      </v-card-item>
      <v-card-text>
        <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>
        <v-skeleton-loader v-if="loading" type="card"></v-skeleton-loader>
        <div v-else>
          <!-- 数据统计展示 -->
          <v-row v-if="stats">
            <v-col v-for="(value, key) in stats" :key="key" cols="12" sm="6" md="4">
              <v-card variant="outlined" class="text-center">
                <v-card-text>
                  <div class="text-h4 font-weight-bold">{{ value }}</div>
                  <div class="text-subtitle-1">{{ key }}</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- 最近记录展示 -->
          <div v-if="recentItems && recentItems.length" class="mt-4">
            <div class="text-h6 mb-2">最近记录</div>
            <v-timeline density="compact">
              <v-timeline-item
                v-for="(item, index) in recentItems"
                :key="index"
                :dot-color="getItemColor(item.type)"
                size="small"
              >
                <div class="d-flex align-center">
                  <v-icon :color="getItemColor(item.type)" size="small" class="mr-2">
                    {{ getItemIcon(item.type) }}
                  </v-icon>
                  <span class="font-weight-medium">{{ item.title }}</span>
                </div>
                <div class="text-caption text-secondary">{{ item.time }}</div>
              </v-timeline-item>
            </v-timeline>
          </div>

          <!-- 当前状态 -->
          <div class="mt-4 text-subtitle-2">
            <div>
              <strong>状态:</strong>
              <v-chip size="small" :color="status === 'running' ? 'success' : 'warning'">{{ status }}</v-chip>
            </div>
            <div><strong>最后更新:</strong> {{ lastUpdated }}</div>
          </div>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" @click="refreshData" :loading="loading">
          <v-icon left>mdi-refresh</v-icon>
          刷新数据
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="notifySwitch">
          <v-icon left>mdi-cog</v-icon>
          配置
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 接收初始配置
const props = defineProps({
  model: {
    type: Object,
    default: () => {},
  },
  api: {
    type: Object,
    default: () => {},
  },
})

// 组件状态
const title = ref('插件详情页面')
const loading = ref(true)
const error = ref(null)
const stats = ref(null)
const recentItems = ref([])
const status = ref('running')
const lastUpdated = ref('')

// 自定义事件，用于通知主应用刷新数据
const emit = defineEmits(['action', 'switch', 'close'])

// 获取状态图标
function getItemIcon(type) {
  const icons = {
    'movie': 'mdi-movie',
    'tv': 'mdi-television-classic',
    'download': 'mdi-download',
    'error': 'mdi-alert-circle',
    'success': 'mdi-check-circle',
  }
  return icons[type] || 'mdi-information'
}

// 获取状态颜色
function getItemColor(type) {
  const colors = {
    'movie': 'blue',
    'tv': 'green',
    'download': 'purple',
    'error': 'red',
    'success': 'success',
  }
  return colors[type] || 'grey'
}

// 获取和刷新数据
async function refreshData() {
  loading.value = true
  error.value = null

  try {
    // 模拟数据
    stats.value = {
      '电影': Math.floor(Math.random() * 100) + 50,
      '电视剧': Math.floor(Math.random() * 100) + 30,
      '动漫': Math.floor(Math.random() * 100) + 20,
      '纪录片': Math.floor(Math.random() * 100) + 10,
      '综艺': Math.floor(Math.random() * 100) + 5,
    }

    // 演示使用api模块调用插件接口
    recentItems.value = await props.api.get(`plugin/MyPlugin/history`)

    status.value = Math.random() > 0.2 ? 'running' : 'paused'
    lastUpdated.value = new Date().toLocaleString()
  } catch (err) {
    console.error('获取数据失败:', err)
    error.value = err.message || '获取数据失败'
  } finally {
    loading.value = false
    // 通知主应用组件已更新
    emit('action')
  }
}

// 通知主应用切换到配置页面
function notifySwitch() {
  emit('switch')
}

// 通知主应用关闭组件
function notifyClose() {
  emit('close')
}

// 组件挂载时加载数据
onMounted(() => {
  refreshData()
})
</script>
