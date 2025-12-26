import { importShared } from './__federation_fn_import-JrT3xvdd.js';

var __defProp = Object.defineProperty;
var __getOwnPropSymbols = Object.getOwnPropertySymbols;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __propIsEnum = Object.prototype.propertyIsEnumerable;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __spreadValues = (a, b) => {
  for (var prop in b || (b = {}))
    if (__hasOwnProp.call(b, prop))
      __defNormalProp(a, prop, b[prop]);
  if (__getOwnPropSymbols)
    for (var prop of __getOwnPropSymbols(b)) {
      if (__propIsEnum.call(b, prop))
        __defNormalProp(a, prop, b[prop]);
    }
  return a;
};

// src/index.ts
const {provide,inject,getCurrentInstance} = await importShared('vue');


// src/ts/interface.ts
const {createApp,nextTick} = await importShared('vue');


// src/ts/utils.ts
const {defineComponent,toRaw,unref} = await importShared('vue');

var isFunction = (value) => typeof value === "function";
var isString = (value) => typeof value === "string";
var isNonEmptyString = (value) => isString(value) && value.trim().length > 0;
var isNumber = (value) => typeof value === "number";
var isUndefined = (value) => typeof value === "undefined";
var isObject = (value) => typeof value === "object" && value !== null;
var isJSX = (obj) => hasProp(obj, "tag") && isNonEmptyString(obj.tag);
var isTouchEvent = (event) => window.TouchEvent && event instanceof TouchEvent;
var isToastComponent = (obj) => hasProp(obj, "component") && isToastContent(obj.component);
var isVueComponent = (c) => isFunction(c) || isObject(c);
var isToastContent = (obj) => !isUndefined(obj) && (isString(obj) || isVueComponent(obj) || isToastComponent(obj));
var isDOMRect = (obj) => isObject(obj) && ["height", "width", "right", "left", "top", "bottom"].every((p) => isNumber(obj[p]));
var hasProp = (obj, propKey) => (isObject(obj) || isFunction(obj)) && propKey in obj;
var getId = ((i) => () => i++)(0);
function getX(event) {
  return isTouchEvent(event) ? event.targetTouches[0].clientX : event.clientX;
}
function getY(event) {
  return isTouchEvent(event) ? event.targetTouches[0].clientY : event.clientY;
}
var removeElement = (el) => {
  if (!isUndefined(el.remove)) {
    el.remove();
  } else if (el.parentNode) {
    el.parentNode.removeChild(el);
  }
};
var getVueComponentFromObj = (obj) => {
  if (isToastComponent(obj)) {
    return getVueComponentFromObj(obj.component);
  }
  if (isJSX(obj)) {
    return defineComponent({
      render() {
        return obj;
      }
    });
  }
  return typeof obj === "string" ? obj : toRaw(unref(obj));
};
var normalizeToastComponent = (obj) => {
  if (typeof obj === "string") {
    return obj;
  }
  const props = hasProp(obj, "props") && isObject(obj.props) ? obj.props : {};
  const listeners = hasProp(obj, "listeners") && isObject(obj.listeners) ? obj.listeners : {};
  return { component: getVueComponentFromObj(obj), props, listeners };
};
var isBrowser = () => typeof window !== "undefined";

// src/ts/eventBus.ts
var EventBus = class {
  constructor() {
    this.allHandlers = {};
  }
  getHandlers(eventType) {
    return this.allHandlers[eventType] || [];
  }
  on(eventType, handler) {
    const handlers = this.getHandlers(eventType);
    handlers.push(handler);
    this.allHandlers[eventType] = handlers;
  }
  off(eventType, handler) {
    const handlers = this.getHandlers(eventType);
    handlers.splice(handlers.indexOf(handler) >>> 0, 1);
  }
  emit(eventType, event) {
    const handlers = this.getHandlers(eventType);
    handlers.forEach((handler) => handler(event));
  }
};
var isEventBusInterface = (e) => ["on", "off", "emit"].every((f) => hasProp(e, f) && isFunction(e[f]));

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtToastContainer.vue?vue&type=script
const {defineComponent:defineComponent7} = await importShared('vue');


// src/ts/constants.ts
var TYPE;
(function(TYPE2) {
  TYPE2["SUCCESS"] = "success";
  TYPE2["ERROR"] = "error";
  TYPE2["WARNING"] = "warning";
  TYPE2["INFO"] = "info";
  TYPE2["DEFAULT"] = "default";
})(TYPE || (TYPE = {}));
var POSITION;
(function(POSITION2) {
  POSITION2["TOP_LEFT"] = "top-left";
  POSITION2["TOP_CENTER"] = "top-center";
  POSITION2["TOP_RIGHT"] = "top-right";
  POSITION2["BOTTOM_LEFT"] = "bottom-left";
  POSITION2["BOTTOM_CENTER"] = "bottom-center";
  POSITION2["BOTTOM_RIGHT"] = "bottom-right";
})(POSITION || (POSITION = {}));
var EVENTS;
(function(EVENTS2) {
  EVENTS2["ADD"] = "add";
  EVENTS2["DISMISS"] = "dismiss";
  EVENTS2["UPDATE"] = "update";
  EVENTS2["CLEAR"] = "clear";
  EVENTS2["UPDATE_DEFAULTS"] = "update_defaults";
})(EVENTS || (EVENTS = {}));
var VT_NAMESPACE = "Vue-Toastification";

