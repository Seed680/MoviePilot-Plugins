# 站点自动签到插件 - Vue 版本

## 快速开始

### 1. 安装依赖

```bash
cd plugins.v2/autosignin
yarn install
```

### 2. 开发模式

```bash
yarn dev
```

访问 http://localhost:5002 查看效果

### 3. 构建生产版本

```bash
yarn build
```

构建后的文件将输出到 `dist` 目录

### 4. 部署到 MoviePilot

将整个 `autosignin` 文件夹复制到 MoviePilot 的插件目录，然后在 MoviePilot 中重新加载插件。

## 项目结构

```
autosignin/
├── src/
│   ├── components/
│   │   ├── Config.vue      # 配置页面组件
│   │   └── Page.vue        # 历史记录页面组件
│   ├── vuetify/
│   │   ├── defaults.ts     # Vuetify 默认配置
│   │   └── theme.ts        # Vuetify 主题配置
│   ├── App.vue             # 主应用组件
│   └── main.js             # 应用入口
├── dist/                   # 构建输出目录
├── index.html              # HTML 模板
├── package.json            # 项目配置
├── vite.config.js          # Vite 配置
└── __init__.py             # Python 插件主文件
```

## 技术栈

- **前端框架**: Vue 3 (Composition API)
- **UI 组件库**: Vuetify 3
- **构建工具**: Vite
- **模块联邦**: @originjs/vite-plugin-federation

## API 端点

插件提供以下 API 端点:

1. **GET /plugin/AutoSignIn/config** - 获取当前配置
2. **GET /plugin/AutoSignIn/history** - 获取签到和登录历史
3. **GET /plugin/AutoSignIn/signin_by_domain** - 手动触发站点签到

## 功能特性

- ✅ 自动签到指定站点
- ✅ 模拟登录指定站点
- ✅ 自定义执行周期
- ✅ 失败重试机制
- ✅ Cloudflare IP 自动优选
- ✅ 详细的签到/登录历史记录
- ✅ 美观的 Vue 界面

## 注意事项

⚠️ **重要提示**: 不是所有的站点都会把程序自动登录/签到定义为用户活跃（比如馒头），提示签到/登录成功仍然存在掉号风险！请结合站点公告说明自行把握。
