import { importShared } from './__federation_fn_import-JrT3xvdd.js';

const {toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,createElementVNode:_createElementVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,withModifiers:_withModifiers} = await importShared('vue');


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
  emits: ['save', 'close', 'switch'],
  setup(__props, { emit: __emit }) {

const props = __props;

// 表单状态
const form = ref(null);
const isFormValid = ref(true);
const error = ref(null);
const saving = ref(false);
ref(false);

const scheduleTypes = ['禁用','计划任务','固定间隔'];


// 配置数据，使用默认值和初始配置合并
const defaultConfig = {
  id: 'DownloadSiteTagModNew',
  name: '下载任务分类与标签联邦魔改版',
};

// 合并默认配置和初始配置
const config = reactive({ ...defaultConfig, ...props.initialConfig});

async function loadInitialData() {

  
}
// 初始化配置
onMounted(async () => {
  loadInitialData();
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
    // 模拟API调用等待
    await new Promise(resolve => setTimeout(resolve, 1000));

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
  Object.keys(defaultConfig).forEach(key => {
    config[key] = defaultConfig[key];
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
  const _component_v_checkbox = _resolveComponent("v-checkbox");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_divider = _resolveComponent("v-divider");
  const _component_v_select = _resolveComponent("v-select");
  const _component_v_text_field = _resolveComponent("v-text-field");
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
                _createVNode(_component_v_icon, { left: "" }, {
                  default: _withCtx(() => _cache[12] || (_cache[12] = [
                    _createTextVNode("mdi-close")
                  ])),
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
              "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((isFormValid).value = $event)),
              onSubmit: _withModifiers(saveConfig, ["prevent"])
            }, {
              default: _withCtx(() => [
                _cache[13] || (_cache[13] = _createElementVNode("div", { class: "text-subtitle-1 font-weight-bold mt-4 mb-2" }, "基本设置", -1)),
                _createVNode(_component_v_row, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_col, {
                      cols: "6",
                      md: "3"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_switch, {
                          modelValue: config.enable,
                          "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((config.enable) = $event)),
                          label: "启用插件",
                          color: "primary",
                          "persistent-hint": "",
                          inset: ""
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, {
                      cols: "6",
                      md: "3"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_checkbox, {
                          modelValue: config.enable_tag,
                          "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.enable_tag) = $event)),
                          label: "自动站点标签",
                          color: "primary"
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, {
                      cols: "6",
                      md: "3"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_checkbox, {
                          modelValue: config.enable_media_tag,
                          "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.enable_media_tag) = $event)),
                          label: "自动剧名标签",
                          color: "primary"
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, {
                      cols: "6",
                      md: "3"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_checkbox, {
                          modelValue: config.enable_category,
                          "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.enable_category) = $event)),
                          label: "自动设置分类",
                          color: "primary"
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, {
                      cols: "6",
                      md: "3"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_checkbox, {
                          modelValue: config.onlyonce,
                          "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.onlyonce) = $event)),
                          label: "补全下载历史的标签与分类(一次性任务)",
                          color: "primary",
                          inset: ""
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_switch, {
                          modelValue: config.rename_type,
                          "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.rename_type) = $event)),
                          label: "自定义",
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
                _createVNode(_component_v_divider),
                _createVNode(_component_v_row, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_col, { cols: "12" }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_select, {
                          modelValue: config.downloader,
                          "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.downloader) = $event)),
                          items: config.all_downloaders,
                          label: "下载器",
                          placeholder: "请选择下载器",
                          "item-text": "title",
                          "item-value": "value",
                          "return-object": ""
                        }, null, 8, ["modelValue", "items"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, {
                      cols: "6",
                      md: "3"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_select, {
                          modelValue: config.interval,
                          "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.interval) = $event)),
                          items: scheduleTypes,
                          label: "定时任务类型"
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    }),
                    (config.scheduleType === 'cron')
                      ? (_openBlock(), _createBlock(_component_v_col, {
                          key: 0,
                          cols: "6",
                          md: "3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_text_field, {
                              modelValue: config.cronExpression,
                              "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.cronExpression) = $event)),
                              label: "计划任务设置",
                              placeholder: "例如：5 4 * * *",
                              hint: "Cron表达式格式",
                              "persistent-hint": ""
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        }))
                      : _createCommentVNode("", true),
                    (config.scheduleType === 'interval')
                      ? (_openBlock(), _createBlock(_component_v_col, {
                          key: 1,
                          cols: "6",
                          md: "3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_text_field, {
                              modelValue: config.interval,
                              "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.interval) = $event)),
                              modelModifiers: { number: true },
                              label: "固定间隔",
                              type: "number",
                              placeholder: "输入间隔时间"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        }))
                      : _createCommentVNode("", true),
                    (config.scheduleType === 'interval')
                      ? (_openBlock(), _createBlock(_component_v_col, {
                          key: 2,
                          cols: "6",
                          md: "3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_select, {
                              modelValue: config.intervalUnit,
                              "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.intervalUnit) = $event)),
                              items: _ctx.intervalUnits,
                              label: "单位",
                              "item-text": "name",
                              "item-value": "id",
                              dense: ""
                            }, null, 8, ["modelValue", "items"])
                          ]),
                          _: 1
                        }))
                      : _createCommentVNode("", true)
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_divider, { class: "my-4" }),
                _createVNode(_component_v_row, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_col, { cols: "12" }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_row, null, {
                          default: _withCtx(() => [
                            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(config.all_cat, (category, index) => {
                              return (_openBlock(), _createBlock(_component_v_col, {
                                cols: "12",
                                md: "3",
                                key: index
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_v_text_field, {
                                    modelValue: config.all_cat[index],
                                    "onUpdate:modelValue": $event => ((config.all_cat[index]) = $event),
                                    label: category,
                                    placeholder: category
                                  }, null, 8, ["modelValue", "onUpdate:modelValue", "label", "placeholder"])
                                ]),
                                _: 2
                              }, 1024))
                            }), 128))
                          ]),
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
              default: _withCtx(() => _cache[14] || (_cache[14] = [
                _createTextVNode("重置")
              ])),
              _: 1
            }),
            _createVNode(_component_v_spacer),
            _createVNode(_component_v_btn, {
              color: "primary",
              disabled: !isFormValid.value,
              onClick: saveConfig,
              loading: saving.value
            }, {
              default: _withCtx(() => _cache[15] || (_cache[15] = [
                _createTextVNode("保存配置")
              ])),
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
