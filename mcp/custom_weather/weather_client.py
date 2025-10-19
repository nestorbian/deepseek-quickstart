# weather_client.py
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import mcp.types as types
from typing import List, Any

class WeatherClient:
    """天气 MCP 服务器客户端"""
    
    def __init__(self, server_script_path: str = "weather.py"):
        """
        初始化客户端
        
        Args:
            server_script_path: 天气服务器脚本路径
        """
        self.server_script_path = server_script_path
        self.session = None
        self.stdio_context = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
        
    async def connect(self):
        """连接到天气 MCP 服务器"""
        try:
            # 配置服务器参数，通过 stdio 传输
            server_params = StdioServerParameters(
                command="python",
                args=[self.server_script_path]
            )
            
            # 创建 stdio 客户端并连接到服务器
            self.stdio_context = stdio_client(server_params)
            stdio_transport = await self.stdio_context.__aenter__()
            read, write = stdio_transport
            
            # 创建客户端会话
            session_context = ClientSession(read, write)
            self.session = await session_context.__aenter__()
            
            # 初始化会话
            initialization_result = await self.session.initialize()
            print(f"✅ 服务器初始化成功: {initialization_result}")
            
            # 获取可用工具列表
            tools_result = await self.session.list_tools()
            print(f"🛠️  可用工具: {[tool.name for tool in tools_result.tools]}")
            
            return self
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            await self.close()
            raise
    
    async def get_available_tools(self) -> List[types.Tool]:
        """获取服务器提供的所有可用工具"""
        if not self.session:
            raise RuntimeError("客户端未连接，请先调用 connect() 方法")
            
        result = await self.session.list_tools()
        return result.tools
    
    async def get_weather_alerts(self, state: str) -> str:
        """
        获取指定州的天气预警信息
        
        Args:
            state: 两个字母的美国州代码 (例如: CA, NY)
            
        Returns:
            天气预警信息字符串
        """
        if not self.session:
            raise RuntimeError("客户端未连接，请先调用 connect() 方法")
            
        try:
            # 调用 get_alerts 工具
            result = await self.session.call_tool(
                "get_alerts", 
                {"state": state}
            )
            return result.content[0].text
        except Exception as e:
            return f"❌ 获取天气预警失败: {str(e)}"
    
    async def get_weather_forecast(self, latitude: float, longitude: float) -> str:
        """
        获取指定经纬度的天气预报
        
        Args:
            latitude: 纬度
            longitude: 经度
            
        Returns:
            天气预报信息字符串
        """
        if not self.session:
            raise RuntimeError("客户端未连接，请先调用 connect() 方法")
            
        try:
            # 调用 get_forecast 工具
            result = await self.session.call_tool(
                "get_forecast",
                {
                    "latitude": latitude,
                    "longitude": longitude
                }
            )
            return result.content[0].text
        except Exception as e:
            return f"❌ 获取天气预报失败: {str(e)}"
    
    async def close(self):
        """关闭客户端连接"""
        try:
            if self.session:
                # 正确关闭会话
                await self.session.__aexit__(None, None, None)
                self.session = None
                
            if self.stdio_context:
                # 正确关闭 stdio 连接
                await self.stdio_context.__aexit__(None, None, None)
                self.stdio_context = None
                
        except Exception as e:
            print(f"⚠️ 关闭连接时出现警告: {e}")

async def main():
    """主函数 - 演示客户端用法"""
    
    # 使用异步上下文管理器确保资源正确清理
    async with WeatherClient("weather.py") as client:
        print("=" * 50)
        print("🌤️  天气 MCP 客户端演示")
        print("=" * 50)
        
        # 1. 显示可用工具
        tools = await client.get_available_tools()
        print(f"tools: {json.dumps(tools, default=lambda o: o.__dict__, indent=2)}")
        print(f"\n📋 服务器提供 {len(tools)} 个工具:")
        for tool in tools:
            print(f"  • {tool.name}: {tool.description}")
        
        # 2. 获取加利福尼亚州的天气预警
        print(f"\n🚨 获取加利福尼亚州天气预警...")
        alerts = await client.get_weather_alerts("CA")
        print(alerts)
        
        # 3. 获取纽约的天气预报 (纽约市的经纬度)
        print(f"\n📅 获取纽约天气预报...")
        forecast = await client.get_weather_forecast(40.7128, -74.0060)
        print(forecast)
        
        # 4. 获取洛杉矶的天气预报
        print(f"\n📅 获取洛杉矶天气预报...")
        la_forecast = await client.get_weather_forecast(34.0522, -118.2437)
        print(la_forecast)

async def simple_example():
    """简单用法示例 - 修复版本"""
    client = WeatherClient("weather.py")
    try:
        await client.connect()
        
        # 直接获取某个州的预警
        texas_alerts = await client.get_weather_alerts("TX")
        print("德克萨斯州天气预警:")
        print(texas_alerts)
        
    finally:
        await client.close()

if __name__ == "__main__":
    # 运行主演示函数
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 客户端已退出")
    except Exception as e:
        print(f"❌ 客户端运行出错: {e}")