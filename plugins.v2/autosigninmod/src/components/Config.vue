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
                v-model="config.enabled"
                label="启用插件"
                color="primary"
                persistent-hint
                inset
              ></v-switch>
            </v-col>
            <v-col cols="12" md="6">
              <v-switch
                v-model="config.notify"
                label="发送通知"
                color="primary"
                persistent-hint
                inset
              ></v-switch>
            </v-col>
            <v-col cols="12" md="6">
              <v-switch
                v-model="config.onlyonce"
                label="立即运行一次"
                color="primary"
                persistent-hint
                inset
              ></v-switch>
            </v-col>
            <v-col cols="12" md="6">
              <v-switch
                v-model="config.clean"
                label="清理本日缓存"
                color="primary"
                persistent-hint
                inset
              ></v-switch>
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12" md="6">
              <VCronField
                v-model="config.cron"
                label="执行周期"
                placeholder="5位cron表达式，留空自动"
                hint="支持：1、5位cron表达式；2、配置间隔（小时），如2.3/9-23；3、周期不填默认9-23点随机执行2次"
                persistent-hint
              ></VCronField>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model.number="config.queue_cnt"
                label="队列数量"
                type="number"
                placeholder="请输入队列数量"
                hint="并发执行的站点数量"
                persistent-hint
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="config.retry_keyword"
                label="重试关键词"
                placeholder="支持正则表达式，命中才重签"
                hint="签到失败时匹配此关键词的站点会被重试"
                persistent-hint
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model.number="config.auto_cf"
                label="自动优选"
                type="number"
                placeholder="0-关闭"
                hint="命中重试关键词次数大于该数量时自动执行Cloudflare IP优选"
                persistent-hint
              ></v-text-field>
            </v-col>
          </v-row>

          <v-divider class="my-4"></v-divider>

          <!-- 站点选择区域 -->
          <div class="text-subtitle-1 font-weight-bold mt-4 mb-2">站点选择</div>
          <v-row>
            <v-col cols="12">
              <v-select
                v-model="config.sign_sites"
                :items="siteOptions"
                label="签到站点"
                placeholder="请选择需要签到的站点"
                item-title="title"
                item-value="value"
                chips
                multiple
                clearable
              ></v-select>
            </v-col>
            <v-col cols="12">
              <v-select
                v-model="config.login_sites"
                :items="siteOptions"
                label="登录站点"
                placeholder="请选择需要模拟登录的站点"
                item-title="title"
                item-value="value"
                chips
                multiple
                clearable
              ></v-select>
            </v-col>
          </v-row>

          <v-divider class="my-4"></v-divider>

          <!-- 提示信息 -->
          <v-alert type="info" variant="tonal" class="mt-4">
            <div class="text-body-2">
              <strong>执行周期说明：</strong><br/>
              1、5位cron表达式；<br/>
              2、配置间隔（小时），如2.3/9-23（9-23点之间每隔2.3小时执行一次）；<br/>
              3、周期不填默认9-23点随机执行2次。<br/>
              每天首次全量执行，其余执行命中重试关键词的站点。
            </div>
          </v-alert>

          <v-alert type="warning" variant="tonal" class="mt-2">
            <div class="text-body-2">
              <strong>注意：</strong>不是所有的站点都会把程序自动登录/签到定义为用户活跃（比如馒头），提示签到/登录成功仍然存在掉号风险！请结合站点公告说明自行把握。
            </div>
          </v-alert>
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
const siteOptions = ref([])

// 配置数据，使用默认值和初始配置合并
const defaultConfig = {
  id: 'AutoSignInMod',
  name: '站点自动签到魔改版',
  enabled: false,
  notify: true,
  cron: '',
  onlyonce: false,
  clean: false,
  queue_cnt: 5,
  sign_sites: [],
  login_sites: [],
  retry_keyword: '错误|失败',
  auto_cf: 0,
}

// 合并默认配置和初始配置
const config = reactive({ ...defaultConfig, ...props.initialConfig })

// 初始化配置
onMounted(async () => {
  try {
    // 获取当前配置
    const data = await props.api.get(`plugin/AutoSignInMod/config`)
    if (data) {
      Object.assign(config, { ...config, ...data })
    }
    
    // 获取站点列表
    siteOptions.value = config.all_sites || []
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