// src/ts/propValidators.ts
var COMMON = {
  type: {
    type: String,
    default: TYPE.DEFAULT
  },
  classNames: {
    type: [String, Array],
    default: () => []
  },
  trueBoolean: {
    type: Boolean,
    default: true
  }
};
var ICON = {
  type: COMMON.type,
  customIcon: {
    type: [String, Boolean, Object, Function],
    default: true
  }
};
var CLOSE_BUTTON = {
  component: {
    type: [String, Object, Function, Boolean],
    default: "button"
  },
  classNames: COMMON.classNames,
  showOnHover: {
    type: Boolean,
    default: false
  },
  ariaLabel: {
    type: String,
    default: "close"
  }
};
var PROGRESS_BAR = {
  timeout: {
    type: [Number, Boolean],
    default: 5e3
  },
  hideProgressBar: {
    type: Boolean,
    default: false
  },
  isRunning: {
    type: Boolean,
    default: false
  }
};
var TRANSITION = {
  transition: {
    type: [Object, String],
    default: `${VT_NAMESPACE}__bounce`
  }
};
var CORE_TOAST = {
  position: {
    type: String,
    default: POSITION.TOP_RIGHT
  },
  draggable: COMMON.trueBoolean,
  draggablePercent: {
    type: Number,
    default: 0.6
  },
  pauseOnFocusLoss: COMMON.trueBoolean,
  pauseOnHover: COMMON.trueBoolean,
  closeOnClick: COMMON.trueBoolean,
  timeout: PROGRESS_BAR.timeout,
  hideProgressBar: PROGRESS_BAR.hideProgressBar,
  toastClassName: COMMON.classNames,
  bodyClassName: COMMON.classNames,
  icon: ICON.customIcon,
  closeButton: CLOSE_BUTTON.component,
  closeButtonClassName: CLOSE_BUTTON.classNames,
  showCloseButtonOnHover: CLOSE_BUTTON.showOnHover,
  accessibility: {
    type: Object,
    default: () => ({
      toastRole: "alert",
      closeButtonLabel: "close"
    })
  },
  rtl: {
    type: Boolean,
    default: false
  },
  eventBus: {
    type: Object,
    required: false,
    default: () => new EventBus()
  }
};
var TOAST = {
  id: {
    type: [String, Number],
    required: true,
    default: 0
  },
  type: COMMON.type,
  content: {
    type: [String, Object, Function],
    required: true,
    default: ""
  },
  onClick: {
    type: Function,
    default: void 0
  },
  onClose: {
    type: Function,
    default: void 0
  }
};
var CONTAINER = {
  container: {
    type: [
      Object,
      Function
    ],
    default: () => document.body
  },
  newestOnTop: COMMON.trueBoolean,
  maxToasts: {
    type: Number,
    default: 20
  },
  transition: TRANSITION.transition,
  toastDefaults: Object,
  filterBeforeCreate: {
    type: Function,
    default: (toast) => toast
  },
  filterToasts: {
    type: Function,
    default: (toasts) => toasts
  },
  containerClassName: COMMON.classNames,
  onMounted: Function,
  shareAppContext: [Boolean, Object]
};
var propValidators_default = {
  CORE_TOAST,
  TOAST,
  CONTAINER,
  PROGRESS_BAR,
  ICON,
  TRANSITION,
  CLOSE_BUTTON
};

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtToast.vue?vue&type=script
const {defineComponent:defineComponent5} = await importShared('vue');


// vue:/Users/maronato/Developer/vue-toastification/src/components/VtProgressBar.vue?vue&type=script
const {defineComponent:defineComponent2} = await importShared('vue');

var VtProgressBar_default = defineComponent2({
  name: "VtProgressBar",
  props: propValidators_default.PROGRESS_BAR,
  data() {
    return {
      hasClass: true
    };
  },
  computed: {
    style() {
      return {
        animationDuration: `${this.timeout}ms`,
        animationPlayState: this.isRunning ? "running" : "paused",
        opacity: this.hideProgressBar ? 0 : 1
      };
    },
    cpClass() {
      return this.hasClass ? `${VT_NAMESPACE}__progress-bar` : "";
    }
  },
  watch: {
    timeout() {
      this.hasClass = false;
      this.$nextTick(() => this.hasClass = true);
    }
  },
  mounted() {
    this.$el.addEventListener("animationend", this.animationEnded);
  },
  beforeUnmount() {
    this.$el.removeEventListener("animationend", this.animationEnded);
  },
  methods: {
    animationEnded() {
      this.$emit("close-toast");
    }
  }
});

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtProgressBar.vue?vue&type=template
const {normalizeClass:_normalizeClass,normalizeStyle:_normalizeStyle,openBlock:_openBlock$1,createElementBlock:_createElementBlock$1} = await importShared('vue');

function render(_ctx, _cache) {
  return _openBlock$1(), _createElementBlock$1("div", {
    style: _normalizeStyle(_ctx.style),
    class: _normalizeClass(_ctx.cpClass)
  }, null, 6);
}

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtProgressBar.vue
VtProgressBar_default.render = render;
var VtProgressBar_default2 = VtProgressBar_default;

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtCloseButton.vue?vue&type=script
const {defineComponent:defineComponent3} = await importShared('vue');

var VtCloseButton_default = defineComponent3({
  name: "VtCloseButton",
  props: propValidators_default.CLOSE_BUTTON,
  computed: {
    buttonComponent() {
      if (this.component !== false) {
        return getVueComponentFromObj(this.component);
      }
      return "button";
    },
    classes() {
      const classes = [`${VT_NAMESPACE}__close-button`];
      if (this.showOnHover) {
        classes.push("show-on-hover");
      }
      return classes.concat(this.classNames);
    }
  }
});

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtCloseButton.vue?vue&type=template
const {createTextVNode:_createTextVNode$1,resolveDynamicComponent:_resolveDynamicComponent,mergeProps:_mergeProps,withCtx:_withCtx$1,openBlock:_openBlock2,createBlock:_createBlock$1} = await importShared('vue');

var _hoisted_1$1 = /* @__PURE__ */ _createTextVNode$1(" \xD7 ");
function render2(_ctx, _cache) {
  return _openBlock2(), _createBlock$1(_resolveDynamicComponent(_ctx.buttonComponent), _mergeProps({
    "aria-label": _ctx.ariaLabel,
    class: _ctx.classes
  }, _ctx.$attrs), {
    default: _withCtx$1(() => [
      _hoisted_1$1
    ]),
    _: 1
  }, 16, ["aria-label", "class"]);
}

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtCloseButton.vue
VtCloseButton_default.render = render2;
var VtCloseButton_default2 = VtCloseButton_default;

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtIcon.vue?vue&type=script
const {defineComponent:defineComponent4} = await importShared('vue');


// vue:/Users/maronato/Developer/vue-toastification/src/components/icons/VtSuccessIcon.vue?vue&type=script
var VtSuccessIcon_default = {};

// vue:/Users/maronato/Developer/vue-toastification/src/components/icons/VtSuccessIcon.vue?vue&type=template
const {createElementVNode:_createElementVNode$1,openBlock:_openBlock3,createElementBlock:_createElementBlock2} = await importShared('vue');

var _hoisted_12 = {
  "aria-hidden": "true",
  focusable: "false",
  "data-prefix": "fas",
  "data-icon": "check-circle",
  class: "svg-inline--fa fa-check-circle fa-w-16",
  role: "img",
  xmlns: "http://www.w3.org/2000/svg",
  viewBox: "0 0 512 512"
};
var _hoisted_2$1 = /* @__PURE__ */ _createElementVNode$1("path", {
  fill: "currentColor",
  d: "M504 256c0 136.967-111.033 248-248 248S8 392.967 8 256 119.033 8 256 8s248 111.033 248 248zM227.314 387.314l184-184c6.248-6.248 6.248-16.379 0-22.627l-22.627-22.627c-6.248-6.249-16.379-6.249-22.628 0L216 308.118l-70.059-70.059c-6.248-6.248-16.379-6.248-22.628 0l-22.627 22.627c-6.248 6.248-6.248 16.379 0 22.627l104 104c6.249 6.249 16.379 6.249 22.628.001z"
}, null, -1);
var _hoisted_3 = [
  _hoisted_2$1
];
function render3(_ctx, _cache) {
  return _openBlock3(), _createElementBlock2("svg", _hoisted_12, _hoisted_3);
}

