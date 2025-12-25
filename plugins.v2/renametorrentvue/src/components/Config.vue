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
                    v-model="config.movie_format_torrent_name"
                    label="电影格式化字符"
                    placeholder="{{ title }}{% if year %} ({{ year }}){% endif %} - {{original_name}}"
                    hint="电影种子重命名的格式模板"
                    persistent-hint
                    ref="movieFormatTextarea"
                    id="movie-format-template"
                    @focus="setActiveTemplate('movie')"
                    @click="setActiveTemplate('movie')"
                  ></v-textarea>
                </v-col>
              </v-row>
              
              <v-row>
                <v-col cols="12">
                  <v-textarea
                    v-model="config.tv_format_torrent_name"
                    label="剧集格式化字符"
                    placeholder="{{ title }}{% if year %} ({{ year }}){% endif %}{% if season_episode %} - {{season_episode}}{% endif %} - {{original_name}}"
                    hint="剧集种子重命名的格式模板"
                    persistent-hint
                    ref="tvFormatTextarea"
                    id="tv-format-template"
                    @focus="setActiveTemplate('tv')"
                    @click="setActiveTemplate('tv')"
                  ></v-textarea>
                </v-col>
              </v-row>
              
              <!-- 模板变量选择器 -->
              <v-row>
                <v-col cols="12">
                  <v-card variant="outlined">
                    <v-card-item>
                      <v-card-title class="text-subtitle-2">模板变量</v-card-title>
                    </v-card-item>
                    <v-card-text>
                      <div class="d-flex flex-wrap overflow-x-auto" style="gap: 8px; padding: 8px 0;">
                        <!-- 通用变量 -->
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('title')">标题</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('en_title')">英文标题</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('original_title')">原始标题</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('name')">识别名称</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('en_name')">英文名称</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('original_name')">原始文件名</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('year')">年份</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('resourceType')">资源类型</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('effect')">特效</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('edition')">版本</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('videoFormat')">分辨率</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('releaseGroup')">制作组</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('videoCodec')">视频编码</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('audioCodec')">音频编码</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('tmdbid')">TMDB ID</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('imdbid')">IMDB ID</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('doubanid')">豆瓣ID</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('webSource')">流媒体平台</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('type')">一级分类</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('category')">二级分类</v-chip>
                        <v-chip size="small" variant="flat" color="primary" @click="insertVariable('vote_average')">评分</v-chip>
                        
                        <!-- TV剧集专用变量 -->
                        <div class="mt-2 w-100">
                          <v-divider class="mb-2"></v-divider>
                          <span class="text-subtitle-2 text-primary">TV剧集专用变量</span>
                        </div>
                        <v-chip size="small" variant="flat" color="secondary" @click="insertVariable('season')">季号</v-chip>
                        <v-chip size="small" variant="flat" color="secondary" @click="insertVariable('season_year')">季年份</v-chip>
                        <v-chip size="small" variant="flat" color="secondary" @click="insertVariable('episode')">集号</v-chip>
                        <v-chip size="small" variant="flat" color="secondary" @click="insertVariable('season_episode')">季集</v-chip>
                        <v-chip size="small" variant="flat" color="secondary" @click="insertVariable('episode_title')">集标题</v-chip>
                        <v-chip size="small" variant="flat" color="secondary" @click="insertVariable('episode_date')">集播出日期</v-chip>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
              
              <!-- 结果预览 -->
              <v-row>
                <v-col cols="12" md="6">
                  <v-card variant="outlined">
                    <v-card-item>
                      <v-card-title class="text-subtitle-2">电影预览结果</v-card-title>
                    </v-card-item>
                    <v-card-text>
                      <v-textarea
                        :model-value="previewResult"
                        label="电影预览"
                        readonly
                        variant="outlined"
                        hide-details
                        auto-grow
                        rows="1"
                      ></v-textarea>
                      <div class="text-caption mt-2">
                        注意：预览使用示例数据，实际效果可能有所不同
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
                <v-col cols="12" md="6">
                  <v-card variant="outlined">
                    <v-card-item>
                      <v-card-title class="text-subtitle-2">剧集预览结果</v-card-title>
                    </v-card-item>
                    <v-card-text>
                      <v-textarea
                        :model-value="tvPreviewResult"
                        label="剧集预览"
                        readonly
                        variant="outlined"
                        hide-details
                        auto-grow
                        rows="1"
                      ></v-textarea>
                      <div class="text-caption mt-2">
                        注意：预览使用示例数据，实际效果可能有所不同
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn color="secondary" @click="resetForm">重置配置</v-btn>
        <v-spacer></v-spacer>
        <v-btn color="primary" :disabled="!isFormValid" @click="saveConfig" :loading="saving">保存配置</v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'

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
const formatTextarea = ref(null)
const movieFormatTextarea = ref(null)
const tvFormatTextarea = ref(null)
// 跟踪当前活动的模板
const activeTemplate = ref('movie') // 默认为电影模板

