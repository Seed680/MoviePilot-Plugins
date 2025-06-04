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
              <v-switch
                v-model="config.watch"
                label="下载器监控"
                color="primary"
                persistent-hint
                inset
              ></v-switch>
            </v-col>
            <v-col cols="6" md="3">
              <v-switch
                v-model="config.onlyonce"
                label="立即运行一次"
                color="primary"
                persistent-hint
                inset
              ></v-switch>
            </v-col>
            
          </v-row>
              
          <!-- <v-divider></v-divider> -->
              
          <v-row>
            <v-col cols="6" md="3">
                <v-select
                  v-model="config.downloaders"
                  :items="config.all_downloaders"
                  label="启用下载器"
                  placeholder="请选择下载器"
                  item-text="title"
                  item-value="value"
                  multiple
                  chips
                ></v-select>
            </v-col>
            <v-col cols="6" md="3">
              <v-select
                v-model="config.interval"
                :items="scheduleTypes"
                label="定时任务类型"
              ></v-select>
            </v-col>
            <v-col cols="6" md="6" v-if="config.interval === '计划任务'">
              <VCronField
                    v-model="config.interval_cron"
                    label="计划任务设置 CRON表达式"
                    hint="设置日志清理的执行周期，如：5 4 * * * (每天凌晨4:05)"
                    persistent-hint
                    density="compact"
                  ></VCronField>
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
          <div class="text-caption d-flex align-center justify-space-between px-3 py-2 bg-primary-lighten-5 flex-wrap">
            <div class="text-subtitle-1 font-weight-bold mt-4 mb-2 align-center">站点设置</div>
            <div>
              <v-btn size="x-small" @click="dialog = true">新增</v-btn>
            </div>
          </div>
          <v-row>
            <v-col cols="6" md="3" v-for="(site, index) in config.siteConfig" :key="index">
              <v-card flat class="rounded mb-3 border bg-transparent">
                <v-card-title class="text-caption d-flex align-center justify-space-between px-3 py-2 bg-primary-lighten-5 flex-wrap">
                  <div class="d-flex align-center">
                    <v-icon icon="mdi-tune" class="mr-2" color="primary" size="small" />
                    <span>{{ site.name }} </span>
                  </div>
                  <div class="d-flex align-center">
                    <v-btn color="error" size="x-small" class="ml-1" @click="removeSite(index)">删除</v-btn>
                  </div>
                </v-card-title>
                <v-card-text class="px-3 py-2">
                    <v-row>
                      <v-col cols="12">
                        <v-switch
                          v-model="site.enabled"
                          label="启用"
                          color="primary"
                          persistent-hint
                          inset
                        ></v-switch>
                      </v-col>
                      <v-col cols="12">
                        <v-text-field label="限速设定" hint="KB/s" v-model="site.speedLimit"></v-text-field>
                      </v-col>
                      <v-col cols="12">
                        <v-textarea label="特殊Tracker" hint="额外的" rows="2"   :model-value="getTrackerText(index)" @update:model-value="setTrackerText($event, index)"></v-textarea>
                      </v-col>
                    </v-row>
                </v-card-text>
              </v-card>
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
  <v-dialog 
    v-model="dialog" 
    max-width="500px"
    transition="scale-transition"
  >
      <v-card class="elevation-8 rounded-lg">
        <v-card-title class="bg-primary text-white text-h6">
          添加新设定
        </v-card-title>
        <v-card-text class="p-6">
          <v-select
            label="站点"
            :items="availableSites"
            item-title="name"
            return-object=true
            v-model="selectSite"
          ></v-select>
        </v-card-text>
        <v-card-actions class="px-6 py-4 justify-end">
          <v-btn 
            text 
            @click="dialog = false"
            class="text-gray-600 hover:text-primary transition-custom"
          >
            取消
          </v-btn>
          <v-btn 
            color="primary" 
            @click="addItem"
            :loading="loading"
            :disabled="!selectSite || loading"
          >
            保存
          </v-btn>
        </v-card-actions>
      </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, reactive, onMounted ,computed ,watch} from 'vue'
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
const selectSite = ref(null)
const scheduleTypes = ['禁用','计划任务','固定间隔']
const intervalUnits = ['分钟','小时']

// 配置数据，使用默认值和初始配置合并
const defaultConfig = {
  id: 'TrackerSpeedLimit',
  name: 'Tracker速度限制',
}

const dialog = ref(false)
// 合并默认配置和初始配置
const config = reactive({ ...defaultConfig, ...props.initialConfig})


// 初始化配置
onMounted(async () => {
  const data = await props.api.get(`plugin/${config.id}/getDownloaders`)
  // config.value = { ...config,...data }
  config.all_downloaders = data;

  const all_sites = await props.api.get(`plugin/${config.id}/getAllSites`)
  config.allSites = all_sites.map(site => ({
    id: site.id,
    name: site.name,
    url: site.url,
  }))
})

// 计算属性：过滤已选择的站点
const availableSites = computed(() => {
  const selectedNames = config.siteConfig?.map(site => site.name);
  return config.allSites.filter(site => !selectedNames?.includes(site.name));
});

// 在setup()中添加：
const getTrackerText = (index) => {
  return config.siteConfig[index].tackerList?.join('\n') || ''
}

const setTrackerText = (value, index) => {
  if (!config.siteConfig[index]) return
  config.siteConfig[index].tackerList = value
    .split('\n')
    .map(t => t.trim())
    .filter(t => t)
}



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
    // await new Promise(resolve => setTimeout(resolve, 1000))

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

function addItem() {
  if (!selectSite.value) return
  config.siteConfig.push({
    id: selectSite.value.id,
    name: selectSite.value.name,
    url: selectSite.value.url,
    enabled: false,
    speedLimit: -1,
    tackerList: [],
  })
  dialog.value = false
  selectSite.value = null
}

// 移除站点
const removeSite = (index) => {
  config.siteConfig.splice(index, 1);
};
</script>
