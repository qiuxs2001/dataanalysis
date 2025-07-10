# 导入必要的库
import gradio as gr  # Gradio用户界面库
from data_analysis_code import DataAnalysisApp  # 导入数据分析应用类
import matplotlib.pyplot as plt  # 绘图库
import os  # 操作系统接口

def main():
    """主函数，创建并启动Gradio界面"""
    # 创建数据分析应用实例
    app = DataAnalysisApp()
    
    # 使用Gradio Blocks创建自定义界面布局
    with gr.Blocks() as demo:
        # 添加标题
        gr.Markdown("# 智能数据分析助手")

        # 第一行：文件上传区域
        with gr.Row():
            with gr.Column():
                # 文件上传组件
                file_input = gr.File(label="上传文件")
                # 上传状态显示
                upload_status = gr.Textbox(label="上传状态")
            with gr.Column():
                # 数据预览表格
                data_preview = gr.DataFrame(label="数据预览")

        # 第二行：问题输入区域
        with gr.Row():
            question_input = gr.Textbox(
                label="请输入您的问题",
                placeholder="例如，计算每列的基本统计信息",

            )
        # 第三行：结果显示区域
        with gr.Row():
            with gr.Column():
                # 分析结果文本框
                analysis_output = gr.Textbox(label="分析结果")
                # 代码显示框（只读）
                code_output = gr.Code(label="代码", language="python", interactive=False)
            with gr.Column():
                # 图表显示区域（只读）
                plot_output = gr.Image(label="图表", interactive=False)

        # 绑定文件上传事件
        file_input.upload(
            app.process_file,  # 调用处理文件的方法
            inputs=[file_input],  # 输入：上传的文件
            outputs=[upload_status, data_preview],  # 输出：状态和数据预览
        )

        # 绑定问题提交事件
        question_input.submit(
            app.analyze_data,  # 调用数据分析方法
            inputs=[question_input],  # 输入：用户问题
            outputs=[analysis_output, code_output, plot_output],  # 输出：分析结果、代码、图表
        )
        

                

    # 启动Gradio应用
    demo.launch()

if __name__ == "__main__":
    """程序入口点，配置环境并启动应用"""
    
    # 设置OpenAI API配置
    os.environ["OPENAI_API_KEY"] = "sk-20f470100bd645f8b93db1bd38605bc6"
    os.environ["OPENAI_BASE_URL"] = "https://api.deepseek.com/v1"
    
    # 设置matplotlib中文字体支持
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'STHeiti', 'SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    
    # 启动主程序
    main()