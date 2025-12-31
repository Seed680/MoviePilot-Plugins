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
          <!-- 搜索和筛选工具栏 -->
          <v-row class="mb-4">
            <v-col cols="12" md="4">
              <v-text-field
                v-model="searchTitle"
                label="搜索标题"
                placeholder="输入标题关键词"
                clearable
                density="compact"
                variant="outlined"
                hide-details
                @keyup.enter="filterRecords"
              >
                <template v-slot:prepend-inner>
                  <v-icon>mdi-magnify</v-icon>
                </template>
              </v-text-field>
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field
                v-model="minSeeders"
                label="最小做种人数"
                type="number"
                density="compact"
                variant="outlined"
                hide-details
                @keyup.enter="filterRecords"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field
                v-model="maxSeeders"
                label="最大做种人数"
                type="number"
                density="compact"
                variant="outlined"
                hide-details
                @keyup.enter="filterRecords"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="2">
              <v-btn 
                color="primary" 
                @click="filterRecords" 
                block
                :disabled="!searchTitle && !minSeeders && !maxSeeders"
              >
                <v-icon start>mdi-filter</v-icon>
                筛选
              </v-btn>
            </v-col>
          </v-row>
          
          <!-- 下载记录展示 -->
          <div class="mt-4">
            <div class="d-flex align-center justify-space-between mb-2">
              <div class="text-h6">下载记录</div>
              <v-btn 
                v-if="selectedRecords.length > 0" 
                color="error" 
                @click="confirmDeleteSelected"
                :disabled="selectedRecords.length === 0"
              >
                <v-icon start>mdi-delete</v-icon>
                删除选中 ({{ selectedRecords.length }})
              </v-btn>
            </div>
            <v-data-table
              v-if="filteredRecords && filteredRecords.length > 0"
              :headers="downloadHeaders"
              :items="filteredRecords"
              :items-per-page="10"
              :footer-props="{
                'items-per-page-options': [5, 10, 20, -1]
              }"
              item-value="title"
              show-select
              v-model="selectedRecords"
              class="elevation-1"
            >
              <template v-slot:item.download_time="{ item }">
                {{ formatTime(item.download_time) }}
              </template>
              <template v-slot:item.torrent_hash="{ item }">
                <span v-if="item.torrent_hash" class="text-success">{{ item.torrent_hash.substring(0, 8) }}...</span>
                <span v-else class="text-grey">-</span>
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
    
    <!-- 删除确认对话框 -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title>确认删除</v-card-title>
        <v-card-text>
          <p v-if="selectedRecords.length > 0">
            确定要删除 {{ selectedRecords.length }} 条记录吗？
            包含种子hash的记录将同时删除下载器中的种子。
          </p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="deleteDialog = false">取消</v-btn>
          <v-btn color="error" @click="deleteConfirmed" :loading="deleting">
            <v-progress-circular v-if="deleting" size="20" width="2" indeterminate></v-progress-circular>
            <span v-else>确认删除</span>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useToast } from 'vue-toastification'
const $toast = useToast()
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
const deleting = ref(false)
const error = ref(null)
const downloadRecords = ref([])
const searchTitle = ref('')
const minSeeders = ref('')
const maxSeeders = ref('')
const selectedRecords = ref([])
const deleteDialog = ref(false)

// 过滤后的记录
const filteredRecords = computed(() => {
  let records = [...downloadRecords.value]
  
  // 按标题搜索
  if (searchTitle.value) {
    const searchLower = searchTitle.value.toLowerCase()
    records = records.filter(record => 
      (record.title && record.title.toLowerCase().includes(searchLower)) ||
      (record.zh_title && record.zh_title.toLowerCase().includes(searchLower))
    )
  }
  
  // 按做种人数筛选
  if (minSeeders.value !== '') {
    const min = parseInt(minSeeders.value)
    if (!isNaN(min)) {
      records = records.filter(record => {
        const seeders = parseInt(record.seeders)
        return !isNaN(seeders) && seeders >= min
      })
    }
  }
  
  if (maxSeeders.value !== '') {
    const max = parseInt(maxSeeders.value)
    if (!isNaN(max)) {
      records = records.filter(record => {
        const seeders = parseInt(record.seeders)
        return !isNaN(seeders) && seeders <= max
      })
    }
  }
  
  return records
})



const downloadHeaders = ref([
  { title: '英文标题', key: 'title' },
  { title: '中文标题', key: 'zh_title' },
  { title: '种子大小', key: 'size' },
  { title: '做种人数', key: 'seeders' },
  { title: '种子Hash', key: 'torrent_hash' },
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
    error.value = '获取下载记录失败:'+ err.message || '获取下载记录失败'
    $toast.error(error.value)
    downloadRecords.value = []
  } finally {
    loading.value = false
    // 通知主应用组件已更新
    emit('action')
  }
}

// 过滤记录
function filterRecords() {
  // 通过computed属性自动过滤，无需额外操作
}



// 删除选中记录
function confirmDeleteSelected() {
  deleteDialog.value = true
}

// 确认删除
async function deleteConfirmed() {
  deleting.value = true
  try {
    // 删除选中记录
    await deleteMultipleRecords(selectedRecords.value)
    selectedRecords.value = []
    
    // 重新加载数据
    await refreshData()
  } catch (err) {
    console.error('删除记录失败:', err)
    error.value = '删除记录失败: ' + err.message
    $toast.error(error.value)
  } finally {
    deleteDialog.value = false
    deleting.value = false
  }
}

// 批量删除记录
async function deleteMultipleRecords(recordTitles) {
  // 根据标题从downloadRecords中获取完整的记录对象
  const records = recordTitles.map(title => 
    downloadRecords.value.find(record => record.title === title)
  ).filter(record => record !== undefined) // 过滤掉未找到的记录
  
  // 分离有hash和无hash的记录
  const recordsWithHash = records.filter(record => record && record.torrent_hash)
  // const recordsWithoutHash = records.filter(record => record && !record.torrent_hash)
  
  // 如果有包含hash的记录，先批量删除种子
  if (recordsWithHash.length > 0) {
    const hashes = recordsWithHash.map(record => record.torrent_hash)
    try {
      const response = await props.api.post(`plugin/HanHanRescueSeeding/delete_torrents`, hashes)
      if (!response.success) {
        console.error('删除种子失败:', response.message)
        $toast.error('删除种子失败:' + response.message)
        // 即使部分失败，也继续删除记录
      } else {
        $toast.success('下载删除种子成功')
      }
    } catch (err) {
      console.error('删除种子API调用失败:', err)
      $toast.error('删除种子API调用失败:' + err.message)
      // 即使API调用失败，也要继续删除记录
    }
  }
  
  // 删除所有选中的记录
  const titles = records.map(record => record.title)
  
  // 同时调用后端API删除数据库中的记录
  try {
    const response = await props.api.post(`plugin/HanHanRescueSeeding/delete_download_records`, titles)
    if (!response.success) {
      console.error('删除下载记录失败:', response.message)
      $toast.error('删除下载记录失败:' + response.message)
    } else {
      $toast.success('删除下载记录成功')
    }
  } catch (err) {
    console.error('删除下载记录API调用失败:', err)
    $toast('删除下载记录API调用失败:' + err.message)
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