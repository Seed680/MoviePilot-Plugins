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
const siteOptions = ref([]);

// 配置数据，使用默认值和初始配置合并
const defaultConfig = {
  id: 'AutoSignIn',
  name: '站点自动签到',
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
};

// 合并默认配置和初始配置
const config = reactive({ ...defaultConfig, ...props.initialConfig });

// 初始化配置
onMounted(async () => {
  try {
    // 获取当前配置
    const data = await props.api.get(`plugin/autosignin/config`);
    if (data) {
      Object.assign(config, { ...config, ...data });
    }
    
    // 获取站点列表 - 这里需要从MoviePilot API获取
    // 暂时使用空数组，实际使用时由MoviePilot注入
    siteOptions.value = config.all_sites || [];
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
  const _component_VCronField = _resolveComponent("VCronField");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_divider = _resolveComponent("v-divider");
  const _component_v_select = _resolveComponent("v-select");
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
                  default: _withCtx(() => [...(_cache[11] || (_cache[11] = [
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
              "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((isFormValid).value = $event)),
              onSubmit: _withModifiers(saveConfig, ["prevent"])
            }, {
              default: _withCtx(() => [
                _cache[14] || (_cache[14] = _createElementVNode("div", { class: "text-subtitle-1 font-weight-bold mt-4 mb-2" }, "基本设置", -1)),
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
                          label: "发送通知",
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
                          "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.onlyonce) = $event)),
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
                          modelValue: config.clean,
                          "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.clean) = $event)),
                          label: "清理本日缓存",
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
                        _createVNode(_component_VCronField, {
                          modelValue: config.cron,
                          "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.cron) = $event)),
                          label: "执行周期",
                          placeholder: "5位cron表达式，留空自动",
                          hint: "支持：1、5位cron表达式；2、配置间隔（小时），如2.3/9-23；3、周期不填默认9-23点随机执行2次",
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
                          modelValue: config.queue_cnt,
                          "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.queue_cnt) = $event)),
                          modelModifiers: { number: true },
                          label: "队列数量",
                          type: "number",
                          placeholder: "请输入队列数量",
                          hint: "并发执行的站点数量",
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
                          modelValue: config.retry_keyword,
                          "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.retry_keyword) = $event)),
                          label: "重试关键词",
                          placeholder: "支持正则表达式，命中才重签",
                          hint: "签到失败时匹配此关键词的站点会被重试",
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
                          modelValue: config.auto_cf,
                          "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.auto_cf) = $event)),
                          modelModifiers: { number: true },
                          label: "自动优选",
                          type: "number",
                          placeholder: "0-关闭",
                          hint: "命中重试关键词次数大于该数量时自动执行Cloudflare IP优选",
                          "persistent-hint": ""
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_divider, { class: "my-4" }),
                _cache[15] || (_cache[15] = _createElementVNode("div", { class: "text-subtitle-1 font-weight-bold mt-4 mb-2" }, "站点选择", -1)),
                _createVNode(_component_v_row, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_col, { cols: "12" }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_select, {
                          modelValue: config.sign_sites,
                          "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.sign_sites) = $event)),
                          items: siteOptions.value,
                          label: "签到站点",
                          placeholder: "请选择需要签到的站点",
                          "item-title": "title",
                          "item-value": "value",
                          chips: "",
                          multiple: "",
                          clearable: ""
                        }, null, 8, ["modelValue", "items"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, { cols: "12" }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_select, {
                          modelValue: config.login_sites,
                          "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.login_sites) = $event)),
                          items: siteOptions.value,
                          label: "登录站点",
                          placeholder: "请选择需要模拟登录的站点",
                          "item-title": "title",
                          "item-value": "value",
                          chips: "",
                          multiple: "",
                          clearable: ""
                        }, null, 8, ["modelValue", "items"])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_divider, { class: "my-4" }),
                _createVNode(_component_v_alert, {
                  type: "info",
                  variant: "tonal",
                  class: "mt-4"
                }, {
                  default: _withCtx(() => [...(_cache[12] || (_cache[12] = [
                    _createElementVNode("div", { class: "text-body-2" }, [
                      _createElementVNode("strong", null, "执行周期说明："),
                      _createElementVNode("br"),
                      _createTextVNode(" 1、5位cron表达式；"),
                      _createElementVNode("br"),
                      _createTextVNode(" 2、配置间隔（小时），如2.3/9-23（9-23点之间每隔2.3小时执行一次）；"),
                      _createElementVNode("br"),
                      _createTextVNode(" 3、周期不填默认9-23点随机执行2次。"),
                      _createElementVNode("br"),
                      _createTextVNode(" 每天首次全量执行，其余执行命中重试关键词的站点。 ")
                    ], -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_v_alert, {
                  type: "warning",
                  variant: "tonal",
                  class: "mt-2"
                }, {
                  default: _withCtx(() => [...(_cache[13] || (_cache[13] = [
                    _createElementVNode("div", { class: "text-body-2" }, [
                      _createElementVNode("strong", null, "注意："),
                      _createTextVNode("不是所有的站点都会把程序自动登录/签到定义为用户活跃（比如馒头），提示签到/登录成功仍然存在掉号风险！请结合站点公告说明自行把握。 ")
                    ], -1)
                  ]))]),
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
              default: _withCtx(() => [...(_cache[16] || (_cache[16] = [
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
              default: _withCtx(() => [...(_cache[17] || (_cache[17] = [
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
