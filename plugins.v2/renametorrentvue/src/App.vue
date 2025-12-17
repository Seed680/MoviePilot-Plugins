<template>
  <div class="app-container">
    <v-app>
      <v-app-bar color="primary" dark app>
        <v-app-bar-title>重命名种子Vue版</v-app-bar-title>
      </v-app-bar>

      <v-main>
        <v-container>
          <v-tabs v-model="activeTab" bg-color="primary">
            <v-tab value="page">主页</v-tab>
            <v-tab value="config">配置</v-tab>
          </v-tabs>

          <v-window v-model="activeTab" class="mt-4">
            <v-window-item value="page">
              <div class="component-preview">
                <page-component 
                  :api="api" 
                  @switch="switchToConfig"
                  @close="handleClose">
                </page-component>
              </div>
            </v-window-item>
            
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
          </v-window>
        </v-container>
      </v-main>

      <v-footer app color="primary" class="text-center d-flex justify-center">
        <span class="text-white">重命名种子Vue版插件 ©{{ new Date().getFullYear() }}</span>
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
const activeTab = ref('page')

// 配置初始值
const initialConfig = {
  id: 'RenameTorrentVue',
  name: '重命名种子Vue版',
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

// 切换到配置页面
function switchToConfig() {
  activeTab.value = 'config'
}

// 处理配置保存
function handleConfigSave(config) {
  console.log('配置已保存:', config)
  showNotification('配置已保存')
}

// 处理关闭
function handleClose() {
  // 可以在这里添加关闭逻辑
  console.log('关闭插件配置界面')
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