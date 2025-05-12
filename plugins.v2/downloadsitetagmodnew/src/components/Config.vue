<template>
  <div class="plugin-config">
    <v-card>
      <v-card-item>
        <v-card-title>{{ config.name }}</v-card-title>
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
            <v-col cols="6" md="3">
              <v-switch
                v-model="config.enable"
                label="启用插件"
                color="primary"
                persistent-hint
                inset
              ></v-switch>
            </v-col>
                
            <v-col cols="6" md="3">
              <v-checkbox
                v-model="config.enable_tag"
                label="自动站点标签"
                color="primary"
              ></v-checkbox>
            </v-col>
            
            <v-col cols="6" md="3">
              <v-checkbox
                v-model="config.enable_media_tag"
                label="自动剧名标签"
                color="primary"
              ></v-checkbox>
            </v-col>
            
            <v-col cols="6" md="3">
              <v-checkbox
                v-model="config.enable_category"
                label="自动设置分类"
                color="primary"
              ></v-checkbox>
            </v-col>
            
            <v-col cols="6" md="6">
              <v-checkbox
                v-model="config.onlyonce"
                label="补全下载历史的标签与分类(一次性任务)"
                color="primary"
                inset
              ></v-checkbox>
            </v-col>
            <v-col>
            <v-switch
                v-model="config.rename_type"
                label="自定义"
                color="primary"
                persistent-hint
                inset
              ></v-switch>
            </v-col>
          </v-row>
              
          <v-divider></v-divider>
              
          <v-row>
            <v-col cols="12">
              <v-select
                v-model="config.downloader"
                :items="config.all_downloaders"
                label="下载器"
                placeholder="请选择下载器"
                item-text="title"
                item-value="value"
                return-object
              ></v-select>
            </v-col>
            
            <v-col cols="6" md="3">
              <v-select
                v-model="config.interval"
                :items="scheduleTypes"
                label="定时任务类型"
              ></v-select>
            </v-col>
            
            <v-col cols="6" md="3" v-if="config.interval === '计划任务'">
              <v-text-field
                v-model="config.interval_cron"
                label="计划任务设置"
                placeholder="例如：5 4 * * *"
                hint="Cron表达式格式"
                persistent-hint
              ></v-text-field>
            </v-col>
            
            <v-col cols="6" md="3" v-if="config.interval === '固定间隔'">
              <v-text-field
                v-model.number="config._interval_time"
                label="固定间隔"
                type="number"
                placeholder="输入间隔时间"
              ></v-text-field>
            </v-col>
            
            <v-col cols="6" md="3" v-if="config.interval === '固定间隔'">
              <v-select
                v-model="config.interval_unit"
                :items="intervalUnits"
                label="单位"
                dense
              ></v-select>
            </v-col>
          </v-row>
          <v-divider class="my-4"></v-divider>
          <v-row  v-if="!config.rename_type">
            <v-col cols="12">
              <!-- 循环生成输入框，每行4个 -->
              <v-row>
                <v-col 
                  cols="12" 
                  md="3" 
                  v-for="(category, index) in config.all_cat" 
                  :key="index"
                >
                  <v-text-field
                    v-model="config.all_cat_rename[index]"
                    :label="category"
                    :placeholder="category"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
          <v-row v-if="config.rename_type">
            <v-col cols="12">
              <v-textarea
                label="按路径自定义分类"
                hint="每一行一个配置，中间以#分隔
                 路径#分类名称"
                persistent-hint
                v-model="config.path_rename"
                variant="filled"
                auto-grow
              ></v-textarea>
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
const showApiKey = ref(false)

const scheduleTypes = ['禁用','计划任务','固定间隔']
const intervalUnits = ['分钟','小时']

// 配置数据，使用默认值和初始配置合并
const defaultConfig = {
  id: 'DownloadSiteTagModNew',
  name: '下载任务分类与标签联邦魔改版',
}

// 合并默认配置和初始配置
const config = reactive({ ...defaultConfig, ...props.initialConfig})


// 初始化配置
onMounted(() => {

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

  Object.keys(props.initialConfig).forEach(key => {
    console.log(key)
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