// 可能为空的字段列表
const nullableFields = ['en_name', 'tmdbid', 'imdbid', 'doubanid']

// 示例数据用于预览
const previewData = {
  'original_name': 'Love & Crown S01E33-E34 2025 2160p WEB-DL AAC H265 60fps-XXXWEB',
  'name': 'Love Crown',
  'en_name': 'Love Crown',
  'year': '2025',
  'title': '凤凰台上',
  'en_title': 'Love & Crown',
  'original_title': '凤凰台上',
  'season': '1',
  'season_fmt': 'S01',
  'episode': '33-34',
  'season_episode': 'S01E33-E34',
  'resourceType': 'WEB-DL',
  'edition': 'WEB-DL',
  'videoFormat': '2160p',
  'releaseGroup': 'XXXWEB',
  'videoCodec': 'H265',
  'audioCodec': 'AAC',
  'tmdbid': 271015,
  'imdbid': 'tt32679087',
  'season_year': '2025',
  'type': '电视剧',
  'category': '国产剧',
  'vote_average': 8.7
}

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
  movie_format_torrent_name: '{{ title }}{% if year %} ({{ year }}){% endif %} - {{original_name}}',
  tv_format_torrent_name: '{{ title }}{% if year %} ({{ year }}){% endif %}{% if season_episode %} - {{season_episode}}{% endif %} - {{original_name}}',
  onlyonce: false,
  recovery: false,
  retry: false,
  add_tag_after_rename: false,
  cron: ''
}

// 合并默认配置和初始配置
const config = reactive({ ...defaultConfig, ...props.initialConfig})

// 计算预览结果
const previewResult = computed(() => {
  return renderTemplate(config.movie_format_torrent_name, previewData)
})

// 计算TV预览结果
const tvPreviewResult = computed(() => {
  return renderTemplate(config.tv_format_torrent_name, {
    ...previewData,
    type: '电视剧'
  })
})

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

// 设置当前活动的模板
function setActiveTemplate(templateType) {
  activeTemplate.value = templateType
}

