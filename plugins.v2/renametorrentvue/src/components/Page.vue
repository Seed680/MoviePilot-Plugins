<template>
  <div class="history-container">
    <v-card>
      <v-card-item>
        <v-card-title>重命名历史记录</v-card-title>
        <template #append>
          <v-btn icon color="primary" variant="text" @click="notifyClose">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </template>
      </v-card-item>
      
      <!-- Tabs -->
      <v-tabs v-model="activeTab" color="primary" align-tabs="center">
        <v-tab value="history">历史记录</v-tab>
        <v-tab value="index">索引缓存</v-tab>
      </v-tabs>
      
      <v-card-text>
        <!-- History Tab -->
        <v-window v-model="activeTab">
          <v-window-item value="history">
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
                @click="deleteSelectedHistory"
                :disabled="selectedHistory.length === 0"
                prepend-icon="mdi-delete"
                class="mr-2 mb-2"
                size="small"
              >
                批量删除 ({{ selectedHistory.length }})
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
                placeholder="搜索名称"
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
              show-select
              item-value="hash"
            >
              <template v-slot:item.success="{ item }">
                <v-chip :color="item.success ? 'success' : 'error'" size="small">
                  {{ item.success ? '成功' : '失败' }}
                </v-chip>
              </template>
              
              <template v-slot:item.date="{ item }">
                {{ formatDate(item.date) }}
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
          </v-window-item>
          
          <!-- Index Cache Tab -->
          <v-window-item value="index">
            <!-- 操作栏 -->
            <div class="d-flex flex-wrap align-center mb-4">
              <VBtn
                color="primary"
                @click="refreshIndex"
                :loading="indexLoading"
                prepend-icon="mdi-refresh"
                class="mr-2 mb-2"
                size="small"
              >
                刷新索引
              </VBtn>
              
              <VTextField
                v-model="indexFilterKeyword"
                placeholder="搜索名称"
                density="compact"
                hide-details
                clearable
                class="mr-2 mb-2"
                style="max-width: 200px;"
              />
              
              <VSpacer />
            </div>
            
            <!-- 索引缓存表格 -->
            <VDataTable
              :headers="indexHeaders"
              :items="filteredIndexRecords"
              :loading="indexLoading"
              class="elevation-1"
              :items-per-page="10"
              :items-per-page-options="[10, 20, 50, -1]"
            >
              <template v-slot:item.actions="{ item }">
                <VBtn
                  color="primary"
                  variant="outlined"
                  size="small"
                  @click="editIndexItem(item)"
                  class="mr-2"
                >
                  编辑
                </VBtn>
              </template>
            </VDataTable>
          </v-window-item>
        </v-window>
      </v-card-text>
      
      <v-card-actions>
        <v-btn color="primary" @click="refreshAllData" :loading="loading || indexLoading">
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
    <VDialog v-model="detailDialog" max-width="600px">
      <VCard>
        <VCardTitle>
          <span class="text-h5">重命名详情</span>
        </VCardTitle>
        
        <VCardText>
          <v-list>
            <v-list-item>
              <v-list-item-title class="font-weight-bold">种子哈希:</v-list-item-title>
              <v-list-item-subtitle>{{ currentRecord.hash }}</v-list-item-subtitle>
            </v-list-item>
            
            <v-list-item>
              <v-list-item-title class="font-weight-bold">原始名称:</v-list-item-title>
              <v-list-item-subtitle>{{ currentRecord.original_name }}</v-list-item-subtitle>
            </v-list-item>
            
            <v-list-item>
              <v-list-item-title class="font-weight-bold">重命名后:</v-list-item-title>
              <v-list-item-subtitle>{{ currentRecord.after_name }}</v-list-item-subtitle>
            </v-list-item>
            
            <v-list-item>
              <v-list-item-title class="font-weight-bold">状态:</v-list-item-title>
              <v-list-item-subtitle>
                <v-chip :color="currentRecord.success ? 'success' : 'error'" size="small">
                  {{ currentRecord.success ? '成功' : '失败' }}
                </v-chip>
              </v-list-item-subtitle>
            </v-list-item>
            
            <v-list-item>
              <v-list-item-title class="font-weight-bold">下载器:</v-list-item-title>
              <v-list-item-subtitle>{{ currentRecord.downloader }}</v-list-item-subtitle>
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
    
    <!-- 编辑索引对话框 -->
    <VDialog v-model="editIndexDialog" max-width="600px">
      <VCard>
        <VCardTitle>
          <span class="text-h5">编辑索引条目</span>
        </VCardTitle>
        
        <VCardText>
          <v-form ref="editIndexForm">
            <v-text-field
              v-model="editingItem.original_name"
              label="原始名称"
              readonly
              variant="outlined"
              density="compact"
              class="mb-4"
            ></v-text-field>
            
            <v-text-field
              v-model="editingItem.after_name"
              label="重命名后"
              variant="outlined"
              density="compact"
              class="mb-4"
              :rules="[v => !!v || '重命名后不能为空']"
            ></v-text-field>
          </v-form>
        </VCardText>
        
        <VCardActions>
          <VSpacer />
          <VBtn
            color="blue darken-1"
            variant="text"
            @click="editIndexDialog = false"
          >
            取消
          </VBtn>
          <VBtn
            color="primary"
            @click="saveIndexItem"
            :loading="savingIndex"
          >
            保存
          </VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
    
    <!-- 删除确认对话框 -->
    <VDialog v-model="deleteConfirmDialog" max-width="400px">
      <VCard>
        <VCardTitle>
          <span class="text-h5">确认删除</span>
        </VCardTitle>
        
        <VCardText>
          确定要删除选中的 {{ selectedHistory.length }} 条历史记录吗？
        </VCardText>
        
        <VCardActions>
          <VSpacer />
          <VBtn
            color="blue darken-1"
            variant="text"
            @click="deleteConfirmDialog = false"
          >
            取消
          </VBtn>
          <VBtn
            color="error"
            @click="confirmDeleteHistory"
            :loading="deleting"
          >
            确认删除
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

