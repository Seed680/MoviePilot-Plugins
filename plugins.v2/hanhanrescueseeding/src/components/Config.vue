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
                label="立即运行普通保种任务"
                color="primary"
                persistent-hint
                inset
              ></v-switch>
            </v-col>
            <v-col cols="12" md="6">
              <v-switch
                v-model="config.history_rescue_enabled"
                label="立即运行下载历史保种任务"
                color="primary"
                persistent-hint
                inset
              ></v-switch>
            </v-col>
            <v-col cols="12" md="6">
              <v-switch
                v-model="config.enable_notification"
                label="启用通知"
                color="primary"
                persistent-hint
                inset
              ></v-switch>
            </v-col>
            <v-col cols="12" md="6">
              <v-switch
                v-model="config.notify_on_zero_torrents"
                label="种子数为0时发送通知"
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
            <v-col cols="12" md="6" v-if="config.history_rescue_enabled">
              <v-text-field
                v-model="config.user_id"
                label="用户ID"
                type="number"
                placeholder="请输入用户ID"
                hint="用于下载历史保种任务的用户ID"
                persistent-hint
              ></v-text-field>
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
                v-model="config.seeding_count"
                label="做种人数"
                type="text"
                placeholder="请输入做种人数"
                hint="例:3或者1-3"
                persistent-hint
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model.number="config.download_limit"
                label="单次下载数量"
                type="number"
                placeholder="请输入单次下载数量"
                hint="每次执行时最多下载的种子数量，0表示无限制"
                persistent-hint
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="config.save_path"
                label="保存路径"
                placeholder="请输入保存路径"
                hint="设置种子文件的保存路径"
                persistent-hint
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="config.custom_tag"
                label="自定义标签"
                placeholder="请输入自定义标签"
                hint="为下载的种子添加自定义标签"
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
  id: 'HanHanRescueSeeding',
  name: '憨憨保种区',
  enable: false,
  cron: '',
  downloader: '',
  seeding_count: '1-3',
  download_limit: 5,
  all_downloaders: [],
  save_path: '',
  run_once: false,
  custom_tag: '',
  enable_notification: true,
  notify_on_zero_torrents: true,
  history_rescue_enabled: false,
  user_id: ''
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