// vue:/Users/maronato/Developer/vue-toastification/src/components/icons/VtSuccessIcon.vue
VtSuccessIcon_default.render = render3;
var VtSuccessIcon_default2 = VtSuccessIcon_default;

// vue:/Users/maronato/Developer/vue-toastification/src/components/icons/VtInfoIcon.vue?vue&type=script
var VtInfoIcon_default = {};

// vue:/Users/maronato/Developer/vue-toastification/src/components/icons/VtInfoIcon.vue?vue&type=template
const {createElementVNode:_createElementVNode2,openBlock:_openBlock4,createElementBlock:_createElementBlock3} = await importShared('vue');

var _hoisted_13 = {
  "aria-hidden": "true",
  focusable: "false",
  "data-prefix": "fas",
  "data-icon": "info-circle",
  class: "svg-inline--fa fa-info-circle fa-w-16",
  role: "img",
  xmlns: "http://www.w3.org/2000/svg",
  viewBox: "0 0 512 512"
};
var _hoisted_22 = /* @__PURE__ */ _createElementVNode2("path", {
  fill: "currentColor",
  d: "M256 8C119.043 8 8 119.083 8 256c0 136.997 111.043 248 248 248s248-111.003 248-248C504 119.083 392.957 8 256 8zm0 110c23.196 0 42 18.804 42 42s-18.804 42-42 42-42-18.804-42-42 18.804-42 42-42zm56 254c0 6.627-5.373 12-12 12h-88c-6.627 0-12-5.373-12-12v-24c0-6.627 5.373-12 12-12h12v-64h-12c-6.627 0-12-5.373-12-12v-24c0-6.627 5.373-12 12-12h64c6.627 0 12 5.373 12 12v100h12c6.627 0 12 5.373 12 12v24z"
}, null, -1);
var _hoisted_32 = [
  _hoisted_22
];
function render4(_ctx, _cache) {
  return _openBlock4(), _createElementBlock3("svg", _hoisted_13, _hoisted_32);
}

// vue:/Users/maronato/Developer/vue-toastification/src/components/icons/VtInfoIcon.vue
VtInfoIcon_default.render = render4;
var VtInfoIcon_default2 = VtInfoIcon_default;

// vue:/Users/maronato/Developer/vue-toastification/src/components/icons/VtWarningIcon.vue?vue&type=script
var VtWarningIcon_default = {};

// vue:/Users/maronato/Developer/vue-toastification/src/components/icons/VtWarningIcon.vue?vue&type=template
const {createElementVNode:_createElementVNode3,openBlock:_openBlock5,createElementBlock:_createElementBlock4} = await importShared('vue');

var _hoisted_14 = {
  "aria-hidden": "true",
  focusable: "false",
  "data-prefix": "fas",
  "data-icon": "exclamation-circle",
  class: "svg-inline--fa fa-exclamation-circle fa-w-16",
  role: "img",
  xmlns: "http://www.w3.org/2000/svg",
  viewBox: "0 0 512 512"
};
var _hoisted_23 = /* @__PURE__ */ _createElementVNode3("path", {
  fill: "currentColor",
  d: "M504 256c0 136.997-111.043 248-248 248S8 392.997 8 256C8 119.083 119.043 8 256 8s248 111.083 248 248zm-248 50c-25.405 0-46 20.595-46 46s20.595 46 46 46 46-20.595 46-46-20.595-46-46-46zm-43.673-165.346l7.418 136c.347 6.364 5.609 11.346 11.982 11.346h48.546c6.373 0 11.635-4.982 11.982-11.346l7.418-136c.375-6.874-5.098-12.654-11.982-12.654h-63.383c-6.884 0-12.356 5.78-11.981 12.654z"
}, null, -1);
var _hoisted_33 = [
  _hoisted_23
];
function render5(_ctx, _cache) {
  return _openBlock5(), _createElementBlock4("svg", _hoisted_14, _hoisted_33);
}

// vue:/Users/maronato/Developer/vue-toastification/src/components/icons/VtWarningIcon.vue
VtWarningIcon_default.render = render5;
var VtWarningIcon_default2 = VtWarningIcon_default;

// vue:/Users/maronato/Developer/vue-toastification/src/components/icons/VtErrorIcon.vue?vue&type=script
var VtErrorIcon_default = {};

// vue:/Users/maronato/Developer/vue-toastification/src/components/icons/VtErrorIcon.vue?vue&type=template
const {createElementVNode:_createElementVNode4,openBlock:_openBlock6,createElementBlock:_createElementBlock5} = await importShared('vue');

var _hoisted_15 = {
  "aria-hidden": "true",
  focusable: "false",
  "data-prefix": "fas",
  "data-icon": "exclamation-triangle",
  class: "svg-inline--fa fa-exclamation-triangle fa-w-18",
  role: "img",
  xmlns: "http://www.w3.org/2000/svg",
  viewBox: "0 0 576 512"
};
var _hoisted_24 = /* @__PURE__ */ _createElementVNode4("path", {
  fill: "currentColor",
  d: "M569.517 440.013C587.975 472.007 564.806 512 527.94 512H48.054c-36.937 0-59.999-40.055-41.577-71.987L246.423 23.985c18.467-32.009 64.72-31.951 83.154 0l239.94 416.028zM288 354c-25.405 0-46 20.595-46 46s20.595 46 46 46 46-20.595 46-46-20.595-46-46-46zm-43.673-165.346l7.418 136c.347 6.364 5.609 11.346 11.982 11.346h48.546c6.373 0 11.635-4.982 11.982-11.346l7.418-136c.375-6.874-5.098-12.654-11.982-12.654h-63.383c-6.884 0-12.356 5.78-11.981 12.654z"
}, null, -1);
var _hoisted_34 = [
  _hoisted_24
];
function render6(_ctx, _cache) {
  return _openBlock6(), _createElementBlock5("svg", _hoisted_15, _hoisted_34);
}