// 在光标位置插入变量
function insertVariable(variable) {
  // 获取当前焦点的元素
  const activeElement = document.activeElement;
  
  // 如果当前焦点在模板输入框中，更新活动模板
  if (activeElement && activeElement.tagName === 'TEXTAREA') {
    if (activeElement.id === 'movie-format-template') {
      activeTemplate.value = 'movie';
    } else if (activeElement.id === 'tv-format-template') {
      activeTemplate.value = 'tv';
    }
  }
  
  // 根据当前活动模板插入变量
  if (activeTemplate.value === 'movie') {
    // 获取电影模板输入框
    const textarea = movieFormatTextarea.value?.$el?.querySelector('textarea');
    if (textarea) {
      const startPos = textarea.selectionStart || 0;
      const endPos = textarea.selectionEnd || 0;
      const textBefore = config.movie_format_torrent_name.substring(0, startPos);
      const textAfter = config.movie_format_torrent_name.substring(endPos);
      
      // 默认插入带条件判断的语句
      let insertText = `{% if ${variable} %}{{ ${variable} }}{% endif %}`;
      
      config.movie_format_torrent_name = textBefore + insertText + textAfter;
      
      // 设置焦点和光标位置
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(startPos + insertText.length, startPos + insertText.length);
      }, 10);
    }
  } else {
    // 获取剧集模板输入框
    const textarea = tvFormatTextarea.value?.$el?.querySelector('textarea');
    if (textarea) {
      const startPos = textarea.selectionStart || 0;
      const endPos = textarea.selectionEnd || 0;
      const textBefore = config.tv_format_torrent_name.substring(0, startPos);
      const textAfter = config.tv_format_torrent_name.substring(endPos);
      
      // 默认插入带条件判断的语句
      let insertText = `{% if ${variable} %}{{ ${variable} }}{% endif %}`;
      
      config.tv_format_torrent_name = textBefore + insertText + textAfter;
      
      // 设置焦点和光标位置
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(startPos + insertText.length, startPos + insertText.length);
      }, 10);
    }
  }
}

// 插入条件语句
function insertConditional(variable) {
  // 获取当前焦点的元素
  const activeElement = document.activeElement;
  
  // 如果当前焦点在模板输入框中，更新活动模板
  if (activeElement && activeElement.tagName === 'TEXTAREA') {
    if (activeElement.id === 'movie-format-template') {
      activeTemplate.value = 'movie';
    } else if (activeElement.id === 'tv-format-template') {
      activeTemplate.value = 'tv';
    }
  }
  
  // 根据当前活动模板插入条件语句
  if (activeTemplate.value === 'movie') {
    // 获取电影模板输入框
    const textarea = movieFormatTextarea.value?.$el?.querySelector('textarea');
    if (textarea) {
      const startPos = textarea.selectionStart || 0;
      const endPos = textarea.selectionEnd || 0;
      const textBefore = config.movie_format_torrent_name.substring(0, startPos);
      const textAfter = config.movie_format_torrent_name.substring(endPos);
      
      // 插入条件语句
      const conditional = `{% if ${variable} %}{{ ${variable} }}{% endif %}`;
      
      config.movie_format_torrent_name = textBefore + conditional + textAfter;
      
      // 设置焦点和光标位置
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(startPos + conditional.length, startPos + conditional.length);
      }, 10);
    }
  } else {
    // 获取剧集模板输入框
    const textarea = tvFormatTextarea.value?.$el?.querySelector('textarea');
    if (textarea) {
      const startPos = textarea.selectionStart || 0;
      const endPos = textarea.selectionEnd || 0;
      const textBefore = config.tv_format_torrent_name.substring(0, startPos);
      const textAfter = config.tv_format_torrent_name.substring(endPos);
      
      // 插入条件语句
      const conditional = `{% if ${variable} %}{{ ${variable} }}{% endif %}`;
      
      config.tv_format_torrent_name = textBefore + conditional + textAfter;
      
      // 设置焦点和光标位置
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(startPos + conditional.length, startPos + conditional.length);
      }, 10);
    }
  }
}

// 渲染模板
function renderTemplate(template, data) {
  // 处理条件语句 {% if variable %}...{% endif %}
  let rendered = template.replace(/{%\s*if\s+(\w+)\s*%}([^]*?){%\s*endif\s*%}/g, (match, variable, content) => {
    // 如果变量存在且不为空，则返回内容部分，否则返回空字符串
    return data[variable] && data[variable].toString().trim() !== '' ? content : '';
  });
  
  // 处理普通变量 {{ variable }}，在使用前增加if判定，变量不为空时才显示
  rendered = rendered.replace(/{{\s*(\w+)\s*}}/g, (match, variable) => {
    // 如果变量存在且不为空则返回其值，否则返回空字符串
    return (data[variable] !== undefined && data[variable].toString().trim() !== '') ? data[variable] : '';
  });
  
  // 移除多余空格
  rendered = rendered.replace(/\s+/g, ' ').trim();
  
  return rendered;
}
</script>