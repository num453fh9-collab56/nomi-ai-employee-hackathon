import gradio as gr
from main import GeneralAgent
import os

agent = GeneralAgent()

def process_file(file):
    if file is None:
        return "Koi file upload nahi ki!"
    result = agent.process_document(file.name)
    if result:
        # Find latest report
        reports = os.listdir("reports")
        if reports:
            latest = sorted(reports)[-1]
            with open(f"reports/{latest}", "r") as f:
                return f.read()
    return "Processing failed!"

def run_synthesis():
    report_path = agent.generate_master_strategy_report()
    if report_path:
        with open(report_path, "r") as f:
            return f.read()
    return "No files found!"

demo = gr.TabbedInterface(
    [
        gr.Interface(
            fn=process_file,
            inputs=gr.File(label="File upload karo (.txt ya .md)"),
            outputs=gr.Textbox(label="Report", lines=25),
            title="📄 Single File Process"
        ),
        gr.Interface(
            fn=run_synthesis,
            inputs=[],
            outputs=gr.Textbox(label="Master Report", lines=25),
            title="🔍 Full Synthesis"
        )
    ],
    tab_names=["Single File", "Master Synthesis"]
)

demo.launch()
