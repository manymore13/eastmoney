#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
东方财富研报 MCP 服务器
让大模型可以通过 MCP 协议调用研报查询和下载功能
"""

import json
import sys
import subprocess
from typing import Any, Dict, List

# MCP 协议常量
MCP_VERSION = "2024-11-05"


def run_command(cmd: List[str]) -> Dict[str, Any]:
    """执行命令行工具并返回结果"""
    try:
        # Windows 上可能使用 GBK/GB2312 编码
        result = subprocess.run(
            cmd,
            capture_output=True,
        )
        # 尝试多种编码
        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
            try:
                stdout = result.stdout.decode(encoding)
                stderr = result.stderr.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            stdout = result.stdout.decode('utf-8', errors='replace')
            stderr = result.stderr.decode('utf-8', errors='replace')
        
        return {
            "success": True,
            "stdout": stdout,
            "stderr": stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def handle_initialize(params: Dict[str, Any]) -> Dict[str, Any]:
    """处理 MCP 初始化请求"""
    return {
        "protocolVersion": MCP_VERSION,
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "eastmoney-reports",
            "version": "1.0.0"
        }
    }


def handle_list_tools(params: Dict[str, Any]) -> Dict[str, Any]:
    """列出可用工具"""
    tools = [
        {
            "name": "list_industries",
            "description": "列出所有可用的行业，用于查询研报前选择行业",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "可选，搜索关键词过滤行业"
                    }
                }
            }
        },
        {
            "name": "query_reports",
            "description": "查询研报列表，支持行业研报、个股研报、策略报告、宏观研究、券商晨报",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["industry", "stock", "strategy", "macro", "morning"],
                        "description": "研报类型"
                    },
                    "industry": {
                        "type": "string",
                        "description": "行业代码，如 1046=游戏行业"
                    },
                    "stock_code": {
                        "type": "string",
                        "description": "股票代码，如 600519=贵州茅台"
                    },
                    "page": {
                        "type": "integer",
                        "default": 1,
                        "description": "页码"
                    },
                    "pagesize": {
                        "type": "integer",
                        "default": 10,
                        "description": "每页数量"
                    },
                    "begin": {
                        "type": "string",
                        "description": "开始日期，格式 YYYY-MM-DD"
                    },
                    "end": {
                        "type": "string",
                        "description": "结束日期，格式 YYYY-MM-DD"
                    }
                }
            }
        },
        {
            "name": "download_reports",
            "description": "下载研报 PDF 文件到指定目录",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["industry", "stock", "strategy", "macro", "morning"],
                        "description": "研报类型"
                    },
                    "industry": {
                        "type": "string",
                        "description": "行业代码"
                    },
                    "stock_code": {
                        "type": "string",
                        "description": "股票代码"
                    },
                    "page": {
                        "type": "integer",
                        "default": 1,
                        "description": "下载第几页"
                    },
                    "pagesize": {
                        "type": "integer",
                        "default": 5,
                        "description": "每页数量"
                    },
                    "output": {
                        "type": "string",
                        "default": "./reports",
                        "description": "输出目录"
                    }
                }
            }
        }
    ]
    
    return {"tools": tools}


def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """处理工具调用请求"""
    
    if name == "list_industries":
        search = arguments.get("search", "")
        cmd = ["python", "-m", "eastmoney", "list"]
        if search:
            cmd.extend(["-s", search])
        result = run_command(cmd)
        return {"content": [{"type": "text", "text": result.get("stdout", result.get("error", ""))}]}
    
    elif name == "query_reports":
        cmd = ["python", "-m", "eastmoney", "query"]
        cmd.extend(["-t", arguments.get("type", "industry")])
        
        if arguments.get("industry"):
            cmd.extend(["-i", arguments["industry"]])
        if arguments.get("stock_code"):
            cmd.extend(["-c", arguments["stock_code"]])
        
        page = arguments.get("page", 1)
        pagesize = arguments.get("pagesize", 10)
        cmd.extend(["-p", str(page), "-s", str(pagesize)])
        
        if arguments.get("begin"):
            cmd.extend(["--begin", arguments["begin"]])
        if arguments.get("end"):
            cmd.extend(["--end", arguments["end"]])
        
        result = run_command(cmd)
        return {"content": [{"type": "text", "text": result.get("stdout", result.get("error", ""))}]}
    
    elif name == "download_reports":
        cmd = ["python", "-m", "eastmoney", "download"]
        cmd.extend(["-t", arguments.get("type", "industry")])
        
        if arguments.get("industry"):
            cmd.extend(["-i", arguments["industry"]])
        if arguments.get("stock_code"):
            cmd.extend(["-c", arguments["stock_code"]])
        
        page = arguments.get("page", 1)
        pagesize = arguments.get("pagesize", 5)
        cmd.extend(["-p", str(page), "-s", str(pagesize)])
        
        output = arguments.get("output", "./reports")
        cmd.extend(["-o", output])
        
        result = run_command(cmd)
        return {"content": [{"type": "text", "text": result.get("stdout", result.get("error", ""))}]}
    
    else:
        return {"content": [{"type": "text", "text": f"未知工具: {name}"}], "isError": True}


def main():
    """MCP 服务器主循环 - 使用 JSON-RPC over stdio"""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line.strip())
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "initialize":
                response = handle_initialize(params)
            elif method == "tools/list":
                response = handle_list_tools(params)
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                response = handle_call_tool(tool_name, arguments)
            else:
                response = {"error": f"Unknown method: {method}"}
            
            # 发送响应
            if request_id is not None:
                response["id"] = request_id
            print(json.dumps(response), flush=True)
            
        except Exception as e:
            error_response = {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            if 'request_id' in locals():
                error_response["id"] = request_id
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
