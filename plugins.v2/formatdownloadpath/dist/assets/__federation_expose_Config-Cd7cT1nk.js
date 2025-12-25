import { importShared } from './__federation_fn_import-JrT3xvdd.js';

const {toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,createElementVNode:_createElementVNode,withModifiers:_withModifiers,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "plugin-config" };
const _hoisted_2 = {
  class: "d-flex flex-wrap overflow-x-auto",
  style: {"gap":"8px","padding":"8px 0"}
};
const _hoisted_3 = { class: "mt-2 w-100" };

const {ref,reactive,onMounted,computed} = await importShared('vue');


// 接收初始配置

const _sfc_main = {
  __name: 'Config',
  props: {
  api: { 
    type: [Object, Function],
    required: true,
  },
  initialConfig: {
    type: Object,
    default: () => ({}),
  }
},
  emits: ['save', 'close'],
  setup(__props, { emit: __emit }) {

const props = __props;

// 表单状态
const form = ref(null);
const isFormValid = ref(true);
const error = ref(null);
const saving = ref(false);
const movieFormatTextarea = ref(null);
const tvFormatTextarea = ref(null);
// 跟踪当前活动的模板
const activeTemplate = ref('movie'); // 默认为电影模板
// 下载器列表
const downloaders = ref([]);
const loadingDownloaders = ref(false);

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
  'Edition': 'WEB-DL',
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
};

// 配置数据，使用默认值和初始配置合并
const defaultConfig = {
  id: 'FormatDownloadPath',
  name: '下载路径格式化',
  enabled: false,
  enable_listener: false,
  downloaders: [],
  movie_format_path_template: '{{ title }}{% if year %}({{ year }}){% endif %}',
  tv_format_path_template: '{{ title }}{% if year %}({{ year }}){% endif %}',
  exclude_dirs: ''
};

// 合并默认配置和初始配置
const config = reactive({ ...defaultConfig, ...props.initialConfig});

// 计算预览结果
const previewResult = computed(() => {
  // 使用当前活动的模板进行预览
  // 这里我们先使用电影模板进行预览
  return renderTemplate(config.movie_format_path_template, previewData)
});
    
// 计算TV预览结果
const tvPreviewResult = computed(() => {
  return renderTemplate(config.tv_format_path_template, {
    ...previewData,
    type: '电视剧'
  })
});

// 初始化配置
onMounted(async () => {
  try {
    // 先获取下载器列表
    await loadDownloaders();
    
    const data = await props.api.get(`plugin/${config.id}/get_config`);
    Object.assign(config, {...config, ...data});
  } catch (err) {
    console.error('获取配置失败:', err);
    error.value = err.message || '获取配置失败';
  }
});

// 加载下载器列表
async function loadDownloaders() {
  try {
    loadingDownloaders.value = true;
    const response = await props.api.get(`plugin/${config.id}/get_downloaders`);
    // 直接使用返回的响应数据，因为后端现在返回正确的格式
    downloaders.value = Array.isArray(response) ? response : [];
  } catch (err) {
    console.error('获取下载器列表失败:', err);
    error.value = err.message || '获取下载器列表失败';
  } finally {
    loadingDownloaders.value = false;
  }
}

// 自定义事件，用于保存配置
const emit = __emit;

// 保存配置
async function saveConfig() {
  if (!isFormValid.value) {
    error.value = '请修正表单错误';
    return
  }

  saving.value = true;
  error.value = null;

  try {
    // 发送保存事件
    emit('save', { ...config });
  } catch (err) {
    console.error('保存配置失败:', err);
    error.value = err.message || '保存配置失败';
  } finally {
    saving.value = false;
  }
}

// 重置表单
function resetForm() {
  Object.keys(props.initialConfig).forEach(key => {
    config[key] = props.initialConfig[key];
  });

  if (form.value) {
    form.value.resetValidation();
  }
}

// 通知主应用关闭组件
function notifyClose() {
  emit('close');
}

// 设置当前活动的模板
function setActiveTemplate(templateType) {
  activeTemplate.value = templateType;
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
      const textBefore = config.movie_format_path_template.substring(0, startPos);
      const textAfter = config.movie_format_path_template.substring(endPos);
      
      // 默认插入带条件判断的语句
      let insertText = `{% if ${variable} %}{{ ${variable} }}{% endif %}`;
      
      config.movie_format_path_template = textBefore + insertText + textAfter;
      
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
      const textBefore = config.tv_format_path_template.substring(0, startPos);
      const textAfter = config.tv_format_path_template.substring(endPos);
      
      // 默认插入带条件判断的语句
      let insertText = `{% if ${variable} %}{{ ${variable} }}{% endif %}`;
      
      config.tv_format_path_template = textBefore + insertText + textAfter;
      
      // 设置焦点和光标位置
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(startPos + insertText.length, startPos + insertText.length);
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

return (_ctx, _cache) => {
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_card_item = _resolveComponent("v-card-item");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_select = _resolveComponent("v-select");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_textarea = _resolveComponent("v-textarea");
  const _component_v_chip = _resolveComponent("v-chip");
  const _component_v_divider = _resolveComponent("v-divider");
  const _component_v_form = _resolveComponent("v-form");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_card_actions = _resolveComponent("v-card-actions");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_v_card, null, {
      default: _withCtx(() => [
        _createVNode(_component_v_card_item, null, {
          append: _withCtx(() => [
            _createVNode(_component_v_btn, {
              icon: "",
              color: "primary",
              variant: "text",
              onClick: notifyClose
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, null, {
                  default: _withCtx(() => [...(_cache[38] || (_cache[38] = [
                    _createTextVNode("mdi-close", -1)
                  ]))]),
                  _: 1
                })
              ]),
              _: 1
            })
          ]),
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, null, {
              default: _withCtx(() => [
                _createTextVNode(_toDisplayString(config.name), 1)
              ]),
              _: 1
            })
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_text, { class: "overflow-y-auto" }, {
          default: _withCtx(() => [
            (error.value)
              ? (_openBlock(), _createBlock(_component_v_alert, {
                  key: 0,
                  type: "error",
                  class: "mb-4"
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(error.value), 1)
                  ]),
                  _: 1
                }))
              : _createCommentVNode("", true),
            _createVNode(_component_v_form, {
              ref_key: "form",
              ref: form,
              modelValue: isFormValid.value,
              "onUpdate:modelValue": _cache[37] || (_cache[37] = $event => ((isFormValid).value = $event)),
              onSubmit: _withModifiers(saveConfig, ["prevent"])
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card, {
                  variant: "outlined",
                  class: "mb-4"
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_item, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_card_title, { class: "text-subtitle-1 font-weight-bold" }, {
                          default: _withCtx(() => [...(_cache[39] || (_cache[39] = [
                            _createTextVNode("基本设置", -1)
                          ]))]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_card_text, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_row, null, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_col, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_switch, {
                                  modelValue: config.enabled,
                                  "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((config.enabled) = $event)),
                                  label: "启用插件",
                                  color: "primary",
                                  "persistent-hint": "",
                                  inset: ""
                                }, null, 8, ["modelValue"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_v_col, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_switch, {
                                  modelValue: config.enable_listener,
                                  "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.enable_listener) = $event)),
                                  label: "启用监听",
                                  color: "primary",
                                  "persistent-hint": "",
                                  inset: ""
                                }, null, 8, ["modelValue"])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        }),
                        (config.enable_listener)
                          ? (_openBlock(), _createBlock(_component_v_row, { key: 0 }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_col, { cols: "12" }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_v_select, {
                                      modelValue: config.downloaders,
                                      "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.downloaders) = $event)),
                                      items: downloaders.value,
                                      "item-title": "title",
                                      "item-value": "value",
                                      label: "选择监听的下载器",
                                      multiple: "",
                                      chips: "",
                                      clearable: "",
                                      loading: loadingDownloaders.value,
                                      hint: "选择要监听的下载器，留空则不监听下载器",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue", "items", "loading"])
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            }))
                          : _createCommentVNode("", true)
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_card, {
                  variant: "outlined",
                  class: "mb-4"
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_item, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_card_title, { class: "text-subtitle-1 font-weight-bold" }, {
                          default: _withCtx(() => [...(_cache[40] || (_cache[40] = [
                            _createTextVNode("路径格式化配置", -1)
                          ]))]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_card_text, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_row, null, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_col, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_textarea, {
                                  modelValue: config.movie_format_path_template,
                                  "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.movie_format_path_template) = $event)),
                                  label: "电影格式化路径模板",
                                  placeholder: "{{ title }}{% if year %}/{{ year }}{% endif %}",
                                  hint: "使用Jinja2模板语法定义电影下载路径格式",
                                  "persistent-hint": "",
                                  ref_key: "movieFormatTextarea",
                                  ref: movieFormatTextarea,
                                  id: "movie-format-template",
                                  onFocus: _cache[4] || (_cache[4] = $event => (setActiveTemplate('movie'))),
                                  onClick: _cache[5] || (_cache[5] = $event => (setActiveTemplate('movie')))
                                }, null, 8, ["modelValue"])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_v_row, null, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_col, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_textarea, {
                                  modelValue: config.tv_format_path_template,
                                  "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.tv_format_path_template) = $event)),
                                  label: "剧集格式化路径模板",
                                  placeholder: "{{ title }}{% if year %}/{{ year }}{% endif %}/Season {{ season or 1 }}",
                                  hint: "使用Jinja2模板语法定义剧集下载路径格式",
                                  "persistent-hint": "",
                                  ref_key: "tvFormatTextarea",
                                  ref: tvFormatTextarea,
                                  id: "tv-format-template",
                                  onFocus: _cache[7] || (_cache[7] = $event => (setActiveTemplate('tv'))),
                                  onClick: _cache[8] || (_cache[8] = $event => (setActiveTemplate('tv')))
                                }, null, 8, ["modelValue"])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_v_row, null, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_col, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_card, { variant: "outlined" }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_v_card_item, null, {
                                      default: _withCtx(() => [
                                        _createVNode(_component_v_card_title, { class: "text-subtitle-2" }, {
                                          default: _withCtx(() => [...(_cache[41] || (_cache[41] = [
                                            _createTextVNode("模板变量", -1)
                                          ]))]),
                                          _: 1
                                        })
                                      ]),
                                      _: 1
                                    }),
                                    _createVNode(_component_v_card_text, null, {
                                      default: _withCtx(() => [
                                        _createElementVNode("div", _hoisted_2, [
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[9] || (_cache[9] = $event => (insertVariable('title')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[42] || (_cache[42] = [
                                              _createTextVNode("标题", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[10] || (_cache[10] = $event => (insertVariable('en_title')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[43] || (_cache[43] = [
                                              _createTextVNode("英文标题", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[11] || (_cache[11] = $event => (insertVariable('original_title')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[44] || (_cache[44] = [
                                              _createTextVNode("原始标题", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[12] || (_cache[12] = $event => (insertVariable('name')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[45] || (_cache[45] = [
                                              _createTextVNode("识别名称", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[13] || (_cache[13] = $event => (insertVariable('en_name')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[46] || (_cache[46] = [
                                              _createTextVNode("英文名称", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[14] || (_cache[14] = $event => (insertVariable('original_name')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[47] || (_cache[47] = [
                                              _createTextVNode("原始文件名", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[15] || (_cache[15] = $event => (insertVariable('year')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[48] || (_cache[48] = [
                                              _createTextVNode("年份", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[16] || (_cache[16] = $event => (insertVariable('resourceType')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[49] || (_cache[49] = [
                                              _createTextVNode("资源类型", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[17] || (_cache[17] = $event => (insertVariable('effect')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[50] || (_cache[50] = [
                                              _createTextVNode("特效", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[18] || (_cache[18] = $event => (insertVariable('edition')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[51] || (_cache[51] = [
                                              _createTextVNode("版本", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[19] || (_cache[19] = $event => (insertVariable('videoFormat')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[52] || (_cache[52] = [
                                              _createTextVNode("分辨率", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[20] || (_cache[20] = $event => (insertVariable('releaseGroup')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[53] || (_cache[53] = [
                                              _createTextVNode("制作组", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[21] || (_cache[21] = $event => (insertVariable('videoCodec')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[54] || (_cache[54] = [
                                              _createTextVNode("视频编码", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[22] || (_cache[22] = $event => (insertVariable('audioCodec')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[55] || (_cache[55] = [
                                              _createTextVNode("音频编码", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[23] || (_cache[23] = $event => (insertVariable('tmdbid')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[56] || (_cache[56] = [
                                              _createTextVNode("TMDB ID", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[24] || (_cache[24] = $event => (insertVariable('imdbid')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[57] || (_cache[57] = [
                                              _createTextVNode("IMDB ID", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[25] || (_cache[25] = $event => (insertVariable('doubanid')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[58] || (_cache[58] = [
                                              _createTextVNode("豆瓣ID", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[26] || (_cache[26] = $event => (insertVariable('webSource')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[59] || (_cache[59] = [
                                              _createTextVNode("流媒体平台", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[27] || (_cache[27] = $event => (insertVariable('type')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[60] || (_cache[60] = [
                                              _createTextVNode("一级分类", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[28] || (_cache[28] = $event => (insertVariable('category')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[61] || (_cache[61] = [
                                              _createTextVNode("二级分类", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "primary",
                                            onClick: _cache[29] || (_cache[29] = $event => (insertVariable('vote_average')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[62] || (_cache[62] = [
                                              _createTextVNode("评分", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createElementVNode("div", _hoisted_3, [
                                            _createVNode(_component_v_divider, { class: "mb-2" }),
                                            _cache[63] || (_cache[63] = _createElementVNode("span", { class: "text-subtitle-2 text-primary" }, "TV剧集专用变量", -1))
                                          ]),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "secondary",
                                            onClick: _cache[30] || (_cache[30] = $event => (insertVariable('season')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[64] || (_cache[64] = [
                                              _createTextVNode("季号", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "secondary",
                                            onClick: _cache[31] || (_cache[31] = $event => (insertVariable('season_year')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[65] || (_cache[65] = [
                                              _createTextVNode("季年份", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "secondary",
                                            onClick: _cache[32] || (_cache[32] = $event => (insertVariable('episode')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[66] || (_cache[66] = [
                                              _createTextVNode("集号", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "secondary",
                                            onClick: _cache[33] || (_cache[33] = $event => (insertVariable('season_episode')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[67] || (_cache[67] = [
                                              _createTextVNode("季集", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "secondary",
                                            onClick: _cache[34] || (_cache[34] = $event => (insertVariable('episode_title')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[68] || (_cache[68] = [
                                              _createTextVNode("集标题", -1)
                                            ]))]),
                                            _: 1
                                          }),
                                          _createVNode(_component_v_chip, {
                                            size: "small",
                                            variant: "flat",
                                            color: "secondary",
                                            onClick: _cache[35] || (_cache[35] = $event => (insertVariable('episode_date')))
                                          }, {
                                            default: _withCtx(() => [...(_cache[69] || (_cache[69] = [
                                              _createTextVNode("集播出日期", -1)
                                            ]))]),
                                            _: 1
                                          })
                                        ])
                                      ]),
                                      _: 1
                                    })
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_v_row, null, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_col, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_card, { variant: "outlined" }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_v_card_item, null, {
                                      default: _withCtx(() => [
                                        _createVNode(_component_v_card_title, { class: "text-subtitle-2" }, {
                                          default: _withCtx(() => [...(_cache[70] || (_cache[70] = [
                                            _createTextVNode("电影预览结果", -1)
                                          ]))]),
                                          _: 1
                                        })
                                      ]),
                                      _: 1
                                    }),
                                    _createVNode(_component_v_card_text, null, {
                                      default: _withCtx(() => [
                                        _createVNode(_component_v_textarea, {
                                          "model-value": previewResult.value,
                                          label: "电影预览",
                                          readonly: "",
                                          variant: "outlined",
                                          "hide-details": "",
                                          "auto-grow": "",
                                          rows: "1"
                                        }, null, 8, ["model-value"]),
                                        _cache[71] || (_cache[71] = _createElementVNode("div", { class: "text-caption mt-2" }, " 注意：预览使用示例数据，实际效果可能有所不同 ", -1))
                                      ]),
                                      _: 1
                                    })
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_v_col, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_card, { variant: "outlined" }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_v_card_item, null, {
                                      default: _withCtx(() => [
                                        _createVNode(_component_v_card_title, { class: "text-subtitle-2" }, {
                                          default: _withCtx(() => [...(_cache[72] || (_cache[72] = [
                                            _createTextVNode("剧集预览结果", -1)
                                          ]))]),
                                          _: 1
                                        })
                                      ]),
                                      _: 1
                                    }),
                                    _createVNode(_component_v_card_text, null, {
                                      default: _withCtx(() => [
                                        _createVNode(_component_v_textarea, {
                                          "model-value": tvPreviewResult.value,
                                          label: "剧集预览",
                                          readonly: "",
                                          variant: "outlined",
                                          "hide-details": "",
                                          "auto-grow": "",
                                          rows: "1"
                                        }, null, 8, ["model-value"]),
                                        _cache[73] || (_cache[73] = _createElementVNode("div", { class: "text-caption mt-2" }, " 注意：预览使用示例数据，实际效果可能有所不同 ", -1))
                                      ]),
                                      _: 1
                                    })
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_card, {
                  variant: "outlined",
                  class: "mb-4"
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_item, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_card_title, { class: "text-subtitle-1 font-weight-bold" }, {
                          default: _withCtx(() => [...(_cache[74] || (_cache[74] = [
                            _createTextVNode("排除目录设置", -1)
                          ]))]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_card_text, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_row, null, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_col, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_textarea, {
                                  modelValue: config.exclude_dirs,
                                  "onUpdate:modelValue": _cache[36] || (_cache[36] = $event => ((config.exclude_dirs) = $event)),
                                  label: "排除目录",
                                  placeholder: "例:\n/path/to/exclude1\n/path/to/exclude2",
                                  hint: "需要排除的目录，每行一个路径",
                                  "persistent-hint": ""
                                }, null, 8, ["modelValue"])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }, 8, ["modelValue"])
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_actions, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_btn, {
              color: "secondary",
              onClick: resetForm
            }, {
              default: _withCtx(() => [...(_cache[75] || (_cache[75] = [
                _createTextVNode("重置配置", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_v_spacer),
            _createVNode(_component_v_btn, {
              color: "primary",
              disabled: !isFormValid.value,
              onClick: saveConfig,
              loading: saving.value
            }, {
              default: _withCtx(() => [...(_cache[76] || (_cache[76] = [
                _createTextVNode("保存配置", -1)
              ]))]),
              _: 1
            }, 8, ["disabled", "loading"])
          ]),
          _: 1
        })
      ]),
      _: 1
    })
  ]))
}
}

};

export { _sfc_main as default };
