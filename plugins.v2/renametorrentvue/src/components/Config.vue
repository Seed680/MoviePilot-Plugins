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
          <v-card variant="outlined" class="mb-4">
            <v-card-item>
              <v-card-title class="text-subtitle-1 font-weight-bold">基本设置</v-card-title>
            </v-card-item>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="4">
                  <v-switch
                    v-model="config.enabled"
                    label="启用插件"
                    color="primary"
                    persistent-hint
                    inset
                  ></v-switch>
                </v-col>
                <v-col cols="12" md="4">
                  <v-switch
                    v-model="config.notify"
                    label="启用通知"
                    color="primary"
                    persistent-hint
                    inset
                  ></v-switch>
                </v-col>
                <v-col cols="12" md="4">
                  <v-switch
                    v-model="config.add_tag_after_rename"
                    label="重命名成功后添加标签"
                    color="primary"
                    persistent-hint
                    inset
                  ></v-switch>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- 下载器设置 -->
          <v-card variant="outlined" class="mb-4">
            <v-card-item>
              <v-card-title class="text-subtitle-1 font-weight-bold">下载器设置</v-card-title>
            </v-card-item>
            <v-card-text>
              <v-row>
                <v-col cols="12">
                  <v-select
                    v-model="config.downloader"
                    :items="config.all_downloaders"
                    label="下载器"
                    placeholder="请选择下载器"
                    item-title="title"
                    item-value="value"
                    multiple
                    chips
                    deletable-chips
                  ></v-select>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- 执行方式 -->
          <v-card variant="outlined" class="mb-4">
            <v-card-item>
              <v-card-title class="text-subtitle-1 font-weight-bold">执行方式</v-card-title>
            </v-card-item>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="6">
                  <v-switch
                    v-model="config.cron_enabled"
                    label="启用定时任务"
                    color="primary"
                    persistent-hint
                    inset
                  ></v-switch>
                </v-col>
                <v-col cols="12" md="6">
                  <v-switch
                    v-model="config.event_enabled"
                    label="启用事件监听"
                    color="primary"
                    persistent-hint
                    inset
                  ></v-switch>
                </v-col>
                <v-col cols="12" md="6">
                  <v-switch
                    v-model="config.retry"
                    label="尝试处理失败的种子"
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
                    v-model="config.recovery"
                    label="恢复重命名"
                    color="primary"
                    persistent-hint
                    inset
                  ></v-switch>
                </v-col>
              </v-row>
              
              <v-row v-if="config.cron_enabled">
                <v-col cols="12" md="6">
                  <VCronField
                    v-model="config.cron"
                    label="执行周期"
                    hint="设置插件的执行周期，如：0 2 * * * (每天凌晨2点执行)"
                    persistent-hint
                  ></VCronField>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- 标签过滤 -->
          <v-card variant="outlined" class="mb-4">
            <v-card-item>
              <v-card-title class="text-subtitle-1 font-weight-bold">标签过滤</v-card-title>
            </v-card-item>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="config.exclude_tags"
                    label="排除标签"
                    placeholder="已重命名"
                    hint="排除包含指定标签的种子，多个标签用逗号分隔"
                    persistent-hint
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="config.include_tags"
                    label="包含标签"
                    placeholder=""
                    hint="仅处理包含指定标签的种子，多个标签用逗号分隔"
                    persistent-hint
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- 路径过滤 -->
          <v-card variant="outlined" class="mb-4">
            <v-card-item>
              <v-card-title class="text-subtitle-1 font-weight-bold">路径过滤</v-card-title>
            </v-card-item>
            <v-card-text>
              <v-row>
                <v-col cols="12">
                  <v-textarea
                    v-model="config.exclude_dirs"
                    label="排除目录"
                    placeholder=""
                    hint="排除指定目录下的种子，每行一个目录"
                    persistent-hint
                  ></v-textarea>
                </v-col>
                <v-col cols="12">
                  <v-textarea
                    v-model="config.hash_white_list"
                    label="种子哈希白名单"
                    placeholder=""
                    hint="仅处理指定哈希的种子，每行一个哈希值"
                    persistent-hint
                  ></v-textarea>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- 重命名格式 -->
          <v-card variant="outlined" class="mb-4">
            <v-card-item>
              <v-card-title class="text-subtitle-1 font-weight-bold">重命名格式</v-card-title>
            </v-card-item>
            <v-card-text>
              <v-row>
                <v-col cols="12">
                  <v-textarea
                    v-model="config.format_torrent_name"
                    label="格式化字符"
                    placeholder="{{ title }}{% if year %} ({{ year }}){% endif %}{% if season_episode %} - {{season_episode}}{% endif %}.{{original_name}}"
                    hint="种子重命名的格式模板"
                    persistent-hint
                  ></v-textarea>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
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
  id: 'RenameTorrentVue',
  name: '重命名种子Vue版',
  enabled: false,
  notify: false,
  cron_enabled: false,
  event_enabled: false,
  downloader: [],
  all_downloaders: [],
  exclude_tags: '已重命名',
  include_tags: '',
  exclude_dirs: '',
  hash_white_list: '',
  format_torrent_name: '{{ title }}{% if year %} ({{ year }}){% endif %}{% if season_episode %} - {{season_episode}}{% endif %}.{{original_name}}',
  onlyonce: false,
  recovery: false,
  retry: false,
  add_tag_after_rename: false,
  cron: ''
}

// 合并默认配置和初始配置
const config = reactive({ ...defaultConfig, ...props.initialConfig})

// 初始化配置
onMounted(async () => {
  try {
    const data = await props.api.get(`plugin/${config.id}/get_config`)
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