import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading  # 导入 threading 模块
from openai import OpenAI
import aiessay as ae
import time
import sys
from PIL import Image, ImageTk

# 获取用户资料的函数
用户须知 = '''
1.必须先要去各个ai的官网注册得到相应的api秘钥，api网址，并且知道自己想使用什么模型
2.本程序不搜集任何的用户资料
3.有任何问题请联系QQ1750644569

'''
ae.初始化文件夹()

def 获取用户资料():
    user_info = {
        "姓名": name_entry.get(),
        "学号": student_id_entry.get(),
        "邮箱": email_entry.get(),
        "学校": school_entry.get(),
        "API地址": api_key_entry.get(),
        "API网站地址": api_base_url_entry.get(),
        "模型名称": model_name_entry.get(),
        "论文主题": paper_topic_entry.get(),
        "论文相关信息": paper_info_entry.get("1.0", tk.END).strip(),
        "章节数量": int(chapters_entry.get())
    }
    return user_info

# 重定向输出到文本框的类
class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)  # 自动滚动到文本框的底部

    def flush(self):
        pass

# 生成论文的函数
def 生成论文():
    try:
        # 在生成论文之前，重定向输出到文本框
        output_redirect = RedirectText(output_text)
        sys.stdout = output_redirect  # 设置标准输出重定向

        # 获取用户资料
        用户信息 = 获取用户资料()

        # 设置 OpenAI 客户端
        client = OpenAI(
            api_key=f"{用户信息['API地址']}",  # 替换为你的 API Key
            base_url=f"{用户信息['API网站地址']}",
        )

        # 获取论文框架
        print(f"生成论文主题：{用户信息['论文主题']}")
        框架 = ae.生成框架(client, 用户信息["论文主题"], 用户信息["论文相关信息"], 用户信息["章节数量"], 用户信息)
        框架 = 框架[1:-1]
        print("\n框架生成完毕")

        # 创建空白文件
        文本地址 = ae.初始化文本()

        # 按章节生成内容
        for i in range(len(框架)):
            print(f"\n正在生成 {框架[i]} 的内容...")
            section_content = ae.生成正文部分(client, 框架[i], 用户信息)
            print(f"\n{框架[i]} 的 LaTeX 内容：\n{section_content}")

            # 将生成的内容追加到文件中
            with open(文本地址, "a", encoding="utf-8") as f:
                f.write(f"\n\n{section_content}")
                print(f"内容已追加到 '{文本地址}'")
            time.sleep(1)  # 每次请求间隔 1 秒，避免触发速率限制

        # 生成结论并追加到文件末尾
        print("正在生成结论...")
        结论 = ae.生成结论(client, 文本地址, 用户信息)
        with open(文本地址, 'a', encoding='utf-8') as file:
            file.write(f'\n{结论}')
        print("结论生成完毕，并已追加到文件末尾。")

        # 生成引言并插入到文件开头
        print("正在生成引言...")
        引言 = ae.生成引言(client, 文本地址, 用户信息)
        with open(文本地址, 'r', encoding='utf-8') as file:
            original_content = file.read()
        新文件 = 引言 + original_content
        with open(文本地址, 'w', encoding='utf-8') as file:
            file.write(新文件)
        print("引言生成完毕，并已插入到文件开头。")

        # 生成摘要并插入到文件开头
        print("正在生成摘要...")
        摘要 = ae.生成摘要(client, 文本地址, 用户信息)
        with open(文本地址, 'r', encoding='utf-8') as file:
            original_content = file.read()
        新文件 = 摘要 + original_content
        with open(文本地址, 'w', encoding='utf-8') as file:
            file.write(新文件)
        print("摘要生成完毕，并已插入到文件开头。")

        # 生成标题并插入到文件开头
        print("正在生成标题...")
        标题 = ae.生成标题(client, 文本地址, 用户信息)
        with open(文本地址, 'r', encoding='utf-8') as file:
            original_content = file.read()
        新文件 = 标题 + original_content
        with open(文本地址, 'w', encoding='utf-8') as file:
            file.write(新文件)
        print("标题生成完毕，并已插入到文件开头。")

        # 处理文本文件
        ae.处理文本文件(文本地址)
        print("全部生成完成")

        print("开始处理文本")
        模板地址 = ae.读取模板地址()
        print("现在开始处理标题")
        ae.标题处理(文本地址, 模板地址)
        print("现在开始处理摘要")
        ae.摘要处理(文本地址, 模板地址)
        print("现在开始处理正文")
        ae.正文处理(文本地址, 模板地址)
        print("现在开始再模板中填写个人信息")
        ae.个人信息处理(模板地址, 用户信息)
        print("latex模板生成完毕，现在准备开始编译")

        模板地址 = ae.读取模板地址()
        print(f"查找到的模板地址为{模板地址}")
        编译器地址 = ae.查找编译器地址()
        print(f"查找到的编译器地址为{编译器地址}")
        ae.编译pdf(编译器地址, 模板地址)
        ae.处理论文文件()
        print("编译完成，请在output文件夹中找到你的论文~")
        print("谢谢你用我写的程序，虽然很简陋，但是我会继续更新的")
        
        # 提示生成完成
        messagebox.showinfo("完成", "论文生成完成，请在output文件夹中找到你的论文~")
    
    except Exception as e:
        messagebox.showerror("错误", str(e))

