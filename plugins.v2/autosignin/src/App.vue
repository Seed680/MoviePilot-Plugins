<template>
  <div class="app-container">
    <v-app>
      <v-app-bar color="primary" dark app>
        <v-app-bar-title>站点自动签到</v-app-bar-title>
      </v-app-bar>

      <v-main>
        <v-container>
          <v-tabs v-model="activeTab" bg-color="primary">
            <v-tab value="config">配置</v-tab>
            <v-tab value="page">记录</v-tab>
          </v-tabs>

          <v-window v-model="activeTab" class="mt-4">
            <v-window-item value="config">
              <div class="component-preview">
                <config-component 
                  :api="api" 
                  :initial-config="initialConfig" 
                  @save="handleConfigSave"
                  @close="handleClose">
                </config-component>
              </div>
            </v-window-item>
            <v-window-item value="page">
              <div class="component-preview">
                <page-component 
                  :api="api"
                  @switch="handleSwitchToConfig"
                  @close="handleClose">
                </page-component>
              </div>
            </v-window-item>
          </v-window>
        </v-container>
      </v-main>

      <v-footer app color="primary" class="text-center d-flex justify-center">
        <span class="text-white">站点自动签到插件 ©{{ new Date().getFullYear() }}</span>
      </v-footer>
    </v-app>

    <!-- 通知弹窗 -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="snackbar.timeout">
      {{ snackbar.text }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false">关闭</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import ConfigComponent from './components/Config.vue'
import PageComponent from './components/Page.vue'

// 活动标签页
const activeTab = ref('config')

// 配置初始值
const initialConfig = {
  id: 'AutoSignIn',
  name: '站点自动签到',
}

// API对象 - 在实际环境中由MoviePilot注入
const api = window.__MOVIEPILOT_API__ || {
  get: async (path) => {
    console.log('API GET:', path)
    return {}
  },
  post: async (path, data) => {
    console.log('API POST:', path, data)
    return { success: true }
  }
}

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

// 处理配置保存
function handleConfigSave(config) {
  console.log('配置已保存:', config)
  showNotification('配置已保存')
}

// 切换到配置页面
function handleSwitchToConfig() {
  activeTab.value = 'config'
}

// 处理关闭
function handleClose() {
  console.log('关闭插件配置界面')
}
</script>

<style scoped>
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