// vue:/Users/maronato/Developer/vue-toastification/src/components/icons/VtErrorIcon.vue
VtErrorIcon_default.render = render6;
var VtErrorIcon_default2 = VtErrorIcon_default;

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtIcon.vue?vue&type=script
var VtIcon_default = defineComponent4({
  name: "VtIcon",
  props: propValidators_default.ICON,
  computed: {
    customIconChildren() {
      return hasProp(this.customIcon, "iconChildren") ? this.trimValue(this.customIcon.iconChildren) : "";
    },
    customIconClass() {
      if (isString(this.customIcon)) {
        return this.trimValue(this.customIcon);
      } else if (hasProp(this.customIcon, "iconClass")) {
        return this.trimValue(this.customIcon.iconClass);
      }
      return "";
    },
    customIconTag() {
      if (hasProp(this.customIcon, "iconTag")) {
        return this.trimValue(this.customIcon.iconTag, "i");
      }
      return "i";
    },
    hasCustomIcon() {
      return this.customIconClass.length > 0;
    },
    component() {
      if (this.hasCustomIcon) {
        return this.customIconTag;
      }
      if (isToastContent(this.customIcon)) {
        return getVueComponentFromObj(this.customIcon);
      }
      return this.iconTypeComponent;
    },
    iconTypeComponent() {
      const types = {
        [TYPE.DEFAULT]: VtInfoIcon_default2,
        [TYPE.INFO]: VtInfoIcon_default2,
        [TYPE.SUCCESS]: VtSuccessIcon_default2,
        [TYPE.ERROR]: VtErrorIcon_default2,
        [TYPE.WARNING]: VtWarningIcon_default2
      };
      return types[this.type];
    },
    iconClasses() {
      const classes = [`${VT_NAMESPACE}__icon`];
      if (this.hasCustomIcon) {
        return classes.concat(this.customIconClass);
      }
      return classes;
    }
  },
  methods: {
    trimValue(value, empty = "") {
      return isNonEmptyString(value) ? value.trim() : empty;
    }
  }
});

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtIcon.vue?vue&type=template
const {toDisplayString:_toDisplayString$1,createTextVNode:_createTextVNode2,resolveDynamicComponent:_resolveDynamicComponent2,normalizeClass:_normalizeClass2,withCtx:_withCtx2,openBlock:_openBlock7,createBlock:_createBlock2} = await importShared('vue');

function render7(_ctx, _cache) {
  return _openBlock7(), _createBlock2(_resolveDynamicComponent2(_ctx.component), {
    class: _normalizeClass2(_ctx.iconClasses)
  }, {
    default: _withCtx2(() => [
      _createTextVNode2(_toDisplayString$1(_ctx.customIconChildren), 1)
    ]),
    _: 1
  }, 8, ["class"]);
}

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtIcon.vue
VtIcon_default.render = render7;
var VtIcon_default2 = VtIcon_default;

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtToast.vue?vue&type=script
var VtToast_default = defineComponent5({
  name: "VtToast",
  components: { ProgressBar: VtProgressBar_default2, CloseButton: VtCloseButton_default2, Icon: VtIcon_default2 },
  inheritAttrs: false,
  props: Object.assign({}, propValidators_default.CORE_TOAST, propValidators_default.TOAST),
  data() {
    const data = {
      isRunning: true,
      disableTransitions: false,
      beingDragged: false,
      dragStart: 0,
      dragPos: { x: 0, y: 0 },
      dragRect: {}
    };
    return data;
  },
  computed: {
    classes() {
      const classes = [
        `${VT_NAMESPACE}__toast`,
        `${VT_NAMESPACE}__toast--${this.type}`,
        `${this.position}`
      ].concat(this.toastClassName);
      if (this.disableTransitions) {
        classes.push("disable-transition");
      }
      if (this.rtl) {
        classes.push(`${VT_NAMESPACE}__toast--rtl`);
      }
      return classes;
    },
    bodyClasses() {
      const classes = [
        `${VT_NAMESPACE}__toast-${isString(this.content) ? "body" : "component-body"}`
      ].concat(this.bodyClassName);
      return classes;
    },
    draggableStyle() {
      if (this.dragStart === this.dragPos.x) {
        return {};
      } else if (this.beingDragged) {
        return {
          transform: `translateX(${this.dragDelta}px)`,
          opacity: 1 - Math.abs(this.dragDelta / this.removalDistance)
        };
      } else {
        return {
          transition: "transform 0.2s, opacity 0.2s",
          transform: "translateX(0)",
          opacity: 1
        };
      }
    },
    dragDelta() {
      return this.beingDragged ? this.dragPos.x - this.dragStart : 0;
    },
    removalDistance() {
      if (isDOMRect(this.dragRect)) {
        return (this.dragRect.right - this.dragRect.left) * this.draggablePercent;
      }
      return 0;
    }
  },
  mounted() {
    if (this.draggable) {
      this.draggableSetup();
    }
    if (this.pauseOnFocusLoss) {
      this.focusSetup();
    }
  },
  beforeUnmount() {
    if (this.draggable) {
      this.draggableCleanup();
    }
    if (this.pauseOnFocusLoss) {
      this.focusCleanup();
    }
  },
  methods: {
    hasProp,
    getVueComponentFromObj,
    closeToast() {
      this.eventBus.emit(EVENTS.DISMISS, this.id);
    },
    clickHandler() {
      if (this.onClick) {
        this.onClick(this.closeToast);
      }
      if (this.closeOnClick) {
        if (!this.beingDragged || this.dragStart === this.dragPos.x) {
          this.closeToast();
        }
      }
    },
    timeoutHandler() {
      this.closeToast();
    },
    hoverPause() {
      if (this.pauseOnHover) {
        this.isRunning = false;
      }
    },
    hoverPlay() {
      if (this.pauseOnHover) {
        this.isRunning = true;
      }
    },
    focusPause() {
      this.isRunning = false;
    },
    focusPlay() {
      this.isRunning = true;
    },
    focusSetup() {
      addEventListener("blur", this.focusPause);
      addEventListener("focus", this.focusPlay);
    },
    focusCleanup() {
      removeEventListener("blur", this.focusPause);
      removeEventListener("focus", this.focusPlay);
    },
    draggableSetup() {
      const element = this.$el;
      element.addEventListener("touchstart", this.onDragStart, {
        passive: true
      });
      element.addEventListener("mousedown", this.onDragStart);
      addEventListener("touchmove", this.onDragMove, { passive: false });
      addEventListener("mousemove", this.onDragMove);
      addEventListener("touchend", this.onDragEnd);
      addEventListener("mouseup", this.onDragEnd);
    },
    draggableCleanup() {
      const element = this.$el;
      element.removeEventListener("touchstart", this.onDragStart);
      element.removeEventListener("mousedown", this.onDragStart);
      removeEventListener("touchmove", this.onDragMove);
      removeEventListener("mousemove", this.onDragMove);
      removeEventListener("touchend", this.onDragEnd);
      removeEventListener("mouseup", this.onDragEnd);
    },
    onDragStart(event) {
      this.beingDragged = true;
      this.dragPos = { x: getX(event), y: getY(event) };
      this.dragStart = getX(event);
      this.dragRect = this.$el.getBoundingClientRect();
    },
    onDragMove(event) {
      if (this.beingDragged) {
        event.preventDefault();
        if (this.isRunning) {
          this.isRunning = false;
        }
        this.dragPos = { x: getX(event), y: getY(event) };
      }
    },
    onDragEnd() {
      if (this.beingDragged) {
        if (Math.abs(this.dragDelta) >= this.removalDistance) {
          this.disableTransitions = true;
          this.$nextTick(() => this.closeToast());
        } else {
          setTimeout(() => {
            this.beingDragged = false;
            if (isDOMRect(this.dragRect) && this.pauseOnHover && this.dragRect.bottom >= this.dragPos.y && this.dragPos.y >= this.dragRect.top && this.dragRect.left <= this.dragPos.x && this.dragPos.x <= this.dragRect.right) {
              this.isRunning = false;
            } else {
              this.isRunning = true;
            }
          });
        }
      }
    }
  }
});

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtToast.vue?vue&type=template
const {resolveComponent:_resolveComponent$1,openBlock:_openBlock8,createBlock:_createBlock3,createCommentVNode:_createCommentVNode$1,toDisplayString:_toDisplayString2,createTextVNode:_createTextVNode3,Fragment:_Fragment,createElementBlock:_createElementBlock6,resolveDynamicComponent:_resolveDynamicComponent3,toHandlers:_toHandlers,mergeProps:_mergeProps2,normalizeClass:_normalizeClass3,createElementVNode:_createElementVNode5,withModifiers:_withModifiers,normalizeStyle:_normalizeStyle2} = await importShared('vue');

