<template>
  <div class="plugin-config">
    <v-card>
      <v-card-item>
        <v-card-title>插件配置</v-card-title>
        <template #append>
          <v-btn icon color="primary" variant="text" @click="notifyClose">
            <v-icon left>mdi-close</v-icon>
          </v-btn>
        </template>
      </v-card-item>
      <v-card-text class="overflow-y-auto">
        <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>

        <v-form ref="form" v-model="isFormValid" @submit.prevent="saveConfig">
          <!-- 基本设置区域 -->
          <div class="text-subtitle-1 font-weight-bold mt-4 mb-2">基本设置</div>
          <v-row>
            <v-col cols="12">
              <v-switch
                v-model="config.enable"
                label="启用插件"
                color="primary"
                inset
                hint="启用插件后，插件将开始工作"
                persistent-hint
              ></v-switch>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="config.name"
                label="插件名称"
                variant="outlined"
                :rules="[v => !!v || '名称不能为空']"
                hint="显示在插件列表中的名称"
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-textarea
                v-model="config.description"
                label="插件描述"
                variant="outlined"
                rows="3"
                hint="简要说明插件的功能和用途"
              ></v-textarea>
            </v-col>
          </v-row>
          <!-- 功能配置区域 -->
          <div class="text-subtitle-1 font-weight-bold mt-4 mb-2">功能配置</div>
          <v-row>
            <v-col cols="12">
              <v-select
                v-model="config.update_interval"
                label="更新频率"
                :items="updateIntervalOptions"
                variant="outlined"
                item-title="text"
                item-value="value"
              ></v-select>
            </v-col>
          </v-row>
          <!-- API配置区域 -->
          <div class="text-subtitle-1 font-weight-bold mt-4 mb-2">API设置</div>
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="config.api_url"
                label="API地址"
                variant="outlined"
                hint="外部服务API地址"
                :rules="[v => !v || v.startsWith('http') || '请输入有效的URL']"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="config.api_key"
                label="API密钥"
                variant="outlined"
                :append-inner-icon="showApiKey ? 'mdi-eye-off' : 'mdi-eye'"
                :type="showApiKey ? 'text' : 'password'"
                @click:append-inner="showApiKey = !showApiKey"
              ></v-text-field>
            </v-col>
          </v-row>
          <!-- 高级选项区域 -->
          <v-expansion-panels variant="accordion">
            <v-expansion-panel>
              <v-expansion-panel-title>高级选项</v-expansion-panel-title>
              <v-expansion-panel-text>
                <v-slider
                  v-model="config.concurrent_tasks"
                  label="并发任务数"
                  min="1"
                  max="10"
                  step="1"
                  thumb-label
                ></v-slider>

                <v-combobox
                  v-model="config.tags"
                  label="标签"
                  variant="outlined"
                  chips
                  multiple
                  closable-chips
                ></v-combobox>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn color="secondary" @click="resetForm">重置</v-btn>
        <v-spacer></v-spacer>
        <v-btn color="primary" :disabled="!isFormValid" @click="saveConfig" :loading="saving">保存配置</v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

// 接收初始配置
const props = defineProps({
  initialConfig: {
    type: Object,
    default: () => ({}),
  },
  api: {
    type: Object,
    default: () => {},
  },
})

// 表单状态
const form = ref(null)
const isFormValid = ref(true)
const error = ref(null)
const saving = ref(false)
const showApiKey = ref(false)

// 更新频率选项
const updateIntervalOptions = [
  { text: '5分钟', value: 5 },
  { text: '15分钟', value: 15 },
  { text: '30分钟', value: 30 },
  { text: '1小时', value: 60 },
  { text: '2小时', value: 120 },
  { text: '6小时', value: 360 },
  { text: '12小时', value: 720 },
  { text: '1天', value: 1440 },
]

// 配置数据，使用默认值和初始配置合并
const defaultConfig = {
  name: '我的插件',
  description: '',
  enable: true,
  update_interval: 60,
  api_url: '',
  api_key: '',
  concurrent_tasks: 3,
  tags: [],
}

// 合并默认配置和初始配置
const config = reactive({ ...defaultConfig })

// 初始化配置
onMounted(() => {
  // 加载初始配置
  if (props.initialConfig) {
    Object.keys(props.initialConfig).forEach(key => {
      if (key in config) {
        config[key] = props.initialConfig[key]
      }
    })
  }
})

// 自定义事件，用于保存配置
const emit = defineEmits(['save', 'close', 'switch'])

// 保存配置
async function saveConfig() {
  if (!isFormValid.value) {
    error.value = '请修正表单错误'
    return
  }

  saving.value = true
  error.value = null

  try {
    // 模拟API调用等待
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 发送保存事件
    emit('save', { ...config })
  } catch (err) {
    console.error('保存配置失败:', err)
    error.value = err.message || '保存配置失败'
  } finally {
    saving.value = false
  }
}

// 重置表单
function resetForm() {
  Object.keys(defaultConfig).forEach(key => {
    config[key] = defaultConfig[key]
  })

  if (form.value) {
    form.value.resetValidation()
  }
}

// 通知主应用关闭组件
function notifyClose() {
  emit('close')
}
</script>
