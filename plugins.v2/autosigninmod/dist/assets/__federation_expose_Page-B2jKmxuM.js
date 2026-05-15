import { importShared } from './__federation_fn_import-JrT3xvdd.js';

const _export_sfc = (sfc, props) => {
  const target = sfc.__vccOpts || sfc;
  for (const [key, val] of props) {
    target[key] = val;
  }
  return target;
};

const {toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,createElementVNode:_createElementVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass} = await importShared('vue');


const _hoisted_1 = { class: "plugin-page" };
const _hoisted_2 = { key: 2 };
const _hoisted_3 = { class: "d-flex align-center" };
const _hoisted_4 = { class: "text-h5 font-weight-bold" };
const _hoisted_5 = { class: "d-flex align-center" };
const _hoisted_6 = { class: "text-h5 font-weight-bold" };
const _hoisted_7 = { class: "mt-4" };
const _hoisted_8 = { class: "text-h6 mb-2 d-flex align-center" };
const _hoisted_9 = { class: "d-flex align-center w-100" };
const _hoisted_10 = { class: "site-icon" };
const _hoisted_11 = { class: "font-weight-medium" };
const _hoisted_12 = { class: "d-flex align-center w-100" };
const _hoisted_13 = { class: "mt-6" };
const _hoisted_14 = { class: "text-h6 mb-2 d-flex align-center" };
const _hoisted_15 = { class: "d-flex align-center w-100" };
const _hoisted_16 = { class: "site-icon" };
const _hoisted_17 = { class: "font-weight-medium" };
const _hoisted_18 = { class: "d-flex align-center w-100" };

const {ref,onMounted,computed} = await importShared('vue');


// 接收初始配置

