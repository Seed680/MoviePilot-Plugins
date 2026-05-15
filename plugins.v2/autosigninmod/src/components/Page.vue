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
          <!-- 统计信息 -->
          <v-row class="mb-4">
            <v-col cols="12" md="6">
              <v-card variant="outlined" class="pa-4">
                <div class="d-flex align-center">
                  <v-icon color="teal-lighten-3" size="large" class="mr-3">mdi-duck</v-icon>
                  <div>
                    <div class="text-caption text-grey">签到站点数</div>
                    <div class="text-h5 font-weight-bold">{{ signinSiteCount }}</div>
                  </div>
                </div>
              </v-card>
            </v-col>
            <v-col cols="12" md="6">
              <v-card variant="outlined" class="pa-4">
                <div class="d-flex align-center">
                  <v-icon color="light-blue-accent-3" size="large" class="mr-3">mdi-dog</v-icon>
                  <div>
                    <div class="text-caption text-grey">登录站点数</div>
                    <div class="text-h5 font-weight-bold">{{ loginSiteCount }}</div>
                  </div>
                </div>
              </v-card>
            </v-col>
          </v-row>

          <!-- 签到记录 -->
          <div class="mt-4">
            <div class="text-h6 mb-2 d-flex align-center">
              <v-icon color="teal-lighten-3" class="mr-2">mdi-duck</v-icon>
              签到打卡记录
              <v-spacer></v-spacer>
              <v-chip color="teal-lighten-5" size="x-small" variant="elevated">
                {{ signinSiteCount }} 个站点
              </v-chip>
            </div>
            
            <v-expansion-panels v-if="signinPanels.length > 0" variant="accordion" class="mt-2">
              <v-expansion-panel v-for="(panel, index) in signinPanels" :key="index">
                <v-expansion-panel-title>
                  <div class="d-flex align-center w-100">
                    <div class="site-icon">{{ panel.siteInitial }}</div>
                    <span class="font-weight-medium">{{ panel.siteName }}</span>
                    <v-spacer></v-spacer>
                    <v-icon :color="panel.statusColor" size="small" class="mr-2">{{ panel.statusIcon }}</v-icon>
                    <span :class="`text-${panel.statusColor} text-caption`">{{ panel.latestStatus }}</span>
                  </div>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <v-list lines="one" density="compact">
                    <v-list-item v-for="(record, idx) in panel.records" :key="idx" class="site-item px-2 py-1">
                      <div class="d-flex align-center w-100">
                        <v-chip color="grey-lighten-3" size="x-small" class="date-chip mr-2" variant="flat">
                          {{ record.date }}
                        </v-chip>
                        <v-spacer></v-spacer>
                        <v-chip :color="record.color" size="x-small" class="ml-2 status-chip" variant="flat">
                          <v-icon start size="x-small">{{ record.icon }}</v-icon>
                          {{ record.status }}
                        </v-chip>
                      </div>
                    </v-list-item>
                  </v-list>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
            
            <v-alert v-else type="info" variant="tonal" class="mt-4">
              暂无签到数据
            </v-alert>
          </div>

          <!-- 登录记录 -->
          <div class="mt-6">
            <div class="text-h6 mb-2 d-flex align-center">
              <v-icon color="light-blue-accent-3" class="mr-2">mdi-dog</v-icon>
              登录记录
              <v-spacer></v-spacer>
              <v-chip color="light-blue-lighten-4" size="x-small" variant="elevated">
                {{ loginSiteCount }} 个站点
              </v-chip>
            </div>
            
            <v-expansion-panels v-if="loginPanels.length > 0" variant="accordion" class="mt-2">
              <v-expansion-panel v-for="(panel, index) in loginPanels" :key="index">
                <v-expansion-panel-title>
                  <div class="d-flex align-center w-100">
                    <div class="site-icon">{{ panel.siteInitial }}</div>
                    <span class="font-weight-medium">{{ panel.siteName }}</span>
                    <v-spacer></v-spacer>
                    <v-icon :color="panel.statusColor" size="small" class="mr-2">{{ panel.statusIcon }}</v-icon>
                    <span :class="`text-${panel.statusColor} text-caption`">{{ panel.latestStatus }}</span>
                  </div>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <v-list lines="one" density="compact">
                    <v-list-item v-for="(record, idx) in panel.records" :key="idx" class="site-item px-2 py-1">
                      <div class="d-flex align-center w-100">
                        <v-chip color="grey-lighten-3" size="x-small" class="date-chip mr-2" variant="flat">
                          {{ record.date }}
                        </v-chip>
                        <v-spacer></v-spacer>
                        <v-chip :color="record.color" size="x-small" class="ml-2 status-chip" variant="flat">
                          <v-icon start size="x-small">{{ record.icon }}</v-icon>
                          {{ record.status }}
                        </v-chip>
                      </div>
                    </v-list-item>
                  </v-list>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
            
            <v-alert v-else type="info" variant="tonal" class="mt-4">
              暂无登录数据
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
import { ref, onMounted, computed } from 'vue'

