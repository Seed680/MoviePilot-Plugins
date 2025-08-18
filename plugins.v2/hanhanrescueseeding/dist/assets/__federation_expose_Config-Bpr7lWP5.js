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
  id: 'HanHanRescueSeeding',
  name: '憨憨保种区',
  enable: false,
  cron: '',
  downloader: '',
  seeding_count: 10,
  all_downloaders: [],
  save_path: ''
};

// 合并默认配置和初始配置
const config = reactive({ ...defaultConfig, ...props.initialConfig});

// 初始化配置
onMounted(async () => {
  try {
    const data = await props.api.get(`plugin/${config.id}/config`);
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
  const _component_VCronField = _resolveComponent("VCronField");
  const _component_v_text_field = _resolveComponent("v-text-field");
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
                  default: _withCtx(() => _cache[6] || (_cache[6] = [
                    _createTextVNode("mdi-close", -1)
                  ])),
                  _: 1,
                  __: [6]
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
              "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((isFormValid).value = $event)),
              onSubmit: _withModifiers(saveConfig, ["prevent"])
            }, {
              default: _withCtx(() => [
                _cache[7] || (_cache[7] = _createElementVNode("div", { class: "text-subtitle-1 font-weight-bold mt-4 mb-2" }, "基本设置", -1)),
                _createVNode(_component_v_row, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "6"
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
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_row, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_col, { cols: "12" }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_select, {
                          modelValue: config.downloader,
                          "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.downloader) = $event)),
                          items: config.all_downloaders,
                          label: "下载器",
                          placeholder: "请选择下载器",
                          "item-title": "title",
                          "item-value": "value",
                          chips: ""
                        }, null, 8, ["modelValue", "items"])
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
                        _createVNode(_component_VCronField, {
                          modelValue: config.cron,
                          "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.cron) = $event)),
                          label: "执行周期",
                          hint: "设置插件的执行周期，如：0 2 * * * (每天凌晨2点执行)",
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
                          modelValue: config.seeding_count,
                          "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.seeding_count) = $event)),
                          modelModifiers: { number: true },
                          label: "做种人数",
                          type: "number",
                          placeholder: "请输入做种人数",
                          hint: "当种子的做种人数超过该值时进行相应处理",
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
                          modelValue: config.save_path,
                          "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.save_path) = $event)),
                          label: "保存路径",
                          placeholder: "请输入保存路径",
                          hint: "设置种子文件的保存路径",
                          "persistent-hint": ""
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_divider, { class: "my-4" })
              ]),
              _: 1,
              __: [7]
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
              default: _withCtx(() => _cache[8] || (_cache[8] = [
                _createTextVNode("重置", -1)
              ])),
              _: 1,
              __: [8]
            }),
            _createVNode(_component_v_spacer),
            _createVNode(_component_v_btn, {
              color: "primary",
              disabled: !isFormValid.value,
              onClick: saveConfig,
              loading: saving.value
            }, {
              default: _withCtx(() => _cache[9] || (_cache[9] = [
                _createTextVNode("保存配置", -1)
              ])),
              _: 1,
              __: [9]
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
