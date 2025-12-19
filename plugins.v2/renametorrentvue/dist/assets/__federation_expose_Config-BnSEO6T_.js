import { importShared } from './__federation_fn_import-JrT3xvdd.js';

const {toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,withModifiers:_withModifiers,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "plugin-config" };

const {ref,reactive,onMounted} = await importShared('vue');


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
};

// 合并默认配置和初始配置
const config = reactive({ ...defaultConfig, ...props.initialConfig});

// 初始化配置
onMounted(async () => {
  try {
    const data = await props.api.get(`plugin/${config.id}/get_config`);
    Object.assign(config, {...config, ...data});
  } catch (err) {
    console.error('获取配置失败:', err);
    error.value = err.message || '获取配置失败';
  }
});

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

return (_ctx, _cache) => {
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_card_item = _resolveComponent("v-card-item");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_select = _resolveComponent("v-select");
  const _component_VCronField = _resolveComponent("VCronField");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_textarea = _resolveComponent("v-textarea");
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
                  default: _withCtx(() => [...(_cache[16] || (_cache[16] = [
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
              "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((isFormValid).value = $event)),
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
                          default: _withCtx(() => [...(_cache[17] || (_cache[17] = [
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
                              md: "4"
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
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_switch, {
                                  modelValue: config.notify,
                                  "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.notify) = $event)),
                                  label: "启用通知",
                                  color: "primary",
                                  "persistent-hint": "",
                                  inset: ""
                                }, null, 8, ["modelValue"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_v_col, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_switch, {
                                  modelValue: config.add_tag_after_rename,
                                  "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.add_tag_after_rename) = $event)),
                                  label: "重命名成功后添加标签",
                                  color: "primary",
                                  "persistent-hint": "",
                                  inset: ""
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
                }),
                _createVNode(_component_v_card, {
                  variant: "outlined",
                  class: "mb-4"
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_item, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_card_title, { class: "text-subtitle-1 font-weight-bold" }, {
                          default: _withCtx(() => [...(_cache[18] || (_cache[18] = [
                            _createTextVNode("下载器设置", -1)
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
                                _createVNode(_component_v_select, {
                                  modelValue: config.downloader,
                                  "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.downloader) = $event)),
                                  items: config.all_downloaders,
                                  label: "下载器",
                                  placeholder: "请选择下载器",
                                  "item-title": "title",
                                  "item-value": "value",
                                  multiple: "",
                                  chips: "",
                                  "deletable-chips": ""
                                }, null, 8, ["modelValue", "items"])
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
                          default: _withCtx(() => [...(_cache[19] || (_cache[19] = [
                            _createTextVNode("执行方式", -1)
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
                                  modelValue: config.cron_enabled,
                                  "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.cron_enabled) = $event)),
                                  label: "启用定时任务",
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
                                  modelValue: config.event_enabled,
                                  "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.event_enabled) = $event)),
                                  label: "启用事件监听",
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
                                  modelValue: config.retry,
                                  "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.retry) = $event)),
                                  label: "尝试处理失败的种子",
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
                                  modelValue: config.onlyonce,
                                  "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.onlyonce) = $event)),
                                  label: "立即运行一次",
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
                                  modelValue: config.recovery,
                                  "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.recovery) = $event)),
                                  label: "恢复重命名",
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
                        (config.cron_enabled)
                          ? (_openBlock(), _createBlock(_component_v_row, { key: 0 }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_col, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VCronField, {
                                      modelValue: config.cron,
                                      "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.cron) = $event)),
                                      label: "执行周期",
                                      hint: "设置插件的执行周期，如：0 2 * * * (每天凌晨2点执行)",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
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
                          default: _withCtx(() => [...(_cache[20] || (_cache[20] = [
                            _createTextVNode("标签过滤", -1)
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
                                _createVNode(_component_v_text_field, {
                                  modelValue: config.exclude_tags,
                                  "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.exclude_tags) = $event)),
                                  label: "排除标签",
                                  placeholder: "已重命名",
                                  hint: "排除包含指定标签的种子，多个标签用逗号分隔",
                                  "persistent-hint": ""
                                }, null, 8, ["modelValue"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_v_col, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_text_field, {
                                  modelValue: config.include_tags,
                                  "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((config.include_tags) = $event)),
                                  label: "包含标签",
                                  placeholder: "",
                                  hint: "仅处理包含指定标签的种子，多个标签用逗号分隔",
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
                }),
                _createVNode(_component_v_card, {
                  variant: "outlined",
                  class: "mb-4"
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_item, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_card_title, { class: "text-subtitle-1 font-weight-bold" }, {
                          default: _withCtx(() => [...(_cache[21] || (_cache[21] = [
                            _createTextVNode("路径过滤", -1)
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
                                  "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((config.exclude_dirs) = $event)),
                                  label: "排除目录",
                                  placeholder: "",
                                  hint: "排除指定目录下的种子，每行一个目录",
                                  "persistent-hint": ""
                                }, null, 8, ["modelValue"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_v_col, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_textarea, {
                                  modelValue: config.hash_white_list,
                                  "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((config.hash_white_list) = $event)),
                                  label: "种子哈希白名单",
                                  placeholder: "",
                                  hint: "仅处理指定哈希的种子，每行一个哈希值",
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
                }),
                _createVNode(_component_v_card, {
                  variant: "outlined",
                  class: "mb-4"
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_item, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_card_title, { class: "text-subtitle-1 font-weight-bold" }, {
                          default: _withCtx(() => [...(_cache[22] || (_cache[22] = [
                            _createTextVNode("重命名格式", -1)
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
                                  modelValue: config.format_torrent_name,
                                  "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((config.format_torrent_name) = $event)),
                                  label: "格式化字符",
                                  placeholder: "{{ title }}{% if year %} ({{ year }}){% endif %}{% if season_episode %} - {{season_episode}}{% endif %}.{{original_name}}",
                                  hint: "种子重命名的格式模板",
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
              default: _withCtx(() => [...(_cache[23] || (_cache[23] = [
                _createTextVNode("重置", -1)
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
              default: _withCtx(() => [...(_cache[24] || (_cache[24] = [
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