// 自定义事件，用于通知主应用刷新数据
const emit = defineEmits(['switch', 'close'])

// Tabs
const activeTab = ref('history')

// 数据表格头部定义
const headers = [
  { title: '原始名称', key: 'original_name' },
  { title: '重命名后', key: 'after_name' },
  { title: '下载器', key: 'downloader' },
  { title: '状态', key: 'success' },
  { title: '处理时间', key: 'date' },
  { title: '操作', key: 'actions', sortable: false }
]

// 索引缓存表格头部定义
const indexHeaders = [
  { title: '原始名称', key: 'original_name' },
  { title: '重命名后', key: 'after_name' },
  { title: '操作', key: 'actions', sortable: false }
]

// 状态变量
const loading = ref(false)
const indexLoading = ref(false)
const savingIndex = ref(false)
const deleting = ref(false)
const historyRecords = ref([])
const indexRecords = ref([])
const detailDialog = ref(false)
const editIndexDialog = ref(false)
const deleteConfirmDialog = ref(false)
const currentRecord = ref({})
const editingItem = ref({
  original_name: '',
  after_name: ''
})
const selectedHistory = ref([])

// 筛选变量
const filterStatus = ref('all')
const filterKeyword = ref('')
const indexFilterKeyword = ref('')

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
    const isSuccess = filterStatus.value === 'success'
    filtered = filtered.filter(record => record.success === isSuccess)
  }
  
  // 关键字筛选
  if (filterKeyword.value) {
    const keyword = filterKeyword.value.toLowerCase()
    filtered = filtered.filter(record => 
      (record.original_name && record.original_name.toLowerCase().includes(keyword)) ||
      (record.after_name && record.after_name.toLowerCase().includes(keyword))
    )
  }
  
  return filtered
})

