<template>
  <div class="app-container">
    <v-app>
      <v-app-bar color="primary" dark app>
        <v-app-bar-title>下载路径格式化</v-app-bar-title>
      </v-app-bar>

      <v-main>
        <v-container>
          <v-tabs v-model="activeTab" bg-color="primary">
            <v-tab value="config">配置</v-tab>
            <v-tab value="history">历史记录</v-tab>
          </v-tabs>

          <v-window v-model="activeTab" class="mt-4">
            <!-- 配置页面 -->
            <v-window-item value="config">
              <div class="component-preview">
                <Config @switch="switchToHistory" />
              </div>
            </v-window-item>
            
            <!-- 历史记录页面 -->
            <v-window-item value="history">
              <div class="component-preview">
                <Page @switch="switchToConfig" />
              </div>
            </v-window-item>
          </v-window>
        </v-container>
      </v-main>

      <v-footer app color="primary" class="text-center d-flex justify-center">
        <span class="text-white">下载路径格式化插件 ©{{ new Date().getFullYear() }}</span>
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
import Config from './components/Config.vue'
import Page from './components/Page.vue'

// 活动标签页
const activeTab = ref('config')

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

// 切换到历史记录页面
function switchToHistory() {
  activeTab.value = 'history'
}

// 切换到配置页面
function switchToConfig() {
  activeTab.value = 'config'
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