# 表情包 MCP 服务器

一个功能强大的 MCP (Model Context Protocol) 服务器，用于管理、搜索和分发本地表情包。

## 功能特性

- 📋 **智能列表** - 快速获取所有可用表情包的名称。
- 🔍 **模糊搜索** - 支持关键词匹配、模糊匹配及相似名称推荐，找不到精确匹配时也会给出建议。
- 🌐 **即时访问** - 自动将本地图片转为 HTTP URL，支持在聊天软件（如 Cherry Studio）中直接预览。
- ➕ **一键添加** - 支持通过 **本地路径** 或 **网络 URL** 直接添加表情包，自动下载、重命名并归档。
- 🗑️ **便捷删除** - 支持一键从索引和磁盘中永久删除不再需要的表情包。
- 🔄 **全自动管理** - 自动启动和管理后台静态资源服务器，无需人工干预。

![演示](./image/哈哈2.png)

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备工作

创建一个 `memes` 目录。你可以直接把图片丢进去，也可以通过工具动态添加。

目录结构：
```
meme-mcp/
├── meme_server.py
├── requirements.txt
├── README.md
└── memes/          # 表情包存放地
    └── index.json  # 索引文件（自动维护）
```

### 3. 配置 MCP 客户端

在你的 MCP 客户端（如 Claude Desktop, Cherry Studio）中添加配置：

**Windows 示例 (Claude Desktop):**
编辑 `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "meme-server": {
      "command": "python",
      "args": [
        "E:\\你的路径\\meme-mcp\\meme_server.py"
      ]
    }
  }
}
```

## 使用方法

### 1. 查找与搜索
- **列出所有**: `帮我看看有哪些表情包`
- **模糊搜索**: `搜一下关于“开心”的表情` (即使名称不完全匹配也会给出推荐)

### 2. 添加表情包 (强大的一键添加)
- **从网络添加**: `把这个图片存为表情包：https://example.com/smile.gif` (自动下载并命名)
- **从本地添加**: `添加本地图片 C:\Users\Pics\funny.png，命名为“好笑”`
- **自动处理**: 如果你起名带了后缀（如 `哈哈.jpg`），系统会自动处理，不会出现 `哈哈.jpg.jpg` 的尴尬情况。

### 3. 删除表情包
- `删除名为“测试”的表情包` (同时删除文件和记录)

## 工具说明

### `list_memes`
获取所有表情包名称列表。

### `get_meme`
根据名称获取表情包的 HTTP URL。
- 参数: `name` (表情包名称)

### `search_memes`
搜索表情包。
- 参数: `keyword` (关键词)
- 特色: 支持模糊匹配和相似度推荐。

### `add_meme`
添加新表情包。
- 参数: 
    - `source` (必填): 本地路径或 URL。
    - `name` (可选): 表情包名称，建议不带后缀。
- 特色: 自动下载、自动识别格式、智能防重复后缀。

### `delete_meme`
删除表情包。
- 参数: `name` (表情包名称)
- 效果: 同步删除磁盘文件和索引记录。

### `check_server`
检查图片服务器状态。

## 常见问题 (FAQ)

### 为什么图片不显示？
1. 检查 `check_server` 状态是否为“运行中”。
2. 确保 8000 端口未被占用（可在 `meme_server.py` 修改 `STATIC_SERVER_PORT`）。
3. 确保你的聊天软件支持显示 Markdown 图片。

### 如何批量导入？
直接将图片放入 `memes` 文件夹，然后调用一次 `list_memes`，服务器会自动扫描新文件并生成索引。

## 许可证

MIT License
