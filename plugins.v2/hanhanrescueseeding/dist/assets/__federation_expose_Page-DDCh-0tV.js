import { importShared } from './__federation_fn_import-JrT3xvdd.js';

const {toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,createElementVNode:_createElementVNode,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "plugin-page" };
const _hoisted_2 = { key: 2 };
const _hoisted_3 = { class: "mt-4" };

const {ref,onMounted} = await importShared('vue');


// 接收初始配置

const _sfc_main = {
  __name: 'Page',
  props: {
  model: {
    type: Object,
    default: () => {},
  },
  api: {
    type: Object,
    default: () => {},
  },
},
  emits: ['action', 'switch', 'close'],
  setup(__props, { emit: __emit }) {

const props = __props;

// 组件状态
const title = ref('憨憨保种区');
const loading = ref(true);
const error = ref(null);
const downloadRecords = ref([]);
const downloadHeaders = ref([
  { title: '英文标题', key: 'title' },
  { title: '中文标题', key: 'zh_title' },
  { title: '种子大小', key: 'size' },
  { title: '做种人数', key: 'seeders' },
  { title: '下载时间', key: 'download_time' },
]);

// 自定义事件，用于通知主应用刷新数据
const emit = __emit;

// 格式化时间
function formatTime(timeStr) {
  // 检查是否为有效日期字符串
  if (!timeStr) return 'N/A'
  
  // 尝试解析日期
  const date = new Date(timeStr);
  if (isNaN(date.getTime())) {
    // 如果是无效日期，直接返回原始字符串
    return timeStr
  }
  
  // 返回本地化的时间字符串
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取和刷新数据
async function refreshData() {
  loading.value = true;
  error.value = null;

  try {
    // 获取下载记录
    const records = await props.api.get(`plugin/HanHanRescueSeeding/download_records`);
    downloadRecords.value = records || [];
  } catch (err) {
    console.error('获取下载记录失败:', err);
    error.value = err.message || '获取下载记录失败';
    downloadRecords.value = [];
  } finally {
    loading.value = false;
    // 通知主应用组件已更新
    emit('action');
  }
}

// 通知主应用切换到配置页面
function notifySwitch() {
  emit('switch');
}

// 通知主应用关闭组件
function notifyClose() {
  emit('close');
}

// 组件挂载时加载数据
onMounted(() => {
  refreshData();
});

return (_ctx, _cache) => {
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_card_item = _resolveComponent("v-card-item");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_skeleton_loader = _resolveComponent("v-skeleton-loader");
  const _component_v_data_table = _resolveComponent("v-data-table");
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
                  default: _withCtx(() => _cache[0] || (_cache[0] = [
                    _createTextVNode("mdi-close", -1)
                  ])),
                  _: 1,
                  __: [0]
                })
              ]),
              _: 1
            })
          ]),
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, null, {
              default: _withCtx(() => [
                _createTextVNode(_toDisplayString(title.value), 1)
              ]),
              _: 1
            })
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_text, null, {
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
            (loading.value)
              ? (_openBlock(), _createBlock(_component_v_skeleton_loader, {
                  key: 1,
                  type: "table"
                }))
              : (_openBlock(), _createElementBlock("div", _hoisted_2, [
                  _createElementVNode("div", _hoisted_3, [
                    _cache[2] || (_cache[2] = _createElementVNode("div", { class: "text-h6 mb-2" }, "下载记录", -1)),
                    (downloadRecords.value && downloadRecords.value.length > 0)
                      ? (_openBlock(), _createBlock(_component_v_data_table, {
                          key: 0,
                          headers: downloadHeaders.value,
                          items: downloadRecords.value,
                          "items-per-page": 10,
                          "footer-props": {
                'items-per-page-options': [5, 10, 20, -1]
              },
                          class: "elevation-1"
                        }, {
                          "item.download_time": _withCtx(({ item }) => [
                            _createTextVNode(_toDisplayString(formatTime(item.download_time)), 1)
                          ]),
                          _: 1
                        }, 8, ["headers", "items"]))
                      : (_openBlock(), _createBlock(_component_v_alert, {
                          key: 1,
                          type: "info",
                          class: "mt-4"
                        }, {
                          default: _withCtx(() => _cache[1] || (_cache[1] = [
                            _createTextVNode(" 暂无下载记录 ", -1)
                          ])),
                          _: 1,
                          __: [1]
                        }))
                  ])
                ]))
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_actions, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_btn, {
              color: "primary",
              onClick: refreshData,
              loading: loading.value
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, { start: "" }, {
                  default: _withCtx(() => _cache[3] || (_cache[3] = [
                    _createTextVNode("mdi-refresh", -1)
                  ])),
                  _: 1,
                  __: [3]
                }),
                _cache[4] || (_cache[4] = _createTextVNode(" 刷新数据 ", -1))
              ]),
              _: 1,
              __: [4]
            }, 8, ["loading"]),
            _createVNode(_component_v_spacer),
            _createVNode(_component_v_btn, {
              color: "primary",
              onClick: notifySwitch
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, { start: "" }, {
                  default: _withCtx(() => _cache[5] || (_cache[5] = [
                    _createTextVNode("mdi-cog", -1)
                  ])),
                  _: 1,
                  __: [5]
                }),
                _cache[6] || (_cache[6] = _createTextVNode(" 配置 ", -1))
              ]),
              _: 1,
              __: [6]
            })
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