var _hoisted_16 = ["role"];
function render8(_ctx, _cache) {
  const _component_Icon = _resolveComponent$1("Icon");
  const _component_CloseButton = _resolveComponent$1("CloseButton");
  const _component_ProgressBar = _resolveComponent$1("ProgressBar");
  return _openBlock8(), _createElementBlock6("div", {
    class: _normalizeClass3(_ctx.classes),
    style: _normalizeStyle2(_ctx.draggableStyle),
    onClick: _cache[0] || (_cache[0] = (...args) => _ctx.clickHandler && _ctx.clickHandler(...args)),
    onMouseenter: _cache[1] || (_cache[1] = (...args) => _ctx.hoverPause && _ctx.hoverPause(...args)),
    onMouseleave: _cache[2] || (_cache[2] = (...args) => _ctx.hoverPlay && _ctx.hoverPlay(...args))
  }, [
    _ctx.icon ? (_openBlock8(), _createBlock3(_component_Icon, {
      key: 0,
      "custom-icon": _ctx.icon,
      type: _ctx.type
    }, null, 8, ["custom-icon", "type"])) : _createCommentVNode$1("v-if", true),
    _createElementVNode5("div", {
      role: _ctx.accessibility.toastRole || "alert",
      class: _normalizeClass3(_ctx.bodyClasses)
    }, [
      typeof _ctx.content === "string" ? (_openBlock8(), _createElementBlock6(_Fragment, { key: 0 }, [
        _createTextVNode3(_toDisplayString2(_ctx.content), 1)
      ], 2112)) : (_openBlock8(), _createBlock3(_resolveDynamicComponent3(_ctx.getVueComponentFromObj(_ctx.content)), _mergeProps2({
        key: 1,
        "toast-id": _ctx.id
      }, _ctx.hasProp(_ctx.content, "props") ? _ctx.content.props : {}, _toHandlers(_ctx.hasProp(_ctx.content, "listeners") ? _ctx.content.listeners : {}), { onCloseToast: _ctx.closeToast }), null, 16, ["toast-id", "onCloseToast"]))
    ], 10, _hoisted_16),
    !!_ctx.closeButton ? (_openBlock8(), _createBlock3(_component_CloseButton, {
      key: 1,
      component: _ctx.closeButton,
      "class-names": _ctx.closeButtonClassName,
      "show-on-hover": _ctx.showCloseButtonOnHover,
      "aria-label": _ctx.accessibility.closeButtonLabel,
      onClick: _withModifiers(_ctx.closeToast, ["stop"])
    }, null, 8, ["component", "class-names", "show-on-hover", "aria-label", "onClick"])) : _createCommentVNode$1("v-if", true),
    _ctx.timeout ? (_openBlock8(), _createBlock3(_component_ProgressBar, {
      key: 2,
      "is-running": _ctx.isRunning,
      "hide-progress-bar": _ctx.hideProgressBar,
      timeout: _ctx.timeout,
      onCloseToast: _ctx.timeoutHandler
    }, null, 8, ["is-running", "hide-progress-bar", "timeout", "onCloseToast"])) : _createCommentVNode$1("v-if", true)
  ], 38);
}

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtToast.vue
VtToast_default.render = render8;
var VtToast_default2 = VtToast_default;

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtTransition.vue?vue&type=script
const {defineComponent:defineComponent6} = await importShared('vue');

var VtTransition_default = defineComponent6({
  name: "VtTransition",
  props: propValidators_default.TRANSITION,
  emits: ["leave"],
  methods: {
    hasProp,
    leave(el) {
      if (el instanceof HTMLElement) {
        el.style.left = el.offsetLeft + "px";
        el.style.top = el.offsetTop + "px";
        el.style.width = getComputedStyle(el).width;
        el.style.position = "absolute";
      }
    }
  }
});

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtTransition.vue?vue&type=template
const {renderSlot:_renderSlot,TransitionGroup:_TransitionGroup,withCtx:_withCtx3,openBlock:_openBlock9,createBlock:_createBlock4} = await importShared('vue');

