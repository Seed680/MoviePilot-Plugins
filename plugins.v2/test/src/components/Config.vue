<template>
  <div class="plugin-config">
    <v-card>
      <v-card-item>
        <v-card-title>{{ config.name }}</v-card-title>
        <template #append>
          <v-btn icon color="primary" variant="text" @click="notifyClose">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </template>
      </v-card-item>
      <v-card-text class="overflow-y-auto">
        <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>

        <v-form ref="form" v-model="isFormValid" @submit.prevent="saveConfig">
          <!-- 基本设置区域 -->
          <div class="text-subtitle-1 font-weight-bold mt-4 mb-2">基本设置</div>
          <v-row>
            <v-col cols="12" md="6">
              <v-switch
                v-model="config.enable"
                label="启用插件"
                color="primary"
                persistent-hint
                inset
              ></v-switch>
            </v-col>
            <v-col cols="12" md="6">
              <v-switch
                v-model="config.run_once"
                label="立即运行一次"
                color="primary"
                persistent-hint
                inset
              ></v-switch>
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12">
              <v-select
                v-model="config.downloader"
                :items="config.all_downloaders"
                label="下载器"
                placeholder="请选择下载器"
                item-title="title"
                item-value="value"
                chips
              ></v-select>
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12" md="6">
              <VCronField
                v-model="config.cron"
                label="执行周期"
                hint="设置插件的执行周期，如：0 2 * * * (每天凌晨2点执行)"
                persistent-hint
              ></VCronField>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="config.test_value"
                label="测试值"
                type="text"
                placeholder="请输入测试值"
                hint="这是一个测试配置项"
                persistent-hint
              ></v-text-field>
            </v-col>
          </v-row>

          <v-divider class="my-4"></v-divider>
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
  api: { 
    type: [Object, Function],
    required: true,
  },
  initialConfig: {
    type: Object,
    default: () => ({}),
  }
})

// 表单状态
const form = ref(null)
const isFormValid = ref(true)
const error = ref(null)
const saving = ref(false)

// 配置数据，使用默认值和初始配置合并
const defaultConfig = {
  id: 'test',
  name: '测试插件',
  enable: false,
  cron: '',
  downloader: '',
  all_downloaders: [],
  test_value: '',
  run_once: false
}

// 合并默认配置和初始配置
const config = reactive({ ...defaultConfig, ...props.initialConfig})

// 初始化配置
onMounted(async () => {
  try {
    const data = await props.api.get(`plugin/${config.id}/config`)
    Object.assign(config, {...config, ...data})
  } catch (err) {
    console.error('获取配置失败:', err)
    error.value = err.message || '获取配置失败'
  }
})

// 自定义事件，用于保存配置
const emit = defineEmits(['save', 'close'])

// 保存配置
async function saveConfig() {
  if (!isFormValid.value) {
    error.value = '请修正表单错误'
    return
  }

  saving.value = true
  error.value = null

  try {
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
  Object.keys(props.initialConfig).forEach(key => {
    config[key] = props.initialConfig[key]
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