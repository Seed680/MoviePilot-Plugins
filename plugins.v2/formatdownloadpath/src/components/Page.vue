<template>
  <div class="history-container">
    <v-card>
      <v-card-item>
        <v-card-title>路径格式化历史记录</v-card-title>
        <template #append>
          <v-btn icon color="primary" variant="text" @click="notifyClose">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </template>
      </v-card-item>

      <v-card-text>
        <!-- 操作栏 -->
        <div class="d-flex flex-wrap align-center mb-4">
          <VBtn
            color="primary"
            @click="refreshHistory"
            :loading="loading"
            prepend-icon="mdi-refresh"
            class="mr-2 mb-2"
            size="small"
          >
            刷新记录
          </VBtn>

          <VBtn
            color="error"
            @click="deleteSelected"
            :disabled="selectedHistory.length === 0"
            prepend-icon="mdi-delete"
            class="mr-2 mb-2"
            size="small"
          >
            删除选中 ({{ selectedHistory.length }})
          </VBtn>

          <VSelect
            v-model="filterStatus"
            :items="statusOptions"
            density="compact"
            hide-details
            class="mr-2 mb-2"
            style="max-width: 120px;"
          />

          <VTextField
            v-model="filterKeyword"
            placeholder="搜索标题"
            density="compact"
            hide-details
            clearable
            class="mr-2 mb-2"
            style="max-width: 200px;"
          />

          <VSpacer />
        </div>

        <!-- 历史记录表格 -->
        <VDataTable
          v-model="selectedHistory"
          :headers="headers"
          :items="filteredHistoryRecords"
          :loading="loading"
          class="elevation-1"
          :items-per-page="10"
          :items-per-page-options="[10, 20, 50, -1]"
          item-value="title"
          show-select
        >

          <template v-slot:item.date="{ item }">
            {{ formatDate(item.date) }}
          </template>

          <template v-slot:item.category="{ item }">
            <v-chip
              :color="getCategoryColor(item.category)"
              size="small"
              variant="flat"
            >
              {{ item.category || '未知' }}
            </v-chip>
          </template>

          <template v-slot:item.reason="{ item }">
            <v-tooltip v-if="item.reason" :text="item.reason" location="top">
              <template #activator="{ props }">
                <v-chip
                  v-bind="props"
                  :color="item.reason ? 'error' : 'success'"
                  size="small"
                  variant="flat"
                >
                  {{ item.reason ? '失败' : '成功' }}
                </v-chip>
              </template>
            </v-tooltip>
            <v-chip v-else color="success" size="small" variant="flat">
              成功
            </v-chip>
          </template>

          <template v-slot:item.actions="{ item }">
            <VBtn
              color="primary"
              variant="outlined"
              size="small"
              @click="showDetail(item)"
              class="mr-2"
            >
              详情
            </VBtn>
          </template>
        </VDataTable>
      </v-card-text>

      <v-card-actions>
        <v-btn color="primary" @click="refreshHistory" :loading="loading">
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

    <!-- 详情对话框 -->
    <VDialog v-model="detailDialog" max-width="800px">
      <VCard>
        <VCardTitle>
          <span class="text-h5">路径格式化详情</span>
        </VCardTitle>

        <VCardText>
          <v-list>
            <v-list-item>
              <v-list-item-title class="font-weight-bold">种子名称:</v-list-item-title>
              <v-list-item-subtitle>{{ currentRecord.title }}</v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title class="font-weight-bold">原始路径:</v-list-item-title>
              <v-list-item-subtitle>{{ currentRecord.original_path }}</v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title class="font-weight-bold">格式化后路径:</v-list-item-title>
              <v-list-item-subtitle>{{ currentRecord.formatted_path }}</v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title class="font-weight-bold">下载器:</v-list-item-title>
              <v-list-item-subtitle>{{ currentRecord.downloader }}</v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title class="font-weight-bold">类别:</v-list-item-title>
              <v-list-item-subtitle>
                <v-chip
                  :color="getCategoryColor(currentRecord.category)"
                  size="small"
                  variant="flat"
                >
                  {{ currentRecord.category || '未知' }}
                </v-chip>
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title class="font-weight-bold">状态:</v-list-item-title>
              <v-list-item-subtitle>
                <v-chip
                  :color="currentRecord.reason ? 'error' : 'success'"
                  size="small"
                  variant="flat"
                >
                  {{ currentRecord.reason ? '失败' : '成功' }}
                </v-chip>
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item v-if="currentRecord.reason">
              <v-list-item-title class="font-weight-bold">失败原因:</v-list-item-title>
              <v-list-item-subtitle>{{ currentRecord.reason }}</v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title class="font-weight-bold">处理时间:</v-list-item-title>
              <v-list-item-subtitle>{{ formatDate(currentRecord.date) }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </VCardText>

        <VCardActions>
          <VSpacer />
          <VBtn
            color="blue darken-1"
            variant="text"
            @click="detailDialog = false"
          >
            关闭
          </VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

// 接收API对象
const props = defineProps({
  api: {
    type: Object,
    default: () => {},
  },
})

// 自定义事件，用于通知主应用
const emit = defineEmits(['switch', 'close'])

// 数据表格头部定义
const headers = [
  { title: '', key: 'data-table-select' }, // 添加选择列
  { title: '种子名称', key: 'title' },
  { title: '原始路径', key: 'original_path' },
  { title: '格式化后路径', key: 'formatted_path' },
  { title: '下载器', key: 'downloader' },
  { title: '类别', key: 'category' },
  { title: '状态', key: 'reason' },
  { title: '处理时间', key: 'date' },
  { title: '操作', key: 'actions', sortable: false }
]

// 状态变量
const loading = ref(false)
const historyRecords = ref([])
const detailDialog = ref(false)
const currentRecord = ref({})
const selectedHistory = ref([])

// 筛选变量
const filterStatus = ref('all')
const filterKeyword = ref('')

// 状态筛选选项
const statusOptions = [
  { title: '全部', value: 'all' },
  { title: '成功', value: 'success' },
  { title: '失败', value: 'failed' }
]

// 计算属性：过滤后的历史记录
const filteredHistoryRecords = computed(() => {
  let filtered = historyRecords.value

  // 状态筛选
  if (filterStatus.value !== 'all') {
    if (filterStatus.value === 'success') {
      filtered = filtered.filter(record => !record.reason || record.reason === '')
    } else if (filterStatus.value === 'failed') {
      filtered = filtered.filter(record => record.reason && record.reason !== '')
    }
  }

  // 关键字筛选
  if (filterKeyword.value) {
    const keyword = filterKeyword.value.toLowerCase()
    filtered = filtered.filter(record =>
      (record.title && record.title.toLowerCase().includes(keyword)) ||
      (record.original_path && record.original_path.toLowerCase().includes(keyword)) ||
      (record.formatted_path && record.formatted_path.toLowerCase().includes(keyword))
    )
  }

  return filtered
})

// 刷新历史记录
async function refreshHistory() {
  try {
    loading.value = true
    const response = await props.api.get('plugin/FormatDownloadPath/format_history')
    historyRecords.value = response || []
  } catch (error) {
    console.error('获取历史记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 显示详情
function showDetail(record) {
  currentRecord.value = record
  detailDialog.value = true
}

// 格式化日期
function formatDate(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

// 获取类别颜色
function getCategoryColor(category) {
  if (!category) return 'default'
  const categoryLower = category.toLowerCase()
  if (categoryLower.includes('电影') || categoryLower.includes('movie')) {
    return 'primary'
  } else if (categoryLower.includes('剧') || categoryLower.includes('tv') || categoryLower.includes('series')) {
    return 'secondary'
  }
  return 'default'
}

// 删除选中的历史记录
async function deleteSelected() {
  if (selectedHistory.value.length === 0) {
    return
  }

  if (!confirm(`确定要删除选中的 ${selectedHistory.value.length} 条记录吗？`)) {
    return
  }

  try {
    loading.value = true
    
    // 构造请求体，查找完整记录信息
    const recordsToDelete = []
    for (const selectedItem of selectedHistory.value) {
      // 查找匹配的完整记录（在filteredHistoryRecords中）
      const matchingRecord = filteredHistoryRecords.value.find(record => 
        record.title === selectedItem
      )
      
      if (matchingRecord) {
        recordsToDelete.push({
          title: matchingRecord.title,
          date: matchingRecord.date
        })
      }
    }

    const response = await props.api.post('plugin/FormatDownloadPath/delete_format_history', {
      records: recordsToDelete
    })

    if (response && response.success) {
      // 从本地记录中移除已删除的项
      const keysToDelete = new Set(recordsToDelete.map(r => `${r.title}_${r.date}`))
      historyRecords.value = historyRecords.value.filter(record => 
        !keysToDelete.has(`${record.title}_${record.date}`)
      )
      
      // 清空选择
      selectedHistory.value = []
      
      // 显示成功消息
      alert(response.message || `成功删除 ${recordsToDelete.length} 条记录`)
    } else {
      alert(response.message || '删除失败')
    }
  } catch (error) {
    console.error('删除历史记录失败:', error)
    alert('删除失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
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

// 组件挂载时刷新数据
onMounted(() => {
  refreshHistory()
})
</script>

<style scoped>
.history-container {
  padding: 20px;
}
</style>