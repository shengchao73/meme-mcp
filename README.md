# 表情包 MCP 服务器

一个简单的 MCP (Model Context Protocol) 服务器，用于管理和检索本地表情包图片。

## 功能特性

- 📋 **列出所有表情包** - 获取所有可用表情包的名称列表
- 🔍 **搜索表情包** - 根据关键词搜索表情包
- 🌐 **获取图片 URL** - 根据名称获取表情包的 HTTP URL（支持在聊天软件中显示）
- ➕ **添加表情包** - 将新图片添加到表情包索引
- 🔄 **自动启动服务器** - 自动启动和管理静态资源服务器，无需手动操作
- 📊 **服务器状态检查** - 随时查看静态资源服务器的运行状态

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备表情包

将你的表情包图片（支持 .jpg, .png, .gif, .webp 格式）放到 `memes` 目录中。

目录结构示例：
```
meme-mcp/
├── meme_server.py
├── requirements.txt
├── README.md
└── memes/
    ├── 笑哭.png
    ├── 点赞.gif
    ├── 疑问.jpg
    └── index.json  # 自动生成
```

### 3. 配置 MCP 客户端

在你的 MCP 客户端配置文件中添加：

**对于 Claude Desktop (Windows):**

编辑 `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "meme-server": {
      "command": "python",
      "args": [
        "E:\\CherryStudioDaTa\\Agent\\论文\\meme-mcp\\meme_server.py"
      ]
    }
  }
}
```

**对于 Claude Desktop (macOS/Linux):**

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "meme-server": {
      "command": "python3",
      "args": [
        "/path/to/meme-mcp/meme_server.py"
      ]
    }
  }
}
```

## 使用方法

### 1. 列出所有表情包

```
请列出所有可用的表情包
```

### 2. 搜索表情包

```
搜索包含"笑"的表情包
```

### 3. 获取表情包 URL

```
获取"笑哭"表情包的 URL
```

返回示例：
```
表情包路径: http://localhost:8000/laugh_cry.png
```

**注意：** 静态资源服务器会在首次调用 `get_meme` 时自动启动，无需手动操作。

### 4. 检查服务器状态

```
检查静态资源服务器状态
```

返回示例：
```
静态资源服务器状态：
- 运行状态: ✓ 运行中
- 访问地址: http://localhost:8000
- 监听端口: 8000
```

### 5. 添加新表情包

首先将图片文件复制到 `memes` 目录，然后：

```
添加表情包：名称为"新表情"，文件名为"new_meme.png"
```

## 工具说明

### list_memes
获取所有可用表情包的名称列表。

**参数：** 无

**返回：** 表情包名称列表

### get_meme
根据名称获取表情包的 HTTP URL（会自动启动静态资源服务器）。

**参数：**
- `name` (string): 表情包的名称

**返回：** 表情包的 HTTP URL（格式：http://localhost:8000/文件名）

**说明：** 首次调用时会自动启动静态资源服务器，无需手动操作。

### search_memes
根据关键词搜索表情包。

**参数：**
- `keyword` (string): 搜索关键词

**返回：** 匹配的表情包列表

### add_meme
添加新的表情包到索引。

**参数：**
- `name` (string): 表情包的名称（用于查询）
- `filename` (string): 图片文件名（包含扩展名）

**返回：** 添加结果

### check_server
检查静态资源服务器的运行状态。

**参数：** 无

**返回：** 服务器状态信息（运行状态、访问地址、监听端口）

## 索引文件

服务器会自动在 `memes` 目录下创建 `index.json` 文件来管理表情包索引：

```json
{
  "笑哭": "laugh_cry.png",
  "点赞": "thumbs_up.gif",
  "疑问": "question.jpg"
}
```

你可以手动编辑这个文件来自定义表情包的名称。

## 为什么需要静态资源服务器？

由于浏览器的安全限制（Security Sandboxing 和同源策略），基于 Electron 或浏览器内核的聊天软件（如 Cherry Studio）无法直接访问本地文件系统（如 `E:\...\发呆.jpg`）。

为了解决这个问题，我们搭建了一个本地静态资源服务器，将本地文件路径转换为 HTTP URL（如 `http://localhost:8000/发呆.jpg`），这样聊天软件就能正常加载和显示表情包了。

**好消息：** 静态资源服务器现在会自动启动和管理，无需手动操作！

## 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

## 故障排除

### 表情包无法显示

1. **检查服务器状态**
   - 使用 `check_server` 工具查看静态资源服务器是否正在运行
   - 如果未运行，调用 `get_meme` 工具时会自动启动

2. **确认服务器端口未被占用**
   - 如果 8000 端口被其他程序占用，可以修改 `meme_server.py` 中的 `STATIC_SERVER_PORT` 配置
   - 修改后需要重启 MCP 服务器

3. **确认表情包文件存在**
   - 检查 `memes` 目录中是否有对应的图片文件
   - 使用 `list_memes` 工具查看所有可用的表情包

4. **测试服务器访问**
   - 在浏览器中访问 `http://localhost:8000` 测试是否能访问
   - 如果能访问，说明服务器运行正常

### 表情包列表为空

1. 确认 `memes` 目录中有图片文件
2. 检查图片格式是否支持
3. 尝试手动创建 `index.json` 文件

### 无法找到表情包

1. 使用 `list_memes` 查看所有可用的表情包名称
2. 确保名称完全匹配（区分大小写）
3. 检查 `index.json` 中的映射关系

### 文件路径错误

确保在配置文件中使用了正确的绝对路径，Windows 系统注意使用双反斜杠 `\\` 或正斜杠 `/`。

## 许可证

MIT License
