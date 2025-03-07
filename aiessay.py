from openai import OpenAI
import time
import re
import os
import subprocess
import shutil



def 初始化文本():
    # 获取当前脚本文件的绝对路径
    current_file_path = os.path.abspath(__file__)

    # 获取当前脚本文件所在目录的绝对路径
    current_dir_path = os.path.dirname(current_file_path)

    # 构建目标文件夹的绝对路径（即当前脚本文件所在目录下的data文件夹）
    target_folder_path = os.path.join(current_dir_path, 'data')

    # 创建目标文件夹，如果文件夹已存在则忽略
    os.makedirs(target_folder_path, exist_ok=True)

    # 构建目标txt文件的绝对路径
    target_file_path = os.path.join(target_folder_path, 'example.txt')

    # 创建txt文件，如果文件已存在则覆盖
    with open(target_file_path, 'w') as f:
        f.write('')  # 可以在这里写入一些初始内容

    # 返回txt文件的地址
    return target_file_path


def 生成框架(client,topic, info, num_sections,用户信息):
    # 构造 Prompt
    prompt = f"""
    请为我生成一篇关于“{topic}”的中文论文大纲，包含以下内容：
    - 引言
    - 正文部分需分为 {num_sections} 个章节（提供每章节的标题）。
    - 结论
    {f"附加信息：{info}" if info else ""}
    请注意，大纲需结构清晰，标题简洁明了。
    每一个大的部分之间用2个换行符来隔开。
    每一个小的部分之间用1个换行符来隔开。
    在你生成框架的时候，你不需要给我与框架无关的任何内容，也就是说，你只需要直接返回给我框架的内容！
    """
    # 调用 API
    completion = client.chat.completions.create(
        model=f"{用户信息['模型名称']}",
        messages=[
            {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    # 处理生成的大纲
    outline_content = completion.choices[0].message.content
    # 按换行符分割大纲并返回列表
    outline_list = [line.strip() for line in outline_content.split("\n\n") if line.strip()]
    return outline_list

def 生成正文部分(client,框架内容,用户信息):
    啊米诺斯 = 框架内容
    提示词 = f"""接下来请根据以下框架内容生成论文正文的 LaTeX 代码：
    框架内容：
    {啊米诺斯}

    生成规则：
    1. 主标题使用 \\section。
    2. 子标题使用 \\subsection。
    3. 若框架内容中存在分点，请使用 itemize 环境表示，每个分点需适当扩展成完整句子。
    4. 每个小标题及其对应内容需扩写为至少150字，确保内容完整且逻辑清晰。
    5. 保持论文风格，语言专业且流畅。
    6. 不需要任何的latex代码调用库的内容，也就是说只需要给我一个完整的section的代码
    7. 可以在适当添加一些数据，让论文更加符合实际

    注意：你只需要返回完整的 LaTeX 代码，不需要任何无关内容。
    \\section{{主标题}}
    在这里详细展开主标题下的内容。
    \\subsection{{子标题}}
    进一步扩展子标题下的内容，包括细节描述、方法说明等。
    \\begin{{itemize}}
    \\item 分点内容1，具体描述。
    \\item 分点内容2，具体描述。
    \\end{{itemize}}

    请严格按照上述规则生成！"""
    retries = 20 # 最大重试次数
    while retries > 0:
        try:
            completion = client.chat.completions.create(
                model=f"{用户信息['模型名称']}",
                messages=[
                    {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，擅长生成 LaTeX 代码。"},
                    {"role": "user", "content": 框架内容},
                    {"role": "user", "content": 提示词},
                ],
                temperature=0.3,
            )
            content = completion.choices[0].message.content
            # 移除 ```latex 标识
            content = content.replace("```latex", "").replace("```", "")
            return content
        except Exception as e:
            if "rate_limit_reached_error" in str(e):
                print("触发api每分钟访问限制，请稍等")
                time.sleep(1)
                retries -= 1
            else:
                raise e
    raise RuntimeError("超过最大重试次数，生成失败")

def 生成结论(client,file_path,用户信息):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    提示词 = f"""接下来请根据以下论文的正文部分来总结得到相应的结论，生成论文正文的 LaTeX 代码：
    {content}

    生成规则：
    1. 主标题使用 \\section，这个部分的标题就叫做section{"结论"}。
    2. 不一定需要子标题，打碎如果有的话子标题使用 \\subsection。
    3. 若框架内容中存在分点，请使用 itemize 环境表示，每个分点需适当扩展成完整句子。
    4. 每个小标题及其对应内容需扩写为至少250字，确保内容完整且逻辑清晰。
    5. 保持论文风格，语言专业且流畅。
    6. 不需要任何的latex代码调用库的内容，也就是说只需要给我一个完整的section的代码

    注意：你只需要返回完整的 LaTeX 代码，不需要任何无关内容。例如：
    \\section{{主标题}}
    在这里详细展开主标题下的内容。
    \\subsection{{子标题}}
    进一步扩展子标题下的内容，包括细节描述、方法说明等。
    \\begin{{itemize}}
    \\item 分点内容1，具体描述。
    \\item 分点内容2，具体描述。
    \\end{{itemize}}

    请严格按照上述规则生成！"""
    retries = 20 # 最大重试次数
    while retries > 0:
        try:
            completion = client.chat.completions.create(
                model=f"{用户信息['模型名称']}",
                messages=[
                    {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，擅长生成 LaTeX 代码。"},
                    {"role": "user", "content": 提示词},
                ],
                temperature=0.3,
            )
            content = completion.choices[0].message.content
            # 移除 ```latex 标识
            content = content.replace("```latex", "").replace("```", "")
            return content
        except Exception as e:
            if "rate_limit_reached_error" in str(e):
                print("触发api每分钟访问限制，请稍等")
                time.sleep(1)
                retries -= 1
            else:
                raise e
    raise RuntimeError("超过最大重试次数，生成失败")

def 生成引言(client,file_path,用户信息):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    提示词 = f"""接下来请根据以下论文的正文部分来总结得到相应的引言，生成论文正文的 LaTeX 代码：
    框架内容：
    {content}

    生成规则：
    1. 主标题使用 \\section,这个部分的标题就叫做section{"引言"}。
    2. 不一定需要子标题，但是如果有的话子标题使用 \\subsection。
    3. 若框架内容中存在分点，请使用 itemize 环境表示，每个分点需适当扩展成完整句子。
    4. 每个小标题及其对应内容需扩写为至少250字，确保内容完整且逻辑清晰。
    5. 保持论文风格，语言专业且流畅。
    6. 不需要任何的latex代码调用库的内容，也就是说只需要给我一个完整的section的代码

    注意：你只需要返回完整的 LaTeX 代码，不需要任何无关内容。例如：
    \\section{{主标题}}
    在这里详细展开主标题下的内容。
    \\subsection{{子标题}}
    进一步扩展子标题下的内容，包括细节描述、方法说明等。
    \\begin{{itemize}}
    \\item 分点内容1，具体描述。
    \\item 分点内容2，具体描述。
    \\end{{itemize}}

    请严格按照上述规则生成！"""
    retries = 20 # 最大重试次数
    while retries > 0:
        try:
            completion = client.chat.completions.create(
                model=f"{用户信息['模型名称']}",
                messages=[
                    {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，擅长生成 LaTeX 代码。"},
                    {"role": "user", "content": 提示词},
                ],
                temperature=0.3,
            )
            content = completion.choices[0].message.content
            # 移除 ```latex 标识
            content = content.replace("```latex", "").replace("```", "")
            return content
        except Exception as e:
            if "rate_limit_reached_error" in str(e):
                print("触发api每分钟访问限制，请稍等")
                time.sleep(1)
                retries -= 1
            else:
                raise e
    raise RuntimeError("超过最大重试次数，生成失败")

def 生成摘要(client,file_path,用户信息):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    提示词 = f'''
    读取这个论文的内容，然后生成一个摘要{content}
    1. 直接返回完整的摘要 LaTeX 代码（从 beginabstract开始 到 endabstract）以及中间的摘要正文部分，其他的代码什么都不要给我，无需提供任何与正文无关的额外内容。
    2. 使用标准 LaTeX 摘要格式，确保代码清晰、准确。
    3. 摘要内容需学术性强，具有吸引力和逻辑性。
    4. 摘要代码中不需要包含调用库的部分，仅保留摘要部分的核心代码。'''
    retries = 20 # 最大重试次数
    while retries > 0:
        try:
            completion = client.chat.completions.create(
                model=f"{用户信息['模型名称']}",
                messages=[
                    {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，擅长生成 LaTeX 代码。"},
                    {"role": "user", "content": 提示词},
                ],
                temperature=0.3,
            )
            content = completion.choices[0].message.content
            # 移除 ```latex 标识
            content = content.replace("```latex", "").replace("```", "")
            return content
        except Exception as e:
            if "rate_limit_reached_error" in str(e):
                print("触发api每分钟访问限制，请稍等")
                time.sleep(1)
                retries -= 1
            else:
                raise e
    raise RuntimeError("超过最大重试次数，生成失败")

def 生成标题(client,file_path,用户信息):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    提示词 = f'''
    根据以下论文内容，生成一个简洁、学术性强且概括全文的标题：
    {content}
    1. 标题需准确反映论文的核心内容和主题。
    2. 确保标题清晰、有吸引力，符合学术写作规范。
    3. 仅返回标题内容，不需要其他额外解释或文字。
    4. 格式为：......，不需要双引号和其他的符号。只需要直接给我标题就好
    '''
    retries = 20 # 最大重试次数
    while retries > 0:
        try:
            completion = client.chat.completions.create(
                model=f"{用户信息['模型名称']}",
                messages=[
                    {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，擅长生成 LaTeX 代码。"},
                    {"role": "user", "content": 提示词},
                ],
                temperature=0.3,
            )
            content = completion.choices[0].message.content
            # 移除 ```latex 标识
            content = content.replace("```latex", "").replace("```", "")
            return content
        except Exception as e:
            if "rate_limit_reached_error" in str(e):
                print("触发api每分钟访问限制，请稍等")
                time.sleep(1)
                retries -= 1
            else:
                raise e
    raise RuntimeError("超过最大重试次数，生成失败")


def 读取模板地址():
    """
    读取data文件夹中的第一个.tex文件，并返回其地址。
    如果data文件夹不存在或没有.tex文件，则返回None。
    """
    # 获取当前脚本文件所在目录的绝对路径
    current_dir_path = os.path.dirname(os.path.abspath(__file__))

    # 构建data文件夹的绝对路径
    data_folder_path = os.path.join(current_dir_path, 'data')

    # 检查data文件夹是否存在
    if not os.path.exists(data_folder_path):
        print("data文件夹不存在")
        return None

    # 遍历data文件夹中的文件
    for filename in os.listdir(data_folder_path):
        # 检查文件扩展名是否为.tex
        if filename.endswith(".tex"):
            # 构建.tex文件的绝对路径
            tex_file_path = os.path.join(data_folder_path, filename)
            return tex_file_path

    # 如果没有找到.tex文件，返回None
    print("data文件夹中没有找到.tex文件")
    return None


def 标题处理(txt_file, tex_file):
    # 读取txt文件中的内容，只取标题到第一个换行符的部分
    with open(txt_file, 'r', encoding='utf-8') as f:
        txt_content = f.readline().strip()  # 只读取第一行内容并去掉首尾空白字符

    # 读取tex文件中的内容
    with open(tex_file, 'r', encoding='utf-8') as f:
        tex_content = f.read()

    # 替换AAAAA为txt文件中的内容
    updated_tex_content = tex_content.replace('题目', txt_content)

    # 将修改后的内容保存回tex文件
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(updated_tex_content)

    print(f"替换完成！内容已保存到 {tex_file}")
    
def 摘要处理(txt_file, tex_file):
    # 读取txt文件中的内容
    with open(txt_file, 'r', encoding='utf-8') as f:
        txt_content = f.read()

    # 使用正则表达式提取以\begin{abstract}开头，以\end{abstract}结尾的内容
    abstract_pattern = r"\\begin\{abstract\}.*?\\end\{abstract\}"
    match = re.search(abstract_pattern, txt_content, re.DOTALL)  # re.DOTALL支持跨行匹配

    if not match:
        print("未找到摘要部分，请检查txt文件内容格式。")
        return

    abstract_content = match.group()  # 获取匹配的摘要部分

    # 读取tex文件内容
    with open(tex_file, 'r', encoding='utf-8') as f:
        tex_content = f.read()

    # 替换tex文件中的BBBBB为摘要内容
    updated_tex_content = tex_content.replace('摘要', abstract_content)

    # 将修改后的内容保存回tex文件
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(updated_tex_content)

    print(f"摘要替换完成！内容已保存到 {tex_file}")  
    
def 正文处理(txt_file, tex_file):
    # 读取txt文件中的内容
    with open(txt_file, 'r', encoding='utf-8') as f:
        txt_content = f.read()

    # 使用正则表达式提取\end{abstract}之后的内容
    abstract_end_pattern = r"\\end\{abstract\}(.*)"  # 匹配\end{abstract}后面的内容
    match = re.search(abstract_end_pattern, txt_content, re.DOTALL)  # 支持跨行匹配

    if not match:
        print("未找到\\end{abstract}之后的内容，请检查txt文件格式。")
        return

    body_content = match.group(1).strip()  # 获取\end{abstract}之后的内容，并去掉首尾空白字符

    # 读取tex文件内容
    with open(tex_file, 'r', encoding='utf-8') as f:
        tex_content = f.read()

    # 替换tex文件中的CCCCC为正文内容
    updated_tex_content = tex_content.replace('正文', body_content)

    # 将修改后的内容保存回tex文件
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(updated_tex_content)

    print(f"正文替换完成！内容已保存到 {tex_file}")
    
def 个人信息处理(tex_file,用户信息):

    # 读取tex文件内容
    with open(tex_file, 'r', encoding='utf-8') as f:
        tex_content = f.read()
    updated_tex_content = (
        tex_content.replace('姓名', 用户信息["姓名"])
                   .replace('学号号码', 用户信息["学号"])
                   .replace('邮箱', 用户信息["邮箱"])
                   .replace('学校', 用户信息["学校"])
    )

    # 将修改后的内容保存回tex文件
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(updated_tex_content)

    print(f"信息替换完成！内容已保存到 {tex_file}")
    
def 查找编译器地址():
    """
    在当前脚本文件所在目录下的TinyTeX-1文件夹中，
    搜索名为pdflatex.exe的文件，并返回其完整路径。
    如果未找到该文件，则返回None。
    """
    # 获取当前脚本文件所在目录的绝对路径
    current_dir_path = os.path.dirname(os.path.abspath(__file__))

    # 构建TinyTeX-1文件夹的绝对路径
    tinytex_folder_path = os.path.join(current_dir_path, 'TinyTeX-1')

    # 检查TinyTeX-1文件夹是否存在
    if not os.path.exists(tinytex_folder_path):
        print("TinyTeX-1文件夹不存在")
        return None

    # 递归搜索pdflatex.exe文件
    for root, dirs, files in os.walk(tinytex_folder_path):
        if 'pdflatex.exe' in files:
            # 构建pdflatex.exe文件的完整路径
            pdflatex_path = os.path.join(root, 'pdflatex.exe')
            return pdflatex_path

    # 如果未找到pdflatex.exe文件，返回None
    print("未找到pdflatex.exe文件")
    return None


def 编译pdf(compiler_path, tex_file_path):
    """
    使用指定的编译器地址和 .tex 文件地址编译生成 PDF 文件，
    并将生成的 PDF 文件保存到当前脚本文件所在目录下的 output 文件夹中。
    
    参数：
    - compiler_path：编译器的绝对路径
    - tex_file_path：.tex 文件的绝对路径
    """
    # 获取当前脚本文件所在目录的绝对路径
    current_dir_path = os.path.dirname(os.path.abspath(__file__))

    # 构建 output 文件夹的绝对路径
    output_dir_path = os.path.join(current_dir_path, 'output')

    # 确保 output 文件夹存在
    os.makedirs(output_dir_path, exist_ok=True)

    # 构建编译命令
    command = [
        compiler_path,
        f"-output-directory={output_dir_path}",
        tex_file_path
    ]

    # 执行编译命令
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print("编译成功！")
        print(result.stdout)  # 打印编译器输出的消息
    except subprocess.CalledProcessError as e:
        print("编译失败！")
        print(e.stderr)  # 打印错误信息


def 处理论文文件():
    # 获取当前脚本文件所在目录的绝对路径
    current_dir_path = os.path.dirname(os.path.abspath(__file__))
    
    # 定义 data 和 output 文件夹路径
    data_dir = os.path.join(current_dir_path, 'data')
    output_dir = os.path.join(current_dir_path, 'output')
    
    # 确保 output 文件夹存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 查找 data 文件夹中的 .tex 文件
    tex_files = [f for f in os.listdir(data_dir) if f.endswith('.tex')]
    if not tex_files:
        print("在 data 文件夹中未找到 .tex 文件。")
        return
    
    # 复制 .tex 文件到 output 文件夹
    for tex_file in tex_files:
        shutil.copy(os.path.join(data_dir, tex_file), output_dir)
    
    # 删除 output 文件夹中除 .pdf 和 .tex 以外的文件
    for file in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file)
        if not (file.endswith('.pdf') or file.endswith('.tex')):
            os.remove(file_path)
    
    # 重命名 .pdf 和 .tex 文件为 "你的论文 + 后缀名"
    for file in os.listdir(output_dir):
        old_path = os.path.join(output_dir, file)
        new_name = f"你的论文{os.path.splitext(file)[1]}"
        new_path = os.path.join(output_dir, new_name)
        os.rename(old_path, new_path)
    
    print("文件处理完成！")



def 处理文本文件(file_path ):
    """
    删除txt文件中自定义的内容

    :param file_path: txt文件的路径
    :param custom_contents: 自定义要删除的内容列表，例如["要删除的内容1", "要删除的内容2"]
    """
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    custom_contents = ["\documentclass{article}","\begin{document}","\author{}","\date{}","\end{document}"]
    # 删除自定义内容
    new_lines = []
    for line in lines:
        for content in custom_contents:
            line = line.replace(content, "")
        new_lines.append(line)

    # 将修改后的内容写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)


def clear_folder(folder_path):
    """清空指定文件夹中的所有文件和子文件夹"""
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        print(f"{folder_path} cleared.")
    else:
        print(f"{folder_path} does not exist.")

def 初始化文件夹():
    # 获取当前文件所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 清空 data 文件夹
    data_folder = os.path.join(current_dir, 'data')
    clear_folder(data_folder)
    
    # 清空 output 文件夹
    output_folder = os.path.join(current_dir, 'output')
    clear_folder(output_folder)
    
    # 确保 cover 文件夹中的 .tex 文件复制到 data 文件夹
    cover_folder = os.path.join(current_dir, 'cover')
    for filename in os.listdir(cover_folder):
        if filename.endswith('.tex'):
            cover_file_path = os.path.join(cover_folder, filename)
            data_file_path = os.path.join(data_folder, filename)
            try:
                # 复制 .tex 文件到 data 文件夹
                shutil.copy(cover_file_path, data_file_path)
                print(f"Copied {filename} to data folder.")
            except Exception as e:
                print(f"Error copying {filename}: {e}")