function render9(_ctx, _cache) {
  return _openBlock9(), _createBlock4(_TransitionGroup, {
    tag: "div",
    "enter-active-class": _ctx.transition.enter ? _ctx.transition.enter : `${_ctx.transition}-enter-active`,
    "move-class": _ctx.transition.move ? _ctx.transition.move : `${_ctx.transition}-move`,
    "leave-active-class": _ctx.transition.leave ? _ctx.transition.leave : `${_ctx.transition}-leave-active`,
    onLeave: _ctx.leave
  }, {
    default: _withCtx3(() => [
      _renderSlot(_ctx.$slots, "default")
    ]),
    _: 3
  }, 8, ["enter-active-class", "move-class", "leave-active-class", "onLeave"]);
}

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtTransition.vue
VtTransition_default.render = render9;
var VtTransition_default2 = VtTransition_default;

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtToastContainer.vue?vue&type=script
var VtToastContainer_default = defineComponent7({
  name: "VueToastification",
  devtools: {
    hide: true
  },
  components: { Toast: VtToast_default2, VtTransition: VtTransition_default2 },
  props: Object.assign({}, propValidators_default.CORE_TOAST, propValidators_default.CONTAINER, propValidators_default.TRANSITION),
  data() {
    const data = {
      count: 0,
      positions: Object.values(POSITION),
      toasts: {},
      defaults: {}
    };
    return data;
  },
  computed: {
    toastArray() {
      return Object.values(this.toasts);
    },
    filteredToasts() {
      return this.defaults.filterToasts(this.toastArray);
    }
  },
  beforeMount() {
    const events = this.eventBus;
    events.on(EVENTS.ADD, this.addToast);
    events.on(EVENTS.CLEAR, this.clearToasts);
    events.on(EVENTS.DISMISS, this.dismissToast);
    events.on(EVENTS.UPDATE, this.updateToast);
    events.on(EVENTS.UPDATE_DEFAULTS, this.updateDefaults);
    this.defaults = this.$props;
  },
  mounted() {
    this.setup(this.container);
  },
  methods: {
    async setup(container) {
      if (isFunction(container)) {
        container = await container();
      }
      removeElement(this.$el);
      container.appendChild(this.$el);
    },
    setToast(props) {
      if (!isUndefined(props.id)) {
        this.toasts[props.id] = props;
      }
    },
    addToast(params) {
      params.content = normalizeToastComponent(params.content);
      const props = Object.assign({}, this.defaults, params.type && this.defaults.toastDefaults && this.defaults.toastDefaults[params.type], params);
      const toast = this.defaults.filterBeforeCreate(props, this.toastArray);
      toast && this.setToast(toast);
    },
    dismissToast(id) {
      const toast = this.toasts[id];
      if (!isUndefined(toast) && !isUndefined(toast.onClose)) {
        toast.onClose();
      }
      delete this.toasts[id];
    },
    clearToasts() {
      Object.keys(this.toasts).forEach((id) => {
        this.dismissToast(id);
      });
    },
    getPositionToasts(position) {
      const toasts = this.filteredToasts.filter((toast) => toast.position === position).slice(0, this.defaults.maxToasts);
      return this.defaults.newestOnTop ? toasts.reverse() : toasts;
    },
    updateDefaults(update) {
      if (!isUndefined(update.container)) {
        this.setup(update.container);
      }
      this.defaults = Object.assign({}, this.defaults, update);
    },
    updateToast({
      id,
      options,
      create
    }) {
      if (this.toasts[id]) {
        if (options.timeout && options.timeout === this.toasts[id].timeout) {
          options.timeout++;
        }
        this.setToast(Object.assign({}, this.toasts[id], options));
      } else if (create) {
        this.addToast(Object.assign({}, { id }, options));
      }
    },
    getClasses(position) {
      const classes = [`${VT_NAMESPACE}__container`, position];
      return classes.concat(this.defaults.containerClassName);
    }
  }
});

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtToastContainer.vue?vue&type=template
const {renderList:_renderList,Fragment:_Fragment2,openBlock:_openBlock10,createElementBlock:_createElementBlock7,resolveComponent:_resolveComponent2,mergeProps:_mergeProps3,createBlock:_createBlock5,normalizeClass:_normalizeClass4,withCtx:_withCtx4,createVNode:_createVNode$1} = await importShared('vue');

function render10(_ctx, _cache) {
  const _component_Toast = _resolveComponent2("Toast");
  const _component_VtTransition = _resolveComponent2("VtTransition");
  return _openBlock10(), _createElementBlock7("div", null, [
    (_openBlock10(true), _createElementBlock7(_Fragment2, null, _renderList(_ctx.positions, (pos) => {
      return _openBlock10(), _createElementBlock7("div", { key: pos }, [
        _createVNode$1(_component_VtTransition, {
          transition: _ctx.defaults.transition,
          class: _normalizeClass4(_ctx.getClasses(pos))
        }, {
          default: _withCtx4(() => [
            (_openBlock10(true), _createElementBlock7(_Fragment2, null, _renderList(_ctx.getPositionToasts(pos), (toast) => {
              return _openBlock10(), _createBlock5(_component_Toast, _mergeProps3({
                key: toast.id
              }, toast), null, 16);
            }), 128))
          ]),
          _: 2
        }, 1032, ["transition", "class"])
      ]);
    }), 128))
  ]);
}

// vue:/Users/maronato/Developer/vue-toastification/src/components/VtToastContainer.vue
VtToastContainer_default.render = render10;
var VtToastContainer_default2 = VtToastContainer_default;

// src/ts/interface.ts
var buildInterface = (globalOptions = {}, mountContainer = true) => {
  const events = globalOptions.eventBus = globalOptions.eventBus || new EventBus();
  if (mountContainer) {
    nextTick(() => {
      const app = createApp(VtToastContainer_default2, __spreadValues({}, globalOptions));
      const component = app.mount(document.createElement("div"));
      const onMounted = globalOptions.onMounted;
      if (!isUndefined(onMounted)) {
        onMounted(component, app);
      }
      if (globalOptions.shareAppContext) {
        const baseApp = globalOptions.shareAppContext;
        if (baseApp === true) {
          console.warn(`[${VT_NAMESPACE}] App to share context with was not provided.`);
        } else {
          app._context.components = baseApp._context.components;
          app._context.directives = baseApp._context.directives;
          app._context.mixins = baseApp._context.mixins;
          app._context.provides = baseApp._context.provides;
          app.config.globalProperties = baseApp.config.globalProperties;
        }
      }
    });
  }
  const toast = (content, options) => {
    const props = Object.assign({}, { id: getId(), type: TYPE.DEFAULT }, options, {
      content
    });
    events.emit(EVENTS.ADD, props);
    return props.id;
  };
  toast.clear = () => events.emit(EVENTS.CLEAR, void 0);
  toast.updateDefaults = (update) => {
    events.emit(EVENTS.UPDATE_DEFAULTS, update);
  };
  toast.dismiss = (id) => {
    events.emit(EVENTS.DISMISS, id);
  };
  function updateToast(id, { content, options }, create = false) {
    const opt = Object.assign({}, options, { content });
    events.emit(EVENTS.UPDATE, {
      id,
      options: opt,
      create
    });
  }
  toast.update = updateToast;
  toast.success = (content, options) => toast(content, Object.assign({}, options, { type: TYPE.SUCCESS }));
  toast.info = (content, options) => toast(content, Object.assign({}, options, { type: TYPE.INFO }));
  toast.error = (content, options) => toast(content, Object.assign({}, options, { type: TYPE.ERROR }));
  toast.warning = (content, options) => toast(content, Object.assign({}, options, { type: TYPE.WARNING }));
  return toast;
};

