<template>
  <div class="app-container">
    <v-app>
      <v-app-bar color="primary" app>
        <v-app-bar-title>MoviePilot插件组件示例</v-app-bar-title>
      </v-app-bar>

      <v-main>
        <v-container>
          <v-tabs v-model="activeTab" bg-color="primary">
            <v-tab value="config">配置页面</v-tab>
          </v-tabs>

          <v-window v-model="activeTab" class="mt-4">
            <v-window-item value="config">
              <h2 class="text-h5 mb-4">Config组件</h2>
              <div class="component-preview">
                <config-component :api="api" :initial-config="initialConfig" @save="handleConfigSave"></config-component>
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
import ConfigComponent from './components/Config.vue'


// 活动标签页
const activeTab = ref('config')

// 配置初始值
const initialConfig = {
  id: 'trackerspeedlimit',
  name: 'Tracker速度限制',
  // siteConfig: [
  //   { id: 'site1', name: '站点1', url:'xxxx',enabled: true, speedLimit: 100 ,tackerList: ["abcd1234","efgh5678"]},
  //   { id: 'site2', name: '站点2', url:'xxxx',enabled: false, speedLimit: 200, tackerList: [] },
  // ],
  // allSites: [
  //   { id: 'site1', name: '站点1' },
  //   { id: 'site2', name: '站点2' },
  //   { id: 'site3', name: '站点3' },
  // ],

}
console.log(initialConfig.id.value);
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
