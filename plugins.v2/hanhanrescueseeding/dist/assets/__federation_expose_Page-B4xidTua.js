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
var _hoisted_3$1 = [
  _hoisted_2$1
];
function render3(_ctx, _cache) {
  return _openBlock3(), _createElementBlock2("svg", _hoisted_12, _hoisted_3$1);
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

const {toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,withKeys:_withKeys,createElementVNode:_createElementVNode,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "plugin-page" };
const _hoisted_2 = { key: 2 };
const _hoisted_3 = { class: "mt-4" };
const _hoisted_4 = { class: "d-flex align-center justify-space-between mb-2" };
const _hoisted_5 = {
  key: 0,
  class: "text-success"
};
const _hoisted_6 = {
  key: 1,
  class: "text-grey"
};
const _hoisted_7 = { key: 0 };
const _hoisted_8 = { key: 1 };

const {ref,onMounted,computed} = await importShared('vue');

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

const $toast = useToast();
// 接收初始配置
const props = __props;

// 组件状态
const title = ref('憨憨保种区');
const loading = ref(true);
const deleting = ref(false);
const error = ref(null);
const downloadRecords = ref([]);
const searchTitle = ref('');
const minSeeders = ref('');
const maxSeeders = ref('');
const selectedRecords = ref([]);
const deleteDialog = ref(false);

// 过滤后的记录
const filteredRecords = computed(() => {
  let records = [...downloadRecords.value];
  
  // 按标题搜索
  if (searchTitle.value) {
    const searchLower = searchTitle.value.toLowerCase();
    records = records.filter(record => 
      (record.title && record.title.toLowerCase().includes(searchLower)) ||
      (record.zh_title && record.zh_title.toLowerCase().includes(searchLower))
    );
  }
  
  // 按做种人数筛选
  if (minSeeders.value !== '') {
    const min = parseInt(minSeeders.value);
    if (!isNaN(min)) {
      records = records.filter(record => {
        const seeders = parseInt(record.seeders);
        return !isNaN(seeders) && seeders >= min
      });
    }
  }
  
  if (maxSeeders.value !== '') {
    const max = parseInt(maxSeeders.value);
    if (!isNaN(max)) {
      records = records.filter(record => {
        const seeders = parseInt(record.seeders);
        return !isNaN(seeders) && seeders <= max
      });
    }
  }
  
  return records
});



const downloadHeaders = ref([
  { title: '英文标题', key: 'title' },
  { title: '中文标题', key: 'zh_title' },
  { title: '种子大小', key: 'size' },
  { title: '做种人数', key: 'seeders' },
  { title: '种子Hash', key: 'torrent_hash' },
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
    error.value = '获取下载记录失败:'+ err.message || '获取下载记录失败';
    $toast.error(error.value);
    downloadRecords.value = [];
  } finally {
    loading.value = false;
    // 通知主应用组件已更新
    emit('action');
  }
}

// 过滤记录
function filterRecords() {
  // 通过computed属性自动过滤，无需额外操作
}



// 删除选中记录
function confirmDeleteSelected() {
  deleteDialog.value = true;
}

// 确认删除
async function deleteConfirmed() {
  deleting.value = true;
  try {
    // 删除选中记录
    await deleteMultipleRecords(selectedRecords.value);
    selectedRecords.value = [];
    
    // 重新加载数据
    await refreshData();
  } catch (err) {
    console.error('删除记录失败:', err);
    error.value = '删除记录失败: ' + err.message;
    $toast.error(error.value);
  } finally {
    deleteDialog.value = false;
    deleting.value = false;
  }
}

// 批量删除记录
async function deleteMultipleRecords(recordTitles) {
  // 根据标题从downloadRecords中获取完整的记录对象
  const records = recordTitles.map(title => 
    downloadRecords.value.find(record => record.title === title)
  ).filter(record => record !== undefined); // 过滤掉未找到的记录
  
  // 分离有hash和无hash的记录
  const recordsWithHash = records.filter(record => record && record.torrent_hash);
  // const recordsWithoutHash = records.filter(record => record && !record.torrent_hash)
  
  // 如果有包含hash的记录，先批量删除种子
  if (recordsWithHash.length > 0) {
    const hashes = recordsWithHash.map(record => record.torrent_hash);
    try {
      const response = await props.api.post(`plugin/HanHanRescueSeeding/delete_torrents`, hashes);
      if (!response.success) {
        console.error('删除种子失败:', response.message);
        $toast.error('删除种子失败:' + response.message);
        // 即使部分失败，也继续删除记录
      } else {
        $toast.success('下载删除种子成功');
      }
    } catch (err) {
      console.error('删除种子API调用失败:', err);
      $toast.error('删除种子API调用失败:' + err.message);
      // 即使API调用失败，也要继续删除记录
    }
  }
  
  // 删除所有选中的记录
  const titles = records.map(record => record.title);
  
  // 同时调用后端API删除数据库中的记录
  try {
    const response = await props.api.post(`plugin/HanHanRescueSeeding/delete_download_records`, titles);
    if (!response.success) {
      console.error('删除下载记录失败:', response.message);
      $toast.error('删除下载记录失败:' + response.message);
    } else {
      $toast.success('删除下载记录成功');
    }
  } catch (err) {
    console.error('删除下载记录API调用失败:', err);
    $toast('删除下载记录API调用失败:' + err.message);
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
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_data_table = _resolveComponent("v-data-table");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_card_actions = _resolveComponent("v-card-actions");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_progress_circular = _resolveComponent("v-progress-circular");
  const _component_v_dialog = _resolveComponent("v-dialog");

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
                        md: "4"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_text_field, {
                            modelValue: searchTitle.value,
                            "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((searchTitle).value = $event)),
                            label: "搜索标题",
                            placeholder: "输入标题关键词",
                            clearable: "",
                            density: "compact",
                            variant: "outlined",
                            "hide-details": "",
                            onKeyup: _withKeys(filterRecords, ["enter"])
                          }, {
                            "prepend-inner": _withCtx(() => [
                              _createVNode(_component_v_icon, null, {
                                default: _withCtx(() => _cache[7] || (_cache[7] = [
                                  _createTextVNode("mdi-magnify", -1)
                                ])),
                                _: 1,
                                __: [7]
                              })
                            ]),
                            _: 1
                          }, 8, ["modelValue"])
                        ]),
                        _: 1
                      }),
                      _createVNode(_component_v_col, {
                        cols: "12",
                        md: "3"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_text_field, {
                            modelValue: minSeeders.value,
                            "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((minSeeders).value = $event)),
                            label: "最小做种人数",
                            type: "number",
                            density: "compact",
                            variant: "outlined",
                            "hide-details": "",
                            onKeyup: _withKeys(filterRecords, ["enter"])
                          }, null, 8, ["modelValue"])
                        ]),
                        _: 1
                      }),
                      _createVNode(_component_v_col, {
                        cols: "12",
                        md: "3"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_text_field, {
                            modelValue: maxSeeders.value,
                            "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((maxSeeders).value = $event)),
                            label: "最大做种人数",
                            type: "number",
                            density: "compact",
                            variant: "outlined",
                            "hide-details": "",
                            onKeyup: _withKeys(filterRecords, ["enter"])
                          }, null, 8, ["modelValue"])
                        ]),
                        _: 1
                      }),
                      _createVNode(_component_v_col, {
                        cols: "12",
                        md: "2"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_btn, {
                            color: "primary",
                            onClick: filterRecords,
                            block: "",
                            disabled: !searchTitle.value && !minSeeders.value && !maxSeeders.value
                          }, {
                            default: _withCtx(() => [
                              _createVNode(_component_v_icon, { start: "" }, {
                                default: _withCtx(() => _cache[8] || (_cache[8] = [
                                  _createTextVNode("mdi-filter", -1)
                                ])),
                                _: 1,
                                __: [8]
                              }),
                              _cache[9] || (_cache[9] = _createTextVNode(" 筛选 ", -1))
                            ]),
                            _: 1,
                            __: [9]
                          }, 8, ["disabled"])
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  }),
                  _createElementVNode("div", _hoisted_3, [
                    _createElementVNode("div", _hoisted_4, [
                      _cache[11] || (_cache[11] = _createElementVNode("div", { class: "text-h6" }, "下载记录", -1)),
                      (selectedRecords.value.length > 0)
                        ? (_openBlock(), _createBlock(_component_v_btn, {
                            key: 0,
                            color: "error",
                            onClick: confirmDeleteSelected,
                            disabled: selectedRecords.value.length === 0
                          }, {
                            default: _withCtx(() => [
                              _createVNode(_component_v_icon, { start: "" }, {
                                default: _withCtx(() => _cache[10] || (_cache[10] = [
                                  _createTextVNode("mdi-delete", -1)
                                ])),
                                _: 1,
                                __: [10]
                              }),
                              _createTextVNode(" 删除选中 (" + _toDisplayString(selectedRecords.value.length) + ") ", 1)
                            ]),
                            _: 1
                          }, 8, ["disabled"]))
                        : _createCommentVNode("", true)
                    ]),
                    (filteredRecords.value && filteredRecords.value.length > 0)
                      ? (_openBlock(), _createBlock(_component_v_data_table, {
                          key: 0,
                          headers: downloadHeaders.value,
                          items: filteredRecords.value,
                          "items-per-page": 10,
                          "footer-props": {
                'items-per-page-options': [5, 10, 20, -1]
              },
                          "item-value": "title",
                          "show-select": "",
                          modelValue: selectedRecords.value,
                          "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((selectedRecords).value = $event)),
                          class: "elevation-1"
                        }, {
                          "item.download_time": _withCtx(({ item }) => [
                            _createTextVNode(_toDisplayString(formatTime(item.download_time)), 1)
                          ]),
                          "item.torrent_hash": _withCtx(({ item }) => [
                            (item.torrent_hash)
                              ? (_openBlock(), _createElementBlock("span", _hoisted_5, _toDisplayString(item.torrent_hash.substring(0, 8)) + "...", 1))
                              : (_openBlock(), _createElementBlock("span", _hoisted_6, "-"))
                          ]),
                          _: 1
                        }, 8, ["headers", "items", "modelValue"]))
                      : (_openBlock(), _createBlock(_component_v_alert, {
                          key: 1,
                          type: "info",
                          class: "mt-4"
                        }, {
                          default: _withCtx(() => _cache[12] || (_cache[12] = [
                            _createTextVNode(" 暂无下载记录 ", -1)
                          ])),
                          _: 1,
                          __: [12]
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
                  default: _withCtx(() => _cache[13] || (_cache[13] = [
                    _createTextVNode("mdi-refresh", -1)
                  ])),
                  _: 1,
                  __: [13]
                }),
                _cache[14] || (_cache[14] = _createTextVNode(" 刷新数据 ", -1))
              ]),
              _: 1,
              __: [14]
            }, 8, ["loading"]),
            _createVNode(_component_v_spacer),
            _createVNode(_component_v_btn, {
              color: "primary",
              onClick: notifySwitch
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, { start: "" }, {
                  default: _withCtx(() => _cache[15] || (_cache[15] = [
                    _createTextVNode("mdi-cog", -1)
                  ])),
                  _: 1,
                  __: [15]
                }),
                _cache[16] || (_cache[16] = _createTextVNode(" 配置 ", -1))
              ]),
              _: 1,
              __: [16]
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }),
    _createVNode(_component_v_dialog, {
      modelValue: deleteDialog.value,
      "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((deleteDialog).value = $event)),
      "max-width": "500"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, null, {
              default: _withCtx(() => _cache[17] || (_cache[17] = [
                _createTextVNode("确认删除", -1)
              ])),
              _: 1,
              __: [17]
            }),
            _createVNode(_component_v_card_text, null, {
              default: _withCtx(() => [
                (selectedRecords.value.length > 0)
                  ? (_openBlock(), _createElementBlock("p", _hoisted_7, " 确定要删除 " + _toDisplayString(selectedRecords.value.length) + " 条记录吗？ 包含种子hash的记录将同时删除下载器中的种子。 ", 1))
                  : _createCommentVNode("", true)
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, null, {
              default: _withCtx(() => [
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  onClick: _cache[4] || (_cache[4] = $event => (deleteDialog.value = false))
                }, {
                  default: _withCtx(() => _cache[18] || (_cache[18] = [
                    _createTextVNode("取消", -1)
                  ])),
                  _: 1,
                  __: [18]
                }),
                _createVNode(_component_v_btn, {
                  color: "error",
                  onClick: deleteConfirmed,
                  loading: deleting.value
                }, {
                  default: _withCtx(() => [
                    (deleting.value)
                      ? (_openBlock(), _createBlock(_component_v_progress_circular, {
                          key: 0,
                          size: "20",
                          width: "2",
                          indeterminate: ""
                        }))
                      : (_openBlock(), _createElementBlock("span", _hoisted_8, "确认删除"))
                  ]),
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

export { _sfc_main as default };
