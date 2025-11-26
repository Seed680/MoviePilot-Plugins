<template>
  <div class="plugin-page">
    <v-card>
      <v-card-item>
        <v-card-title>{{ title }}</v-card-title>
        <template #append>
          <v-btn icon color="primary" variant="text" @click="notifyClose">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </template>
      </v-card-item>
      <v-card-text>
        <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>
        <v-skeleton-loader v-if="loading" type="table"></v-skeleton-loader>
        <div v-else>
          <!-- 下载记录展示 -->
          <div class="mt-4">
            <div class="text-h6 mb-2">下载记录</div>
            <v-data-table
              v-if="downloadRecords && downloadRecords.length > 0"
              :headers="downloadHeaders"
              :items="downloadRecords"
              :items-per-page="10"
              :footer-props="{
                'items-per-page-options': [5, 10, 20, -1]
              }"
              class="elevation-1"
            >
              <template v-slot:item.download_time="{ item }">
                {{ formatTime(item.download_time) }}
              </template>
            </v-data-table>
            <v-alert v-else type="info" class="mt-4">
              暂无下载记录
            </v-alert>
          </div>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" @click="refreshData" :loading="loading">
          <v-icon start>mdi-refresh</v-icon>
          刷新数据
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="notifySwitch">
          <v-icon start>mdi-cog</v-icon>
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
const title = ref('憨憨保种区')
const loading = ref(true)
const error = ref(null)
const downloadRecords = ref([])
const downloadHeaders = ref([
  { title: '英文标题', key: 'title' },
  { title: '中文标题', key: 'zh_title' },
  { title: '种子大小', key: 'size' },
  { title: '做种人数', key: 'seeders' },
  { title: '下载时间', key: 'download_time' },
])

// 自定义事件，用于通知主应用刷新数据
const emit = defineEmits(['action', 'switch', 'close'])

// 格式化时间
function formatTime(timeStr) {
  // 检查是否为有效日期字符串
  if (!timeStr) return 'N/A'
  
  // 尝试解析日期
  const date = new Date(timeStr)
  if (isNaN(date.getTime())) {
    // 如果是无效日期，直接返回原始字符串
    return timeStr
  }
  
  // 返回本地化的时间字符串
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取和刷新数据
async function refreshData() {
  loading.value = true
  error.value = null

  try {
    // 获取下载记录
    const records = await props.api.get(`plugin/HanHanRescueSeeding/download_records`)
    downloadRecords.value = records || []
  } catch (err) {
    console.error('获取下载记录失败:', err)
    error.value = err.message || '获取下载记录失败'
    downloadRecords.value = []
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