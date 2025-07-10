# 导入必要的库
import os  # 操作系统接口
import pandas as pd  # 数据处理库
from langchain_openai import ChatOpenAI  # OpenAI聊天模型
from langchain_experimental.agents import create_pandas_dataframe_agent  # 创建pandas数据框代理
from langchain.agents import AgentType  # 代理类型
import contextlib  # 上下文管理工具
import matplotlib.pyplot as plt  # 绘图库
import tempfile  # 临时文件处理
import re  # 正则表达式

class CodeCapture:
    """代码捕获类，用于捕获和存储Agent执行过程中的输出和代码"""
    def __init__(self):
        self.output = []  # 存储所有输出内容
        self.code = []  # 存储提取的代码片段

    def clean_ansi_codes(self, text):
        """清理文本中的ANSI转义码（颜色和格式控制字符）"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def clean_code(self, code):
        """清理代码中的特殊字符和格式标记"""
        # 移除ANSI转义码
        code = self.clean_ansi_codes(code)
        code = code.strip()
        # 移除markdown代码块标记
        if code.startswith("```python"):
            code = code[9:].strip()
        if code.startswith("```"):
            code = code[3:].strip()
        if code.endswith("```"):
            code = code[:-3:].strip()
        return code

    def write(self, text):
        """捕获Agent输出的文本，并提取其中的代码"""
        self.output.append(text)

        # 检查是否包含Agent的动作和输入
        if "Action:" in text and "Action Input:" in text:
            # 使用正则表达式提取Action Input到Observation之间的内容
            code_match = re.search(r"Action Input:(.*?)(?=\nObservation:|$)", text, re.DOTALL)
            if code_match:
                code = code_match.group(1).strip()
                code = self.clean_ansi_codes(code)
                code = self.clean_code(code)
                if code:
                    self.code.append(code)
            
    # def get_code(self):
    #     """获取所有捕获的代码，用换行符连接"""
    #     return '\n'.join(self.code)

    # def get_output(self):
    #     """获取所有捕获的输出内容"""
    #     return ''.join(self.output)

class DataAnalysisApp:
    """数据分析应用主类，负责文件处理、Agent创建和数据分析"""

    def __init__(self):
        """初始化数据分析应用"""
        # 注释掉的API密钥设置（在main函数中设置）
        # os.environ["OPENAI_API_KEY"] = "sk-20f470100bd645f8b93db1bd38605bc6"
        # os.environ["OPENAI_BASE_URL"] = "https://api.deepseek.com/v1"
        
        self.df = None  # 存储加载的数据框
        self.agent = None  # 存储创建的LangChain代理
        self.capture = CodeCapture()  # 代码捕获器实例
        
    def create_agent(self):
        """创建LangChain数据分析代理"""
        if self.df is not None:
            # 初始化ChatOpenAI模型
            llm = ChatOpenAI(
                model="deepseek-chat",
                model_kwargs={
                    "messages": [
                        {"role": "system", "content": "你是一个专业的数据分析师，请用中文回答问题。当进行数据分析时，尽可能提供可视化图表来展示结果。"}
                    ]
                }
            )

            # 创建pandas数据框代理
            self.agent = create_pandas_dataframe_agent(
                llm=llm,  # 语言模型
                df=self.df,  # 数据框
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # 代理类型
                verbose=True,  # 详细输出
                allow_dangerous_code=True  # 允许执行代码
            )
    
    def process_file(self, file):
        """处理上传的文件，支持CSV和Excel格式"""
        # 获取文件扩展名
        file_path, ext = os.path.splitext(file)
        
        # 根据文件类型读取数据
        if ext.lower() == '.csv':
            self.df = pd.read_csv(file)
        elif ext.lower() == '.xlsx':
            self.df = pd.read_excel(file)
        else:
            return "不支持该文件格式", None

        # 创建数据分析代理
        self.create_agent()

        # 返回加载状态和数据预览
        return f"文件已成功加载， 数据形状：{self.df.shape}", self.df.head()
    def analyze_data(self, question):
        """分析数据并返回结果、代码和图表"""
        # 检查数据是否已加载
        if self.df is None:
            return "请先上传文件", "", None
        # 检查代理是否已初始化
        if self.agent is None:
            return "Agent未初始化", "", None
        
        # 重定向标准输出到代码捕获器，捕获Agent执行过程
        with contextlib.redirect_stdout(self.capture):
             result = self.agent.invoke({"input": question})

        # 获取执行的代码
        executed_code = '\n'.join(self.capture.code)

        # 检查是否生成了图表
        if len(plt.get_fignums()) > 0:
            plt.savefig("tmp_plot.png")  # 保存图表
            plt.close()  # 关闭图表
            return result["output"], executed_code, "tmp_plot.png"

        # 返回分析结果、执行的代码和图表路径
        return result["output"], executed_code, None



if __name__ == '__main__':
    """主程序入口，用于测试数据分析功能"""
    # 设置OpenAI API配置
    os.environ["OPENAI_API_KEY"] = "sk-20f470100bd645f8b93db1bd38605bc6"
    os.environ["OPENAI_BASE_URL"] = "https://api.deepseek.com/v1"
    
    # 设置matplotlib中文字体支持
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'STHeiti', 'SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

    # 创建数据分析应用实例
    app = DataAnalysisApp()
    
    # 测试文件路径
    file_name = r"C:\Users\26456\Downloads\sales_data.csv"
    # 处理文件
    app.process_file(file_name)
    # 执行数据分析查询
    result = app.agent.invoke({"input":"查询不同类别商品的销售额"})
    # 打印结果
    print(result)