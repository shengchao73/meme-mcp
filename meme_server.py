#!/usr/bin/env python3
"""
表情包 MCP 服务器
提供表情包列表查询和图片路径获取功能
"""

import os
import json
import asyncio
import socket
import threading
from pathlib import Path
from typing import Any
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import http.server
import socketserver

# 表情包存储目录
MEMES_DIR = Path(__file__).parent / "memes"

# 静态资源服务器配置
STATIC_SERVER_HOST = "localhost"
STATIC_SERVER_PORT = 8000

# 全局变量
static_server_thread = None
static_server_running = False

# 创建服务器实例
server = Server("meme-server")


def load_meme_index() -> dict[str, str]:
    """
    加载表情包索引
    返回 {名称: 文件名} 的字典
    """
    index_file = MEMES_DIR / "index.json"

    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    # 如果没有索引文件，自动扫描目录
    meme_index = {}
    if MEMES_DIR.exists():
        for file in MEMES_DIR.iterdir():
            if file.is_file() and file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                # 使用文件名（不含扩展名）作为默认名称
                name = file.stem
                meme_index[name] = file.name

    return meme_index


def save_meme_index(index: dict[str, str]):
    """保存表情包索引到文件"""
    index_file = MEMES_DIR / "index.json"
    MEMES_DIR.mkdir(parents=True, exist_ok=True)

    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def is_port_in_use(port: int) -> bool:
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except OSError:
            return True


class MemeHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定义 HTTP 请求处理器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(MEMES_DIR), **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def log_message(self, format, *args):
        pass


def start_static_server():
    """启动静态资源服务器"""
    global static_server_running
    
    if not MEMES_DIR.exists():
        MEMES_DIR.mkdir(parents=True, exist_ok=True)
    
    os.chdir(MEMES_DIR)
    
    with socketserver.TCPServer((STATIC_SERVER_HOST, STATIC_SERVER_PORT), MemeHTTPRequestHandler) as httpd:
        static_server_running = True
        httpd.serve_forever()


def ensure_static_server():
    """确保静态资源服务器正在运行"""
    global static_server_thread, static_server_running
    
    if static_server_running and is_port_in_use(STATIC_SERVER_PORT):
        return True
    
    if is_port_in_use(STATIC_SERVER_PORT):
        return True
    
    if static_server_thread is None or not static_server_thread.is_alive():
        static_server_thread = threading.Thread(target=start_static_server, daemon=True)
        static_server_thread.start()
        
        import time
        time.sleep(0.5)
    
    return is_port_in_use(STATIC_SERVER_PORT)