// src/index.ts
var createMockToastInterface = () => {
  const toast = () => console.warn(`[${VT_NAMESPACE}] This plugin does not support SSR!`);
  return new Proxy(toast, {
    get() {
      return toast;
    }
  });
};
function createToastInterface(optionsOrEventBus) {
  if (!isBrowser()) {
    return createMockToastInterface();
  }
  if (isEventBusInterface(optionsOrEventBus)) {
    return buildInterface({ eventBus: optionsOrEventBus }, false);
  }
  return buildInterface(optionsOrEventBus, true);
}
var toastInjectionKey = Symbol("VueToastification");
var globalEventBus = new EventBus();
var useToast = (eventBus) => {
  const toast = getCurrentInstance() ? inject(toastInjectionKey, void 0) : void 0;
  return toast ? toast : createToastInterface(globalEventBus);
};

const _export_sfc = (sfc, props) => {
  const target = sfc.__vccOpts || sfc;
  for (const [key, val] of props) {
    target[key] = val;
  }
  return target;
};

const {createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,toDisplayString:_toDisplayString,createElementVNode:_createElementVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "history-container" };
const _hoisted_2 = { class: "d-flex flex-wrap align-center mb-4" };

const {ref,onMounted,computed} = await importShared('vue');

const _sfc_main = {
  __name: 'Page',
  props: {
  api: {
    type: Object,
    default: () => {},
  },
},
  emits: ['switch', 'close'],
  setup(__props, { emit: __emit }) {

const $toast = useToast();
// 接收API对象
const props = __props;

// 自定义事件，用于通知主应用刷新数据
const emit = __emit;

// Tabs
const activeTab = ref('history');

// 数据表格头部定义
const headers = [
  { title: '原始名称', key: 'original_name' },
  { title: '重命名后', key: 'after_name' },
  { title: '下载器', key: 'downloader' },
  { title: '状态', key: 'success' },
  { title: '处理时间', key: 'date' },
  { title: '操作', key: 'actions', sortable: false }
];

// 状态变量
const loading = ref(false);
const deleting = ref(false);
const historyRecords = ref([]);
const detailDialog = ref(false);
const deleteConfirmDialog = ref(false);
const currentRecord = ref({});
const selectedHistory = ref([]);

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
    const response = await props.api.get('plugin/RenameTorrentVue/rename_history');
    historyRecords.value = response || [];
  } catch (error) {
    console.error('获取历史记录失败:', error);
  } finally {
    loading.value = false;
  }
}