# 创建主窗口
root = tk.Tk()
root.title("论文生成器")

# 设置窗口的初始大小和最小尺寸
root.geometry("400x600")
root.minsize(400, 650)

# 设置窗口不可调节大小
root.resizable(width=False, height=False)

# 用户信息输入区
user_info_frame = tk.Frame(root)
user_info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

tk.Label(user_info_frame, text="姓名:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
name_entry = tk.Entry(user_info_frame)
name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

tk.Label(user_info_frame, text="学号:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
student_id_entry = tk.Entry(user_info_frame)
student_id_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

tk.Label(user_info_frame, text="邮箱:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
email_entry = tk.Entry(user_info_frame)
email_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

tk.Label(user_info_frame, text="学校:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
school_entry = tk.Entry(user_info_frame)
school_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

tk.Label(user_info_frame, text="API地址:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
api_key_entry = tk.Entry(user_info_frame)
api_key_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

tk.Label(user_info_frame, text="API网站地址:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
api_base_url_entry = tk.Entry(user_info_frame)
api_base_url_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")


tk.Label(user_info_frame, text="模型名称:").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
model_name_entry = tk.Entry(user_info_frame)
model_name_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

tk.Label(user_info_frame, text="论文主题:").grid(row=7, column=0, sticky=tk.W, padx=10, pady=5)
paper_topic_entry = tk.Entry(user_info_frame)
paper_topic_entry.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

tk.Label(user_info_frame, text="论文相关信息:").grid(row=8, column=0, sticky=tk.W, padx=10, pady=5)
paper_info_entry = scrolledtext.ScrolledText(user_info_frame, height=5, width=30)
paper_info_entry.grid(row=8, column=1, padx=10, pady=5, sticky="ew")

tk.Label(user_info_frame, text="章节数量:").grid(row=9, column=0, sticky=tk.W, padx=10, pady=5)
chapters_entry = tk.Entry(user_info_frame)
chapters_entry.grid(row=9, column=1, padx=10, pady=5, sticky="ew")

# 创建输出框
output_text = scrolledtext.ScrolledText(root, height=10, width=50)
output_text.grid(row=1, column=0, padx=10, pady=10)

# 创建生成按钮
generate_button = tk.Button(root, text="生成论文", width=20, height=2, command=lambda: threading.Thread(target=生成论文).start())
generate_button.grid(row=2, column=0, pady=20)

# 启动主循环
root.mainloop()

