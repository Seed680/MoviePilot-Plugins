<template>
  <div class="app-container">
    <v-app>
      <v-app-bar color="primary" app>
        <v-app-bar-title>MoviePilot插件组件示例</v-app-bar-title>
      </v-app-bar>

      <v-main>
        <v-container>
          <v-tabs v-model="activeTab" bg-color="primary">
            <v-tab value="page">详情页面</v-tab>
            <v-tab value="config">配置页面</v-tab>
            <v-tab value="dashboard">仪表板</v-tab>
          </v-tabs>

          <v-window v-model="activeTab" class="mt-4">
            <v-window-item value="page">
              <h2 class="text-h5 mb-4">Page组件</h2>
              <div class="component-preview">
                <page-component @action="handleAction"></page-component>
              </div>
            </v-window-item>

            <v-window-item value="config">
              <h2 class="text-h5 mb-4">Config组件</h2>
              <div class="component-preview">
                <config-component :initial-config="initialConfig" @save="handleConfigSave"></config-component>
              </div>
            </v-window-item>

            <v-window-item value="dashboard">
              <h2 class="text-h5 mb-4">Dashboard组件</h2>
              <v-switch v-model="dashboardConfig.attrs.border" label="显示边框" color="primary" class="mb-4"></v-switch>
              <div class="component-preview">
                <dashboard-component :config="dashboardConfig" :allow-refresh="true"></dashboard-component>
              </div>
            </v-window-item>
          </v-window>
        </v-container>
      </v-main>

      <v-footer app color="primary" class="text-center d-flex justify-center">
        <span class="text-white">MoviePilot 模块联邦示例 ©{{ new Date().getFullYear() }}</span>
      </v-footer>
    </v-app>

    <!-- 通知弹窗 -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="snackbar.timeout">
      {{ snackbar.text }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false"> 关闭 </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import PageComponent from './components/Page.vue'
import ConfigComponent from './components/Config.vue'
import DashboardComponent from './components/Dashboard.vue'

// 活动标签页
const activeTab = ref('page')

// 配置初始值
const initialConfig = {
  name: '测试插件',
  description: '这是一个测试配置',
  enable_notifications: true,
  update_interval: 30,
  api_url: 'https://api.example.com',
  api_key: 'test_api_key_123',
  concurrent_tasks: 2,
  tags: ['电影', '测试'],
}

// 仪表板配置
const dashboardConfig = reactive({
  id: 'test_plugin',
  name: '测试插件',
  attrs: {
    title: '仪表板示例',
    subtitle: '插件数据展示',
    border: true,
  },
})

// 通知状态
const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
  timeout: 3000,
})

// 显示通知
function showNotification(text, color = 'success') {
  snackbar.text = text
  snackbar.color = color
  snackbar.show = true
}

// 处理详情页面操作
function handleAction() {
  showNotification('Page组件触发了action事件')
}

// 处理配置保存
function handleConfigSave(config) {
  console.log('配置已保存:', config)
  showNotification('配置已保存')
}
</script>

<style scoped>
/* 为了使测试应用更美观 */
.app-container {
  block-size: 100vh;
  inline-size: 100vw;
}

.component-preview {
  overflow: hidden;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}
</style>