// 计算属性：过滤后的索引记录
const filteredIndexRecords = computed(() => {
  let filtered = indexRecords.value
  
  // 关键字筛选
  if (indexFilterKeyword.value) {
    const keyword = indexFilterKeyword.value.toLowerCase()
    filtered = filtered.filter(record => 
      (record.original_name && record.original_name.toLowerCase().includes(keyword)) ||
      (record.after_name && record.after_name.toLowerCase().includes(keyword))
    )
  }
  
  return filtered
})

// 刷新历史记录
async function refreshHistory() {
  try {
    loading.value = true
    const response = await props.api.get('plugin/RenameTorrentVue/rename_history')
    historyRecords.value = response || []
  } catch (error) {
    console.error('获取历史记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 刷新索引缓存
async function refreshIndex() {
  try {
    indexLoading.value = true
    const response = await props.api.get('plugin/RenameTorrentVue/rename_index')
    indexRecords.value = response || []
  } catch (error) {
    console.error('获取索引缓存失败:', error)
  } finally {
    indexLoading.value = false
  }
}

// 刷新所有数据
async function refreshAllData() {
  await refreshHistory()
  await refreshIndex()
}

// 显示详情
function showDetail(record) {
  currentRecord.value = record
  detailDialog.value = true
}

// 编辑索引条目
function editIndexItem(item) {
  editingItem.value = { ...item }
  editIndexDialog.value = true
}

// 保存索引条目
async function saveIndexItem() {
  try {
    savingIndex.value = true
    
    // 发送更新请求
    const response = await props.api.post('plugin/RenameTorrentVue/update_rename_index', {
      original_name: editingItem.value.original_name,
      after_name: editingItem.value.after_name
    })
    
    if (response?.success || response.data?.success) {
      // 更新本地索引记录
      const index = indexRecords.value.findIndex(item => 
        item.original_name === editingItem.value.original_name)
      if (index !== -1) {
        indexRecords.value[index].after_name = editingItem.value.after_name
      }
      
      // 关闭对话框
      editIndexDialog.value = false
      
      // 显示成功消息
      const message = response.message || response.data?.message || '更新成功';
      alert(`更新成功: ${message}`)
    } else {
      const message = response.message || response.data?.message || '未知错误';
      alert(`更新失败: ${message}`)
    }
  } catch (error) {
    console.error('更新索引条目失败:', error)
    alert('更新索引条目失败')
  } finally {
    savingIndex.value = false
  }
}

// 格式化日期
function formatDate(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

// 删除选中的历史记录
function deleteSelectedHistory() {
  // 调试输出选中的记录
  console.log('Delete button clicked. Selected history records:', selectedHistory.value);
  
  if (selectedHistory.value && selectedHistory.value.length > 0) {
    deleteConfirmDialog.value = true
  } else {
    alert('请先选择要删除的记录');
  }
}

// 确认删除历史记录
async function confirmDeleteHistory() {
  try {
    deleting.value = true
    
    // 检查是否有要删除的记录
    if (!selectedHistory.value || selectedHistory.value.length === 0) {
      alert('没有选中的记录');
      deleting.value = false;
      return;
    }
    
    // 构造要发送的记录列表
    const recordsToSend = selectedHistory.value.map(hash => ({ hash: hash }));
    
    // 发送删除请求
    const response = await props.api.post('plugin/RenameTorrentVue/delete_rename_history', {
      records: recordsToSend
    })
    
    if (response?.success || response.data?.success) {
      // 清空选中项
      selectedHistory.value = []
      
      // 关闭确认对话框
      deleteConfirmDialog.value = false
      
      // 刷新历史记录
      await refreshHistory()
      
      // 显示成功消息
      const message = response.message || response.data?.message || '删除成功';
      alert(`删除成功: ${message}`)
    } else {
      const message = response.message || response.data?.message || '未知错误';
      alert(`删除失败: ${message}`)
    }
  } catch (error) {
    console.error('删除历史记录失败:', error)
    alert('删除历史记录失败')
  } finally {
    deleting.value = false
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
  refreshIndex()
})
</script>

<style scoped>
.history-container {
  padding: 20px;
}
</style>