const _sfc_main = {
  __name: 'Page',
  props: {
  api: {
    type: Object,
    default: () => {},
  },
},
  emits: ['action', 'switch', 'close'],
  setup(__props, { emit: __emit }) {

const props = __props;

// 组件状态
const title = ref('站点自动签到');
const loading = ref(true);
const error = ref(null);
const signinData = ref([]);
const loginData = ref([]);

// 自定义事件
const emit = __emit;

// 计算站点数量
const signinSiteCount = computed(() => {
  const sites = new Set(signinData.value.map(item => item.site));
  return sites.size
});

const loginSiteCount = computed(() => {
  const sites = new Set(loginData.value.map(item => item.site));
  return sites.size
});

// 生成签到面板数据
const signinPanels = computed(() => {
  return generatePanels(signinData.value)
});

// 生成登录面板数据
const loginPanels = computed(() => {
  return generatePanels(loginData.value)
});

// 生成面板数据的通用函数
function generatePanels(data) {
  // 按站点分组
  const siteMap = {};
  data.forEach(record => {
    if (!siteMap[record.site]) {
      siteMap[record.site] = [];
    }
    siteMap[record.site].push(record);
  });

  // 转换为面板数组
  return Object.entries(siteMap).map(([siteName, records]) => {
    // 按日期排序，最新的在前面
    records.sort((a, b) => {
      return new Date(b.day_obj || 0) - new Date(a.day_obj || 0)
    });

    // 获取最新状态
    const latestStatus = records[0]?.status || '未知状态';
    
    // 确定状态颜色和图标
    const { statusColor, statusIcon } = getStatusStyle(latestStatus);
    
    // 生成站点首字母
    const siteInitial = siteName ? siteName[0].toUpperCase() : '?';

    // 为每条记录添加样式
    const styledRecords = records.map(record => {
      const { color, icon } = getRecordStyle(record.status);
      return { ...record, color, icon }
    });

    return {
      siteName,
      siteInitial,
      latestStatus,
      statusColor,
      statusIcon,
      records: styledRecords
    }
  })
}

// 获取状态样式
function getStatusStyle(status) {
  let statusColor = 'teal-lighten-3';
  let statusIcon = 'mdi-emoticon-happy-outline';

  if (status.includes('失败') || status.includes('错误')) {
    statusColor = 'deep-orange-lighten-3';
    statusIcon = 'mdi-emoticon-sad-outline';
  } else if (status.includes('Cookie已失效')) {
    statusColor = 'pink-lighten-3';
    statusIcon = 'mdi-cookie-off';
  } else if (status.includes('重试')) {
    statusColor = 'amber-lighten-3';
    statusIcon = 'mdi-emoticon-confused-outline';
  } else if (status.includes('已签到')) {
    statusColor = 'light-blue-lighten-3';
    statusIcon = 'mdi-emoticon-cool-outline';
  } else if (status.includes('成功')) {
    statusColor = 'teal-lighten-3';
    statusIcon = 'mdi-emoticon-happy-outline';
  }

  return { statusColor, statusIcon }
}

// 获取记录样式
function getRecordStyle(status) {
  let color = 'success';
  let icon = 'mdi-check-circle';

  if (status.includes('失败') || status.includes('错误')) {
    color = 'error';
    icon = 'mdi-alert-circle';
  } else if (status.includes('Cookie已失效')) {
    color = 'error';
    icon = 'mdi-cookie-off';
  } else if (status.includes('重试')) {
    color = 'warning';
    icon = 'mdi-refresh';
  } else if (status.includes('已签到')) {
    color = 'info';
    icon = 'mdi-check';
  } else if (status.includes('登录成功')) {
    color = 'success';
    icon = 'mdi-login-variant';
  }

  return { color, icon }
}

// 获取和刷新数据
async function refreshData() {
  loading.value = true;
  error.value = null;

  try {
    const response = await props.api.get(`plugin/AutoSignIn/history`);
    
    if (response && response.signin) {
      signinData.value = response.signin;
    }
    if (response && response.login) {
      loginData.value = response.login;
    }
  } catch (err) {
    console.error('获取历史记录失败:', err);
    error.value = '获取历史记录失败: ' + err.message;
    signinData.value = [];
    loginData.value = [];
  } finally {
    loading.value = false;
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
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_chip = _resolveComponent("v-chip");
  const _component_v_expansion_panel_title = _resolveComponent("v-expansion-panel-title");
  const _component_v_list_item = _resolveComponent("v-list-item");
  const _component_v_list = _resolveComponent("v-list");
  const _component_v_expansion_panel_text = _resolveComponent("v-expansion-panel-text");
  const _component_v_expansion_panel = _resolveComponent("v-expansion-panel");
  const _component_v_expansion_panels = _resolveComponent("v-expansion-panels");
  const _component_v_card_text = _resolveComponent("v-card-text");
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
                  default: _withCtx(() => [...(_cache[0] || (_cache[0] = [
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
                  _createVNode(_component_v_row, { class: "mb-4" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_col, {
                        cols: "12",
                        md: "6"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_card, {
                            variant: "outlined",
                            class: "pa-4"
                          }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_3, [
                                _createVNode(_component_v_icon, {
                                  color: "teal-lighten-3",
                                  size: "large",
                                  class: "mr-3"
                                }, {
                                  default: _withCtx(() => [...(_cache[1] || (_cache[1] = [
                                    _createTextVNode("mdi-duck", -1)
                                  ]))]),
                                  _: 1
                                }),
                                _createElementVNode("div", null, [
                                  _cache[2] || (_cache[2] = _createElementVNode("div", { class: "text-caption text-grey" }, "签到站点数", -1)),
                                  _createElementVNode("div", _hoisted_4, _toDisplayString(signinSiteCount.value), 1)
                                ])
                              ])
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
                          _createVNode(_component_v_card, {
                            variant: "outlined",
                            class: "pa-4"
                          }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_5, [
                                _createVNode(_component_v_icon, {
                                  color: "light-blue-accent-3",
                                  size: "large",
                                  class: "mr-3"
                                }, {
                                  default: _withCtx(() => [...(_cache[3] || (_cache[3] = [
                                    _createTextVNode("mdi-dog", -1)
                                  ]))]),
                                  _: 1
                                }),
                                _createElementVNode("div", null, [
                                  _cache[4] || (_cache[4] = _createElementVNode("div", { class: "text-caption text-grey" }, "登录站点数", -1)),
                                  _createElementVNode("div", _hoisted_6, _toDisplayString(loginSiteCount.value), 1)
                                ])
                              ])
                            ]),
                            _: 1
                          })
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  }),
                  _createElementVNode("div", _hoisted_7, [
                    _createElementVNode("div", _hoisted_8, [
                      _createVNode(_component_v_icon, {
                        color: "teal-lighten-3",
                        class: "mr-2"
                      }, {
                        default: _withCtx(() => [...(_cache[5] || (_cache[5] = [
                          _createTextVNode("mdi-duck", -1)
                        ]))]),
                        _: 1
                      }),
                      _cache[6] || (_cache[6] = _createTextVNode(" 签到打卡记录 ", -1)),
                      _createVNode(_component_v_spacer),
                      _createVNode(_component_v_chip, {
                        color: "teal-lighten-5",
                        size: "x-small",
                        variant: "elevated"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(signinSiteCount.value) + " 个站点 ", 1)
                        ]),
                        _: 1
                      })
                    ]),
                    (signinPanels.value.length > 0)
                      ? (_openBlock(), _createBlock(_component_v_expansion_panels, {
                          key: 0,
                          variant: "accordion",
                          class: "mt-2"
                        }, {
                          default: _withCtx(() => [
                            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(signinPanels.value, (panel, index) => {
                              return (_openBlock(), _createBlock(_component_v_expansion_panel, { key: index }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_v_expansion_panel_title, null, {
                                    default: _withCtx(() => [
                                      _createElementVNode("div", _hoisted_9, [
                                        _createElementVNode("div", _hoisted_10, _toDisplayString(panel.siteInitial), 1),
                                        _createElementVNode("span", _hoisted_11, _toDisplayString(panel.siteName), 1),
                                        _createVNode(_component_v_spacer),
                                        _createVNode(_component_v_icon, {
                                          color: panel.statusColor,
                                          size: "small",
                                          class: "mr-2"
                                        }, {
                                          default: _withCtx(() => [
                                            _createTextVNode(_toDisplayString(panel.statusIcon), 1)
                                          ]),
                                          _: 2
                                        }, 1032, ["color"]),
                                        _createElementVNode("span", {
                                          class: _normalizeClass(`text-${panel.statusColor} text-caption`)
                                        }, _toDisplayString(panel.latestStatus), 3)
                                      ])
                                    ]),
                                    _: 2
                                  }, 1024),
                                  _createVNode(_component_v_expansion_panel_text, null, {
                                    default: _withCtx(() => [
                                      _createVNode(_component_v_list, {
                                        lines: "one",
                                        density: "compact"
                                      }, {
                                        default: _withCtx(() => [
                                          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(panel.records, (record, idx) => {
                                            return (_openBlock(), _createBlock(_component_v_list_item, {
                                              key: idx,
                                              class: "site-item px-2 py-1"
                                            }, {
                                              default: _withCtx(() => [
                                                _createElementVNode("div", _hoisted_12, [
                                                  _createVNode(_component_v_chip, {
                                                    color: "grey-lighten-3",
                                                    size: "x-small",
                                                    class: "date-chip mr-2",
                                                    variant: "flat"
                                                  }, {
                                                    default: _withCtx(() => [
                                                      _createTextVNode(_toDisplayString(record.date), 1)
                                                    ]),
                                                    _: 2
                                                  }, 1024),
                                                  _createVNode(_component_v_spacer),
                                                  _createVNode(_component_v_chip, {
                                                    color: record.color,
                                                    size: "x-small",
                                                    class: "ml-2 status-chip",
                                                    variant: "flat"
                                                  }, {
                                                    default: _withCtx(() => [
                                                      _createVNode(_component_v_icon, {
                                                        start: "",
                                                        size: "x-small"
                                                      }, {
                                                        default: _withCtx(() => [
                                                          _createTextVNode(_toDisplayString(record.icon), 1)
                                                        ]),
                                                        _: 2
                                                      }, 1024),
                                                      _createTextVNode(" " + _toDisplayString(record.status), 1)
                                                    ]),
                                                    _: 2
                                                  }, 1032, ["color"])
                                                ])
                                              ]),
                                              _: 2
                                            }, 1024))
                                          }), 128))
                                        ]),
                                        _: 2
                                      }, 1024)
                                    ]),
                                    _: 2
                                  }, 1024)
                                ]),
                                _: 2
                              }, 1024))
                            }), 128))
                          ]),
                          _: 1
                        }))
                      : (_openBlock(), _createBlock(_component_v_alert, {
                          key: 1,
                          type: "info",
                          variant: "tonal",
                          class: "mt-4"
                        }, {
                          default: _withCtx(() => [...(_cache[7] || (_cache[7] = [
                            _createTextVNode(" 暂无签到数据 ", -1)
                          ]))]),
                          _: 1
                        }))
                  ]),
                  _createElementVNode("div", _hoisted_13, [
                    _createElementVNode("div", _hoisted_14, [
                      _createVNode(_component_v_icon, {
                        color: "light-blue-accent-3",
                        class: "mr-2"
                      }, {
                        default: _withCtx(() => [...(_cache[8] || (_cache[8] = [
                          _createTextVNode("mdi-dog", -1)
                        ]))]),
                        _: 1
                      }),
                      _cache[9] || (_cache[9] = _createTextVNode(" 登录记录 ", -1)),
                      _createVNode(_component_v_spacer),
                      _createVNode(_component_v_chip, {
                        color: "light-blue-lighten-4",
                        size: "x-small",
                        variant: "elevated"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(loginSiteCount.value) + " 个站点 ", 1)
                        ]),
                        _: 1
                      })
                    ]),
                    (loginPanels.value.length > 0)
                      ? (_openBlock(), _createBlock(_component_v_expansion_panels, {
                          key: 0,
                          variant: "accordion",
                          class: "mt-2"
                        }, {
                          default: _withCtx(() => [
                            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(loginPanels.value, (panel, index) => {
                              return (_openBlock(), _createBlock(_component_v_expansion_panel, { key: index }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_v_expansion_panel_title, null, {
                                    default: _withCtx(() => [
                                      _createElementVNode("div", _hoisted_15, [
                                        _createElementVNode("div", _hoisted_16, _toDisplayString(panel.siteInitial), 1),
                                        _createElementVNode("span", _hoisted_17, _toDisplayString(panel.siteName), 1),
                                        _createVNode(_component_v_spacer),
                                        _createVNode(_component_v_icon, {
                                          color: panel.statusColor,
                                          size: "small",
                                          class: "mr-2"
                                        }, {
                                          default: _withCtx(() => [
                                            _createTextVNode(_toDisplayString(panel.statusIcon), 1)
                                          ]),
                                          _: 2
                                        }, 1032, ["color"]),
                                        _createElementVNode("span", {
                                          class: _normalizeClass(`text-${panel.statusColor} text-caption`)
                                        }, _toDisplayString(panel.latestStatus), 3)
                                      ])
                                    ]),
                                    _: 2
                                  }, 1024),
                                  _createVNode(_component_v_expansion_panel_text, null, {
                                    default: _withCtx(() => [
                                      _createVNode(_component_v_list, {
                                        lines: "one",
                                        density: "compact"
                                      }, {
                                        default: _withCtx(() => [
                                          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(panel.records, (record, idx) => {
                                            return (_openBlock(), _createBlock(_component_v_list_item, {
                                              key: idx,
                                              class: "site-item px-2 py-1"
                                            }, {
                                              default: _withCtx(() => [
                                                _createElementVNode("div", _hoisted_18, [
                                                  _createVNode(_component_v_chip, {
                                                    color: "grey-lighten-3",
                                                    size: "x-small",
                                                    class: "date-chip mr-2",
                                                    variant: "flat"
                                                  }, {
                                                    default: _withCtx(() => [
                                                      _createTextVNode(_toDisplayString(record.date), 1)
                                                    ]),
                                                    _: 2
                                                  }, 1024),
                                                  _createVNode(_component_v_spacer),
                                                  _createVNode(_component_v_chip, {
                                                    color: record.color,
                                                    size: "x-small",
                                                    class: "ml-2 status-chip",
                                                    variant: "flat"
                                                  }, {
                                                    default: _withCtx(() => [
                                                      _createVNode(_component_v_icon, {
                                                        start: "",
                                                        size: "x-small"
                                                      }, {
                                                        default: _withCtx(() => [
                                                          _createTextVNode(_toDisplayString(record.icon), 1)
                                                        ]),
                                                        _: 2
                                                      }, 1024),
                                                      _createTextVNode(" " + _toDisplayString(record.status), 1)
                                                    ]),
                                                    _: 2
                                                  }, 1032, ["color"])
                                                ])
                                              ]),
                                              _: 2
                                            }, 1024))
                                          }), 128))
                                        ]),
                                        _: 2
                                      }, 1024)
                                    ]),
                                    _: 2
                                  }, 1024)
                                ]),
                                _: 2
                              }, 1024))
                            }), 128))
                          ]),
                          _: 1
                        }))
                      : (_openBlock(), _createBlock(_component_v_alert, {
                          key: 1,
                          type: "info",
                          variant: "tonal",
                          class: "mt-4"
                        }, {
                          default: _withCtx(() => [...(_cache[10] || (_cache[10] = [
                            _createTextVNode(" 暂无登录数据 ", -1)
                          ]))]),
                          _: 1
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
                  default: _withCtx(() => [...(_cache[11] || (_cache[11] = [
                    _createTextVNode("mdi-refresh", -1)
                  ]))]),
                  _: 1
                }),
                _cache[12] || (_cache[12] = _createTextVNode(" 刷新数据 ", -1))
              ]),
              _: 1
            }, 8, ["loading"]),
            _createVNode(_component_v_spacer),
            _createVNode(_component_v_btn, {
              color: "primary",
              onClick: notifySwitch
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, { start: "" }, {
                  default: _withCtx(() => [...(_cache[13] || (_cache[13] = [
                    _createTextVNode("mdi-cog", -1)
                  ]))]),
                  _: 1
                }),
                _cache[14] || (_cache[14] = _createTextVNode(" 配置 ", -1))
              ]),
              _: 1
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
const PageComponent = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-0fd77b50"]]);

export { _export_sfc as _, PageComponent as default };
