import { importShared } from './__federation_fn_import-JrT3xvdd.js';

const {toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,createElementVNode:_createElementVNode,withModifiers:_withModifiers,createElementBlock:_createElementBlock} = await importShared('vue');


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
  name: '重命名种子文件Vue版',
  enabled: false,
  notify: false,
  downloader: '',
  all_downloaders: [],
  format_torrent_name: '{{ title }}{% if year %} ({{ year }}){% endif %}{% if season_episode %} - {{season_episode}}{% endif %}',
  exclude_tags: '',
  include_tags: '',
  exclude_dirs: '',
  hash_white_list: '',
  add_tag_after_rename: false,
  event_enabled: false,
  cron_enabled: false,
  onlyonce: false,
  recovery: false,
  retry: false,
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
  const _component_v_select = _resolveComponent("v-select");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_textarea = _resolveComponent("v-textarea");
  const _component_v_divider = _resolveComponent("v-divider");
  const _component_v_form = _resolveComponent("v-form");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_card_actions = _resolveComponent("v-card-actions");
  const _component_v_card = _resolveComponent("v-card");

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
                _cache[18] || (_cache[18] = _createElementVNode("div", { class: "text-subtitle-1 font-weight-bold mt-4 mb-2" }, "基本设置", -1)),
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
                      md: "6"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_switch, {
                          modelValue: config.add_tag_after_rename,
                          "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.add_tag_after_rename) = $event)),
                          label: "重命名后添加标签",
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
                          "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.event_enabled) = $event)),
                          label: "启用事件监听",
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
                          modelValue: config.onlyonce,
                          "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.onlyonce) = $event)),
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
                          "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.recovery) = $event)),
                          label: "恢复重命名",
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
                          "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.retry) = $event)),
                          label: "尝试失败",
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
                _createVNode(_component_v_row, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "6"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_select, {
                          modelValue: config.downloader,
                          "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.downloader) = $event)),
                          items: config.all_downloaders,
                          label: "下载器",
                          placeholder: "请选择下载器",
                          "item-title": "title",
                          "item-value": "value",
                          chips: ""
                        }, null, 8, ["modelValue", "items"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "6"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_text_field, {
                          modelValue: config.cron,
                          "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.cron) = $event)),
                          label: "执行周期",
                          placeholder: "0 8 * * *"
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
                          modelValue: config.format_torrent_name,
                          "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.format_torrent_name) = $event)),
                          label: "种子标题重命名格式",
                          rows: "2",
                          "auto-grow": "",
                          hint: "使用Jinja2语法, 所用变量与主程序相同",
                          "persistent-hint": ""
                        }, null, 8, ["modelValue"])
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
                        _createVNode(_component_v_text_field, {
                          modelValue: config.exclude_tags,
                          "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((config.exclude_tags) = $event)),
                          label: "排除标签",
                          placeholder: "注意: 空白字符会排除所有未设置标签的种子",
                          hint: "多个标签用, 分割，空格表示没有标签",
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
                          "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((config.include_tags) = $event)),
                          label: "包含标签",
                          placeholder: "注意: 空白字符会包含所有未设置标签的种子",
                          hint: "多个标签用, 分割，空格表示没有标签，排除标签优先级更高",
                          "persistent-hint": ""
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
                          modelValue: config.hash_white_list,
                          "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((config.hash_white_list) = $event)),
                          label: "指定种子hash",
                          rows: "2",
                          "auto-grow": "",
                          hint: "指定种子hash, 一行一个",
                          "persistent-hint": ""
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
                          modelValue: config.exclude_dirs,
                          "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((config.exclude_dirs) = $event)),
                          label: "排除目录",
                          rows: "3",
                          "auto-grow": "",
                          placeholder: "例如:\\n /mnt/download \\n E:\\download",
                          hint: "排除目录, 一行一个, 路径深度不能超过保存路径",
                          "persistent-hint": ""
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
                        _createVNode(_component_v_alert, {
                          type: "info",
                          variant: "tonal"
                        }, {
                          default: _withCtx(() => [...(_cache[17] || (_cache[17] = [
                            _createTextVNode(" 种子重命名: 重命名种子在下载器显示的名称,qBittorrent 不会影响保存路径和种子内容布局; Transmission 不支持 ", -1)
                          ]))]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_divider, { class: "my-4" })
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
              default: _withCtx(() => [...(_cache[19] || (_cache[19] = [
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
              default: _withCtx(() => [...(_cache[20] || (_cache[20] = [
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
