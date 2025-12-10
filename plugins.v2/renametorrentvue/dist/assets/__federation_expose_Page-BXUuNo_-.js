import { importShared } from './__federation_fn_import-JrT3xvdd.js';

const _export_sfc = (sfc, props) => {
  const target = sfc.__vccOpts || sfc;
  for (const [key, val] of props) {
    target[key] = val;
  }
  return target;
};

const {createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "history-container" };
const _hoisted_2 = { class: "d-flex flex-wrap align-center mb-4" };

const {ref,onMounted,computed} = await importShared('vue');


// 接收API对象

const _sfc_main = {
  __name: 'Page',
  props: {
  api: {
    type: Object,
    default: () => {},
  },
},
  setup(__props) {

const props = __props;

// 数据表格头部定义
const headers = [
  { title: '原始名称', key: 'original_name' },
  { title: '重命名后', key: 'after_name' },
  { title: '状态', key: 'success' },
  { title: '处理时间', key: 'date' },
  { title: '操作', key: 'actions', sortable: false }
];

// 状态变量
const loading = ref(false);
const historyRecords = ref([]);
const detailDialog = ref(false);
const currentRecord = ref({});

// 筛选变量
const filterStatus = ref('all');
const filterKeyword = ref('');

// 状态筛选选项
const statusOptions = [
  { title: '全部', value: 'all' },
  { title: '成功', value: 'success' },
  { title: '失败', value: 'failed' }
];

// 计算属性：过滤后的历史记录
const filteredHistoryRecords = computed(() => {
  let filtered = historyRecords.value;
  
  // 状态筛选
  if (filterStatus.value !== 'all') {
    const isSuccess = filterStatus.value === 'success';
    filtered = filtered.filter(record => record.success === isSuccess);
  }
  
  // 关键字筛选
  if (filterKeyword.value) {
    const keyword = filterKeyword.value.toLowerCase();
    filtered = filtered.filter(record => 
      (record.original_name && record.original_name.toLowerCase().includes(keyword)) ||
      (record.after_name && record.after_name.toLowerCase().includes(keyword))
    );
  }
  
  return filtered
});

// 刷新历史记录
async function refreshHistory() {
  try {
    loading.value = true;
    const response = await props.api.get('/plugin/renametorrentvue/rename_history');
    historyRecords.value = response.data || [];
  } catch (error) {
    console.error('获取历史记录失败:', error);
  } finally {
    loading.value = false;
  }
}

// 显示详情
function showDetail(record) {
  currentRecord.value = record;
  detailDialog.value = true;
}

// 格式化日期
function formatDate(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

// 组件挂载时刷新数据
onMounted(() => {
  refreshHistory();
});

return (_ctx, _cache) => {
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_card_item = _resolveComponent("v-card-item");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VSelect = _resolveComponent("VSelect");
  const _component_VTextField = _resolveComponent("VTextField");
  const _component_VSpacer = _resolveComponent("VSpacer");
  const _component_v_chip = _resolveComponent("v-chip");
  const _component_VDataTable = _resolveComponent("VDataTable");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");
  const _component_VCardTitle = _resolveComponent("VCardTitle");
  const _component_v_list_item_title = _resolveComponent("v-list-item-title");
  const _component_v_list_item_subtitle = _resolveComponent("v-list-item-subtitle");
  const _component_v_list_item = _resolveComponent("v-list-item");
  const _component_v_list = _resolveComponent("v-list");
  const _component_VCardText = _resolveComponent("VCardText");
  const _component_VCardActions = _resolveComponent("VCardActions");
  const _component_VCard = _resolveComponent("VCard");
  const _component_VDialog = _resolveComponent("VDialog");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_v_card, null, {
      default: _withCtx(() => [
        _createVNode(_component_v_card_item, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, null, {
              default: _withCtx(() => [...(_cache[4] || (_cache[4] = [
                _createTextVNode("重命名历史记录", -1)
              ]))]),
              _: 1
            })
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_text, null, {
          default: _withCtx(() => [
            _createElementVNode("div", _hoisted_2, [
              _createVNode(_component_VBtn, {
                color: "primary",
                onClick: refreshHistory,
                loading: loading.value,
                "prepend-icon": "mdi-refresh",
                class: "mr-2 mb-2"
              }, {
                default: _withCtx(() => [...(_cache[5] || (_cache[5] = [
                  _createTextVNode(" 刷新记录 ", -1)
                ]))]),
                _: 1
              }, 8, ["loading"]),
              _createVNode(_component_VSelect, {
                modelValue: filterStatus.value,
                "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((filterStatus).value = $event)),
                items: statusOptions,
                dense: "",
                "hide-details": "",
                class: "mr-2 mb-2",
                style: {"max-width":"120px"}
              }, null, 8, ["modelValue"]),
              _createVNode(_component_VTextField, {
                modelValue: filterKeyword.value,
                "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((filterKeyword).value = $event)),
                placeholder: "搜索名称",
                dense: "",
                "hide-details": "",
                clearable: "",
                class: "mr-2 mb-2",
                style: {"max-width":"200px"}
              }, null, 8, ["modelValue"]),
              _createVNode(_component_VSpacer)
            ]),
            _createVNode(_component_VDataTable, {
              headers: headers,
              items: filteredHistoryRecords.value,
              loading: loading.value,
              class: "elevation-1",
              "items-per-page": 10,
              "footer-props": {
            'items-per-page-options': [10, 20, 50, -1]
          }
            }, {
              "item.success": _withCtx(({ item }) => [
                _createVNode(_component_v_chip, {
                  color: item.success ? 'success' : 'error',
                  small: ""
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(item.success ? '成功' : '失败'), 1)
                  ]),
                  _: 2
                }, 1032, ["color"])
              ]),
              "item.date": _withCtx(({ item }) => [
                _createTextVNode(_toDisplayString(formatDate(item.date)), 1)
              ]),
              "item.actions": _withCtx(({ item }) => [
                _createVNode(_component_VBtn, {
                  color: "primary",
                  variant: "outlined",
                  size: "small",
                  onClick: $event => (showDetail(item)),
                  class: "mr-2"
                }, {
                  default: _withCtx(() => [...(_cache[6] || (_cache[6] = [
                    _createTextVNode(" 详情 ", -1)
                  ]))]),
                  _: 1
                }, 8, ["onClick"])
              ]),
              _: 1
            }, 8, ["items", "loading"])
          ]),
          _: 1
        })
      ]),
      _: 1
    }),
    _createVNode(_component_VDialog, {
      modelValue: detailDialog.value,
      "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((detailDialog).value = $event)),
      "max-width": "600px"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_VCard, null, {
          default: _withCtx(() => [
            _createVNode(_component_VCardTitle, null, {
              default: _withCtx(() => [...(_cache[7] || (_cache[7] = [
                _createElementVNode("span", { class: "text-h5" }, "重命名详情", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VCardText, null, {
              default: _withCtx(() => [
                _createVNode(_component_v_list, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_list_item, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_list_item_title, { class: "font-weight-bold" }, {
                          default: _withCtx(() => [...(_cache[8] || (_cache[8] = [
                            _createTextVNode("种子哈希:", -1)
                          ]))]),
                          _: 1
                        }),
                        _createVNode(_component_v_list_item_subtitle, null, {
                          default: _withCtx(() => [
                            _createTextVNode(_toDisplayString(currentRecord.value.hash), 1)
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_list_item, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_list_item_title, { class: "font-weight-bold" }, {
                          default: _withCtx(() => [...(_cache[9] || (_cache[9] = [
                            _createTextVNode("原始名称:", -1)
                          ]))]),
                          _: 1
                        }),
                        _createVNode(_component_v_list_item_subtitle, null, {
                          default: _withCtx(() => [
                            _createTextVNode(_toDisplayString(currentRecord.value.original_name), 1)
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_list_item, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_list_item_title, { class: "font-weight-bold" }, {
                          default: _withCtx(() => [...(_cache[10] || (_cache[10] = [
                            _createTextVNode("重命名后:", -1)
                          ]))]),
                          _: 1
                        }),
                        _createVNode(_component_v_list_item_subtitle, null, {
                          default: _withCtx(() => [
                            _createTextVNode(_toDisplayString(currentRecord.value.after_name), 1)
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_list_item, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_list_item_title, { class: "font-weight-bold" }, {
                          default: _withCtx(() => [...(_cache[11] || (_cache[11] = [
                            _createTextVNode("状态:", -1)
                          ]))]),
                          _: 1
                        }),
                        _createVNode(_component_v_list_item_subtitle, null, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_chip, {
                              color: currentRecord.value.success ? 'success' : 'error',
                              small: ""
                            }, {
                              default: _withCtx(() => [
                                _createTextVNode(_toDisplayString(currentRecord.value.success ? '成功' : '失败'), 1)
                              ]),
                              _: 1
                            }, 8, ["color"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_list_item, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_list_item_title, { class: "font-weight-bold" }, {
                          default: _withCtx(() => [...(_cache[12] || (_cache[12] = [
                            _createTextVNode("处理时间:", -1)
                          ]))]),
                          _: 1
                        }),
                        _createVNode(_component_v_list_item_subtitle, null, {
                          default: _withCtx(() => [
                            _createTextVNode(_toDisplayString(formatDate(currentRecord.value.date)), 1)
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
            _createVNode(_component_VCardActions, null, {
              default: _withCtx(() => [
                _createVNode(_component_VSpacer),
                _createVNode(_component_VBtn, {
                  color: "blue darken-1",
                  variant: "text",
                  onClick: _cache[2] || (_cache[2] = $event => (detailDialog.value = false))
                }, {
                  default: _withCtx(() => [...(_cache[13] || (_cache[13] = [
                    _createTextVNode(" 关闭 ", -1)
                  ]))]),
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
  ]))
}
}

};
const PageComponent = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-5d23163b"]]);

export { _export_sfc as _, PageComponent as default };