// 接收初始配置
const props = defineProps({
  api: {
    type: Object,
    default: () => {},
  },
})

// 组件状态
const title = ref('站点自动签到魔改版')
const loading = ref(true)
const error = ref(null)
const signinData = ref([])
const loginData = ref([])

// 自定义事件
const emit = defineEmits(['action', 'switch', 'close'])

// 计算站点数量
const signinSiteCount = computed(() => {
  const sites = new Set(signinData.value.map(item => item.site))
  return sites.size
})

const loginSiteCount = computed(() => {
  const sites = new Set(loginData.value.map(item => item.site))
  return sites.size
})

// 生成签到面板数据
const signinPanels = computed(() => {
  return generatePanels(signinData.value)
})

// 生成登录面板数据
const loginPanels = computed(() => {
  return generatePanels(loginData.value)
})

// 生成面板数据的通用函数
function generatePanels(data) {
  // 按站点分组
  const siteMap = {}
  data.forEach(record => {
    if (!siteMap[record.site]) {
      siteMap[record.site] = []
    }
    siteMap[record.site].push(record)
  })

  // 转换为面板数组
  return Object.entries(siteMap).map(([siteName, records]) => {
    // 按日期排序，最新的在前面
    records.sort((a, b) => {
      return new Date(b.day_obj || 0) - new Date(a.day_obj || 0)
    })

    // 获取最新状态
    const latestStatus = records[0]?.status || '未知状态'
    
    // 确定状态颜色和图标
    const { statusColor, statusIcon } = getStatusStyle(latestStatus)
    
    // 生成站点首字母
    const siteInitial = siteName ? siteName[0].toUpperCase() : '?'

    // 为每条记录添加样式
    const styledRecords = records.map(record => {
      const { color, icon } = getRecordStyle(record.status)
      return { ...record, color, icon }
    })

    return {
      siteName,
      siteInitial,
      latestStatus,
      statusColor,
      statusIcon,
      records: styledRecords
    }
  })
}

// 获取状态样式
function getStatusStyle(status) {
  let statusColor = 'teal-lighten-3'
  let statusIcon = 'mdi-emoticon-happy-outline'

  if (status.includes('失败') || status.includes('错误')) {
    statusColor = 'deep-orange-lighten-3'
    statusIcon = 'mdi-emoticon-sad-outline'
  } else if (status.includes('Cookie已失效')) {
    statusColor = 'pink-lighten-3'
    statusIcon = 'mdi-cookie-off'
  } else if (status.includes('重试')) {
    statusColor = 'amber-lighten-3'
    statusIcon = 'mdi-emoticon-confused-outline'
  } else if (status.includes('已签到')) {
    statusColor = 'light-blue-lighten-3'
    statusIcon = 'mdi-emoticon-cool-outline'
  } else if (status.includes('成功')) {
    statusColor = 'teal-lighten-3'
    statusIcon = 'mdi-emoticon-happy-outline'
  }

  return { statusColor, statusIcon }
}

// 获取记录样式
function getRecordStyle(status) {
  let color = 'success'
  let icon = 'mdi-check-circle'

  if (status.includes('失败') || status.includes('错误')) {
    color = 'error'
    icon = 'mdi-alert-circle'
  } else if (status.includes('Cookie已失效')) {
    color = 'error'
    icon = 'mdi-cookie-off'
  } else if (status.includes('重试')) {
    color = 'warning'
    icon = 'mdi-refresh'
  } else if (status.includes('已签到')) {
    color = 'info'
    icon = 'mdi-check'
  } else if (status.includes('登录成功')) {
    color = 'success'
    icon = 'mdi-login-variant'
  }

  return { color, icon }
}

// 获取和刷新数据
async function refreshData() {
  loading.value = true
  error.value = null

  try {
    const response = await props.api.get(`plugin/AutoSignInMod/history`)
    
    if (response && response.signin) {
      signinData.value = response.signin
    }
    if (response && response.login) {
      loginData.value = response.login
    }
  } catch (err) {
    console.error('获取历史记录失败:', err)
    error.value = '获取历史记录失败: ' + err.message
    signinData.value = []
    loginData.value = []
  } finally {
    loading.value = false
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

<style scoped>
.site-icon {
  background: linear-gradient(45deg, #80CBC4, #81D4FA);
  color: white !important;
  border-radius: 12px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  font-weight: bold;
  font-size: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.06);
}

.site-item {
  border-radius: 10px;
  transition: all 0.3s ease;
  margin: 5px 0;
}

.site-item:hover {
  transform: scale(1.01);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.date-chip {
  margin: 2px !important;
  border-radius: 14px !important;
  font-size: 0.75rem !important;
}

.status-chip {
  padding: 0 8px;
  border-radius: 14px !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}

.text-teal-lighten-3 {
  color: #80CBC4 !important;
}

.text-deep-orange-lighten-3 {
  color: #FFAB91 !important;
}

.text-pink-lighten-3 {
  color: #F8BBD0 !important;
}

.text-amber-lighten-3 {
  color: #FFE082 !important;
}

.text-light-blue-lighten-3 {
  color: #81D4FA !important;
}
</style>
