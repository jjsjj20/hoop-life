# 构建与验证（开发者向）

> 玩家不需要这一页——*线上版本已经是构建好的成品。*  
> 这里写给想改代码的人：怎么从源文件重建出线上版本，以及怎么确认自己没改坏。

## 一条命令重建

```bash
python3 tools/build_all.py
```

- 输入：`src/篮球人生-v4.8-原版.html`（未打补丁的原始游戏，重建的唯一输入）
- 输出：`dist/篮球人生.html` + `dist/assets/`（当前 105 张 webp）
- 脚本最后会**自动与仓库根的成品做哈希比对**——不一致说明构建或源文件有问题

依赖：

| 依赖               | 用途                | 缺失会怎样                |
| :--------------- | :---------------- | :------------------- |
| Python 3.10+     | 构建                | 无法构建                 |
| Pillow           | 图片按显示尺寸重采样（可选步骤） | 自动跳过该步并警告，产物体积会大一些 |
| Node ≥ 18（建议 20） | 跑测试（与构建无关）        | 无法跑验证                |

> **⚠️ Node 版本别乱升**：`jsdom` 已锁定 **26.1.0**（兼容 Node ≥ 18）。  
> 千万不要升到 jsdom 30——它带的 undici 8 需要 `node:worker_threads.markAsUncloneable`  
> （Node ≥ 22.10 才有），旧 Node 上 `require('jsdom')` 会直接抛  
> `webidl.util.markAsUncloneable is not a function`，10 个测试全部加载失败。  
> 依赖已用精确版本锁死（`package.json` 无 `^`，且 `package-lock.json` 已入库）。

### 排错：`webidl.util.markAsUncloneable is not a function`

这是 Node 过旧 + jsdom 版本过高导致的。两个解法，二选一：

1. 保持 `package.json` 里锁定的 `jsdom@26.1.0`，删掉 `node_modules` 重新 `npm install`；
2. 或者把本机 Node 升到 ≥ 22.10。

## 跑验证（改完代码必做）

```bash
python tools/test_build_contract.py  # 版本号与 SW 缓存边界
npm ci                 # 只装测试依赖（jsdom / acorn / acorn-walk）
node tools/verify_all.js
```

它会自动发现并依次跑当前全部 27 个 `test_*.js` 脚本，再加 AST 静态审查，汇总成一张表，**任何一项失败退出码非 0**。新增测试文件只要以 `test_` 开头就会自动纳入。
CI（`.github/workflows/verify.yml`）会先从原版源文件重建并校验根目录成品，再安装依赖跑同一套验证。

### 当前测试覆盖

| 脚本                       | 覆盖                                        |
| :----------------------- | :---------------------------------------- |
| 脚本类别 | 覆盖 |
| :-- | :-- |
| 核心流程（`test_smoke.js`、`test_season.js`、`test_playoffs.js`） | 建档、事件、赛季推进、结算、继续、存档往返、季后赛链路 |
| 选秀与交易（`test_draft_*`、`test_pick_*`、`test_team_str.js`） | 抽签概率、签位事件、交易保护、球队强度与页面数据 |
| 内容与数值（`test_balance.js`、`test_drama_quota.js`、`test_focus_league.js` 等） | 事件池可达性、成长/难度、联赛门槛与内容配额 |
| 存档与分享（`test_migration.js`、`test_join_str.js`、`test_share_card.js`、`test_pwa_card.js`） | 老存档迁移、分享卡、PWA manifest/SW/图标与离线守卫 |
| UI 与发布页面（`test_ui.js`、`test_func_return.js`、`test_changelog_page.js`） | 响应式界面、功能页返回、键盘操作、更新日志交互与历史完整性 |
| 静态审查（`audit.js`） | AST 重复声明、事件/效果注册、跳转目标、死配置和严重问题 |

### 加新测试

抄 `tools/test_pick_events.js` 的头尾，把断言写进 `check('描述', 条件, '出问题时的信息')`。  
文件名以 `test_` 开头就会被 `verify_all.js` 自动纳入——不用登记。

### 静态审查

```bash
node tools/audit.js
```

AST 级检查：顶层重复函数声明、状态对象多处构造的字段一致性、  
fx 键是否已注册、跳转目标是否存在、事件 id 唯一性、死配置、死代码、空数组取值。  
有严重问题会以非零退出码结束（CI 因此变红）。

## 构建管线

当前 `tools/build_all.py` 编排 51 个步骤：50 个必需步骤从 v4.8 原版逐项应用唯一匹配补丁，最后运行 `patch_sw_cache.py` 对齐最终 HTML 哈希；`optimize_images.py` 是可选的第 51 项图片优化步骤。每次构建都会生成 `dist/`，并把 `dist/篮球人生.html` 与仓库根成品做 SHA-256 前 16 位比对。

主要阶段包括：

1. 拆出 105 张图片资源并建立相对路径。
2. 依次应用玩法、内容、存档、分享卡和 PWA 补丁。
3. 应用桌面布局、移动端响应式和功能页返回等界面补丁。
4. 用最终 HTML 哈希生成版本化 Service Worker 缓存名。
5. 可选地按显示尺寸重采样图片；CI 使用 `--skip-optimize`，避免依赖 Pillow，同时仍验证完整补丁链和成品哈希。

每一步都要求**精确唯一匹配**才会改动——匹配不上就中止，绝不半途而废。

## ⚠️ 改这批脚本的两条铁律

1. **别用编辑器直接改 `篮球人生.html`**。内联图片会让某一行长达 1.4MB，  
   编辑器定位不可靠。所有改动都走补丁脚本，且用「唯一匹配断言」——匹配不上就整体失败。
2. **连续修改时每次都重新定位**。前面的替换会让后面的字符偏移失效；  
   拿旧偏移去切已改过的字符串，会把夹在中间的语句一起吞掉  
   （v4.9.1 之前就因此静默丢过 `ART_IMG.court` 别名，线上「球场」图变成矢量图）。

## 环境变量

| 变量                                    | 默认                     | 说明                                       |
| :------------------------------------ | :--------------------- | :--------------------------------------- |
| `GAME_SRC` / `GAME_OUT` / `GAME_HTML` | 见 `tools/build_all.py` | 让构建/测试脚本找到对应文件（本地调试用，CI 不需要）             |
| `TESTKIT_COLLECT=1`                   | —                      | `verify_all.js` 内部使用：让测试不自行退出，改由汇总脚本统一退出 |

## 常见问题

**Q：重建出来的文件和仓库根的成品不一致？**  
先确认 `--src` 指向的是未打补丁的 v4.8 原版（`src/篮球人生-v4.8-原版.html`），  
再确认 50 个必需步骤全部成功；若本地跳过可选图片优化，使用与 CI 相同的 `--skip-optimize` 参数，避免把优化步骤的体积差异误判为代码问题。

**Q：测试报「未注册的效果键」？**  
`applyFx` 对未知键只 `console.warn` 不报错。往 `FX` 注册表里补上，  
或者修正事件里的 `fx:{...}` 拼写——写错一个键就等于这个选项没有任何效果。

**Q：想加新事件？**  
抄 `tools/build/patch_pick_events.py` 里 `pk*` 的写法：  
`evt(id, 标题, 场景函数, [ch(...)])`，挂 `isPro()` 之类的门槛，  
标题里带上题材关键词（会被自动归类），然后把它加进 `EV_KIND_OVERRIDE` 与对应季节的池子。  
加完跑 `verify_all`——其中有一条断言专门验证「新事件真的抽得到」。