// 刷新所有数据
async function refreshAllData() {
  await refreshHistory();
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

// 删除选中的历史记录
function deleteSelectedHistory() {
  // 调试输出选中的记录
  if (selectedHistory.value && selectedHistory.value.length > 0) {
    deleteConfirmDialog.value = true;
  } else {
    $toast.warning('请先选择要删除的记录');
  }
}

// 确认删除历史记录
async function confirmDeleteHistory() {
  try {
    deleting.value = true;

    // 检查是否有要删除的记录
    if (!selectedHistory.value || selectedHistory.value.length === 0) {
      $toast.warning('没有选中的记录');
      deleting.value = false;
      return;
    }

    // 构造要发送的记录列表
    const recordsToSend = selectedHistory.value.map(hash => ({ hash: hash }));

    // 发送删除请求
    const response = await props.api.post('plugin/RenameTorrentVue/delete_rename_history', {
      records: recordsToSend
    });

    if (response?.success || response.data?.success) {
      // 清空选中项
      selectedHistory.value = [];

      // 关闭确认对话框
      deleteConfirmDialog.value = false;

      // 刷新历史记录
      await refreshHistory();

      // 显示成功消息
      const message = response.message || response.data?.message || '删除成功';
      $toast.success(`删除成功: ${message}`);
    } else {
      const message = response.message || response.data?.message || '未知错误';
      $toast.error(`删除失败: ${message}`);
    }
  } catch (error) {
    $toast('删除失败: ' + error);
  } finally {
    deleting.value = false;
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

// 组件挂载时刷新数据
onMounted(() => {
  refreshHistory();
});

return (_ctx, _cache) => {
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_card_item = _resolveComponent("v-card-item");
  const _component_v_tab = _resolveComponent("v-tab");
  const _component_v_tabs = _resolveComponent("v-tabs");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VSelect = _resolveComponent("VSelect");
  const _component_VTextField = _resolveComponent("VTextField");
  const _component_VSpacer = _resolveComponent("VSpacer");
  const _component_v_chip = _resolveComponent("v-chip");
  const _component_VDataTable = _resolveComponent("VDataTable");
  const _component_v_window_item = _resolveComponent("v-window-item");
  const _component_v_window = _resolveComponent("v-window");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_card_actions = _resolveComponent("v-card-actions");
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
          append: _withCtx(() => [
            _createVNode(_component_v_btn, {
              icon: "",
              color: "primary",
              variant: "text",
              onClick: notifyClose
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, null, {
                  default: _withCtx(() => [...(_cache[10] || (_cache[10] = [
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
              default: _withCtx(() => [...(_cache[9] || (_cache[9] = [
                _createTextVNode("重命名历史记录", -1)
              ]))]),
              _: 1
            })
          ]),
          _: 1
        }),
        _createVNode(_component_v_tabs, {
          modelValue: activeTab.value,
          "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((activeTab).value = $event)),
          color: "primary",
          "align-tabs": "center"
        }, {
          default: _withCtx(() => [
            _createVNode(_component_v_tab, { value: "history" }, {
              default: _withCtx(() => [...(_cache[11] || (_cache[11] = [
                _createTextVNode("历史记录", -1)
              ]))]),
              _: 1
            })
          ]),
          _: 1
        }, 8, ["modelValue"]),
        _createVNode(_component_v_card_text, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_window, {
              modelValue: activeTab.value,
              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((activeTab).value = $event))
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_window_item, { value: "history" }, {
                  default: _withCtx(() => [
                    _createElementVNode("div", _hoisted_2, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        onClick: refreshHistory,
                        loading: loading.value,
                        "prepend-icon": "mdi-refresh",
                        class: "mr-2 mb-2",
                        size: "small"
                      }, {
                        default: _withCtx(() => [...(_cache[12] || (_cache[12] = [
                          _createTextVNode(" 刷新记录 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"]),
                      _createVNode(_component_VBtn, {
                        color: "error",
                        onClick: deleteSelectedHistory,
                        disabled: selectedHistory.value.length === 0,
                        "prepend-icon": "mdi-delete",
                        class: "mr-2 mb-2",
                        size: "small"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(" 批量删除 (" + _toDisplayString(selectedHistory.value.length) + ") ", 1)
                        ]),
                        _: 1
                      }, 8, ["disabled"]),
                      _createVNode(_component_VSelect, {
                        modelValue: filterStatus.value,
                        "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((filterStatus).value = $event)),
                        items: statusOptions,
                        density: "compact",
                        "hide-details": "",
                        class: "mr-2 mb-2",
                        style: {"max-width":"120px"}
                      }, null, 8, ["modelValue"]),
                      _createVNode(_component_VTextField, {
                        modelValue: filterKeyword.value,
                        "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((filterKeyword).value = $event)),
                        placeholder: "搜索名称",
                        density: "compact",
                        "hide-details": "",
                        clearable: "",
                        class: "mr-2 mb-2",
                        style: {"max-width":"200px"}
                      }, null, 8, ["modelValue"]),
                      _createVNode(_component_VSpacer)
                    ]),
                    _createVNode(_component_VDataTable, {
                      modelValue: selectedHistory.value,
                      "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((selectedHistory).value = $event)),
                      headers: headers,
                      items: filteredHistoryRecords.value,
                      loading: loading.value,
                      class: "elevation-1",
                      "items-per-page": 10,
                      "items-per-page-options": [10, 20, 50, -1],
                      "show-select": "",
                      "item-value": "hash"
                    }, {
                      "item.success": _withCtx(({ item }) => [
                        _createVNode(_component_v_chip, {
                          color: item.success ? 'success' : 'error',
                          size: "small"
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
                          default: _withCtx(() => [...(_cache[13] || (_cache[13] = [
                            _createTextVNode(" 详情 ", -1)
                          ]))]),
                          _: 1
                        }, 8, ["onClick"])
                      ]),
                      _: 1
                    }, 8, ["modelValue", "items", "loading"])
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
              color: "primary",
              onClick: refreshAllData,
              loading: loading.value || _ctx.indexLoading
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, { start: "" }, {
                  default: _withCtx(() => [...(_cache[14] || (_cache[14] = [
                    _createTextVNode("mdi-refresh", -1)
                  ]))]),
                  _: 1
                }),
                _cache[15] || (_cache[15] = _createTextVNode(" 刷新数据 ", -1))
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
                  default: _withCtx(() => [...(_cache[16] || (_cache[16] = [
                    _createTextVNode("mdi-cog", -1)
                  ]))]),
                  _: 1
                }),
                _cache[17] || (_cache[17] = _createTextVNode(" 配置 ", -1))
              ]),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }),
    _createVNode(_component_VDialog, {
      modelValue: detailDialog.value,
      "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((detailDialog).value = $event)),
      "max-width": "600px"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_VCard, null, {
          default: _withCtx(() => [
            _createVNode(_component_VCardTitle, null, {
              default: _withCtx(() => [...(_cache[18] || (_cache[18] = [
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
                          default: _withCtx(() => [...(_cache[19] || (_cache[19] = [
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
                          default: _withCtx(() => [...(_cache[20] || (_cache[20] = [
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
                          default: _withCtx(() => [...(_cache[21] || (_cache[21] = [
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
                          default: _withCtx(() => [...(_cache[22] || (_cache[22] = [
                            _createTextVNode("状态:", -1)
                          ]))]),
                          _: 1
                        }),
                        _createVNode(_component_v_list_item_subtitle, null, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_chip, {
                              color: currentRecord.value.success ? 'success' : 'error',
                              size: "small"
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
                    (!currentRecord.value.success && currentRecord.value.reason)
                      ? (_openBlock(), _createBlock(_component_v_list_item, { key: 0 }, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_list_item_title, { class: "font-weight-bold" }, {
                              default: _withCtx(() => [...(_cache[23] || (_cache[23] = [
                                _createTextVNode("失败原因:", -1)
                              ]))]),
                              _: 1
                            }),
                            _createVNode(_component_v_list_item_subtitle, null, {
                              default: _withCtx(() => [
                                _createTextVNode(_toDisplayString(currentRecord.value.reason), 1)
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        }))
                      : _createCommentVNode("", true),
                    _createVNode(_component_v_list_item, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_list_item_title, { class: "font-weight-bold" }, {
                          default: _withCtx(() => [...(_cache[24] || (_cache[24] = [
                            _createTextVNode("下载器:", -1)
                          ]))]),
                          _: 1
                        }),
                        _createVNode(_component_v_list_item_subtitle, null, {
                          default: _withCtx(() => [
                            _createTextVNode(_toDisplayString(currentRecord.value.downloader), 1)
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_list_item, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_list_item_title, { class: "font-weight-bold" }, {
                          default: _withCtx(() => [...(_cache[25] || (_cache[25] = [
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
                  onClick: _cache[5] || (_cache[5] = $event => (detailDialog.value = false))
                }, {
                  default: _withCtx(() => [...(_cache[26] || (_cache[26] = [
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
    }, 8, ["modelValue"]),
    _createVNode(_component_VDialog, {
      modelValue: deleteConfirmDialog.value,
      "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((deleteConfirmDialog).value = $event)),
      "max-width": "400px"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_VCard, null, {
          default: _withCtx(() => [
            _createVNode(_component_VCardTitle, null, {
              default: _withCtx(() => [...(_cache[27] || (_cache[27] = [
                _createElementVNode("span", { class: "text-h5" }, "确认删除", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VCardText, null, {
              default: _withCtx(() => [
                _createTextVNode(" 确定要删除选中的 " + _toDisplayString(selectedHistory.value.length) + " 条历史记录吗？ ", 1)
              ]),
              _: 1
            }),
            _createVNode(_component_VCardActions, null, {
              default: _withCtx(() => [
                _createVNode(_component_VSpacer),
                _createVNode(_component_VBtn, {
                  color: "blue darken-1",
                  variant: "text",
                  onClick: _cache[7] || (_cache[7] = $event => (deleteConfirmDialog.value = false))
                }, {
                  default: _withCtx(() => [...(_cache[28] || (_cache[28] = [
                    _createTextVNode(" 取消 ", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_VBtn, {
                  color: "error",
                  onClick: confirmDeleteHistory,
                  loading: deleting.value
                }, {
                  default: _withCtx(() => [...(_cache[29] || (_cache[29] = [
                    _createTextVNode(" 确认删除 ", -1)
                  ]))]),
                  _: 1
                }, 8, ["loading"])
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
const PageComponent = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-e4c2e6d5"]]);

export { _export_sfc as _, PageComponent as default };