def get_server_status() -> dict:
    """获取静态资源服务器状态"""
    port_in_use = is_port_in_use(STATIC_SERVER_PORT)
    
    return {
        "running": port_in_use,
        "host": STATIC_SERVER_HOST,
        "port": STATIC_SERVER_PORT,
        "url": f"http://{STATIC_SERVER_HOST}:{STATIC_SERVER_PORT}"
    }


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """列出所有可用的工具"""
    return [
        types.Tool(
            name="list_memes",
            description="获取所有可用表情包的名称列表",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        types.Tool(
            name="get_meme",
            description="根据名称获取表情包的 HTTP URL（会自动启动静态资源服务器）",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "表情包的名称"
                    }
                },
                "required": ["name"]
            },
        ),
        types.Tool(
            name="add_meme",
            description="添加新的表情包到索引（需要先将图片文件放到memes目录）",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "表情包的名称（用于查询）"
                    },
                    "filename": {
                        "type": "string",
                        "description": "图片文件名（包含扩展名）"
                    }
                },
                "required": ["name", "filename"]
            },
        ),
        types.Tool(
            name="search_memes",
            description="根据关键词搜索表情包",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词"
                    }
                },
                "required": ["keyword"]
            },
        ),
        types.Tool(
            name="check_server",
            description="检查静态资源服务器的运行状态",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """处理工具调用"""

    if name == "list_memes":
        # 获取所有表情包列表
        meme_index = load_meme_index()

        if not meme_index:
            return [types.TextContent(
                type="text",
                text="暂无表情包。请将图片文件放到 memes 目录中。"
            )]

        meme_list = "\n".join([f"- {name}" for name in sorted(meme_index.keys())])
        return [types.TextContent(
            type="text",
            text=f"可用的表情包列表（共 {len(meme_index)} 个）：\n\n{meme_list}\n\n##提示：所有表情包都在统一路径，如: http://localhost:8000/点头.gif ；替换文件名【点头.gif】,使用markdown格式即可直接引用，不用再查询地址。##"
        )]

    elif name == "get_meme":
        # 获取指定表情包的路径
        if not arguments or "name" not in arguments:
            raise ValueError("缺少参数: name")

        meme_name = arguments["name"]
        meme_index = load_meme_index()

        if meme_name not in meme_index:
            return [types.TextContent(
                type="text",
                text=f"未找到名为 '{meme_name}' 的表情包。\n\n##提示：所有表情包都在统一路径，如: http://localhost:8000/点头.gif ；替换文件名【点头.gif】,使用markdown格式即可直接引用，不用再查询地址。##\n\n可用的表情包：{', '.join(sorted(meme_index.keys()))}"
            )]

        filename = meme_index[meme_name]
        file_path = MEMES_DIR / filename

        if not file_path.exists():
            return [types.TextContent(
                type="text",
                text=f"表情包文件不存在: {file_path}"
            )]

        # 确保静态资源服务器正在运行
        ensure_static_server()

        # 返回 HTTP URL 而不是本地文件路径
        meme_url = f"http://{STATIC_SERVER_HOST}:{STATIC_SERVER_PORT}/{filename}"
        return [types.TextContent(
            type="text",
            text=f"表情包路径: {meme_url}"
        )]

    elif name == "add_meme":
        # 添加新表情包到索引
        if not arguments or "name" not in arguments or "filename" not in arguments:
            raise ValueError("缺少参数: name 和 filename")

        meme_name = arguments["name"]
        filename = arguments["filename"]

        # 检查文件是否存在
        file_path = MEMES_DIR / filename
        if not file_path.exists():
            return [types.TextContent(
                type="text",
                text=f"错误：文件 '{filename}' 不存在于 memes 目录中。\n请先将图片文件复制到: {MEMES_DIR.absolute()}"
            )]

        # 更新索引
        meme_index = load_meme_index()
        meme_index[meme_name] = filename
        save_meme_index(meme_index)

        return [types.TextContent(
            type="text",
            text=f"成功添加表情包: {meme_name} -> {filename}\n\n访问地址: http://{STATIC_SERVER_HOST}:{STATIC_SERVER_PORT}/{filename}"
        )]

    elif name == "search_memes":
        # 搜索表情包
        if not arguments or "keyword" not in arguments:
            raise ValueError("缺少参数: keyword")

        keyword = arguments["keyword"].lower()
        meme_index = load_meme_index()

        # 搜索名称中包含关键词的表情包
        results = [name for name in meme_index.keys() if keyword in name.lower()]

        if not results:
            return [types.TextContent(
                type="text",
                text=f"未找到包含 '{keyword}' 的表情包。"
            )]

        result_list = "\n".join([f"- {name}" for name in sorted(results)])
        return [types.TextContent(
            type="text",
            text=f"搜索结果（共 {len(results)} 个）：\n\n{result_list}"
        )]

    elif name == "check_server":
        # 检查静态资源服务器状态
        status = get_server_status()
        
        status_text = f"静态资源服务器状态：\n"
        status_text += f"- 运行状态: {'✓ 运行中' if status['running'] else '✗ 未运行'}\n"
        status_text += f"- 访问地址: {status['url']}\n"
        status_text += f"- 监听端口: {status['port']}\n"
        
        if not status['running']:
            status_text += f"\n提示：服务器未运行，将在下次获取表情包时自动启动。"
        
        return [types.TextContent(
            type="text",
            text=status_text
        )]

    else:
        raise ValueError(f"未知工具: {name}")


async def main():
    """运行服务器"""
    # 确保 memes 目录存在
    MEMES_DIR.mkdir(parents=True, exist_ok=True)
    
    # 自动启动静态资源服务器
    ensure_static_server()

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="meme-server",
                server_version="0.2.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
