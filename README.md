# AI-water-essay
AI-generated essays for easy courses

## 写在最前

我是北京师范大学（BNU）的一名学生，我已经厌倦了为各种课程写各种论文。为了增加学分以便能够去香港攻读硕士课程，我选修了很多课程。然而，对于学习系统科学的学生来说，写论文非常困难。当然，我会使用 AI，而且上学期我学习了 LaTeX。所以，我决定把这两者结合起来。这样，我就可以轻松地利用各种 AI API 和 LaTeX 制作出漂亮的论文。而且，我太懒了，不想再复制粘贴了。

因此，我开发了一个程序，用于自动化生成水课论文的整个过程。你只需要提供你的个人信息，例如姓名、学号和邮箱地址。此外，你还需要在 Kimi 上注册一个 API。这个 API 会预存大约 10 元的费用，而生成一篇文章通常非常便宜，只需要几分钱。然后，只需将信息复制到界面中，就可以一键生成一篇“看起来还不错”的论文。虽然这些论文可能没有太多逻辑，仔细看就能发现是 AI 生成的，但用来应付水课已经完全足够了。

这是我第一次在 GitHub 上发布个人项目，当然还有很多需要改进的地方。请继续给我反馈，我会不断更新这个项目。如果这个项目能帮助到大家，我会非常开心！


### 代码原理
以下是您可以在 GitHub 的 `README.md` 文件中使用的代码原理说明，方便其他用户理解和使用您的项目：

---

# 论文生成器项目说明

## 项目简介
本项目是一个基于 Python 和 LaTeX 的自动化论文生成工具，利用 OpenAI 的 API（如 Kimi）生成论文的各个部分（如标题、摘要、正文、结论等），并将其自动编译为 PDF 格式的论文。通过简单的用户输入，用户可以快速生成符合学术格式的论文，适用于低优先级课程（“水课”）的作业需求。

## 核心功能
1. **自动化生成论文**：根据用户提供的主题、章节数量和相关信息，自动生成论文的各个部分。
2. **LaTeX 支持**：生成的论文以 LaTeX 格式保存，确保排版专业。
3. **PDF 编译**：自动调用 LaTeX 编译器（如 TinyTeX）将生成的 LaTeX 文件编译为 PDF。
4. **用户友好界面**：通过 Tkinter 提供图形化界面，用户只需填写基本信息即可生成论文。

## 代码原理
### 1. **用户输入**
用户通过图形化界面输入以下信息：
- 姓名、学号、邮箱、学校
- API 地址、API 网站地址、模型名称
- 论文主题、论文相关信息、章节数量

### 2. **论文生成流程**
#### （1）初始化文件夹和文件
- 创建 `data` 和 `output` 文件夹，用于存储中间文件和最终生成的 PDF。
- 复制 LaTeX 模板文件到 `data` 文件夹。

#### （2）生成论文框架
- 调用 OpenAI API，根据用户提供的主题和章节数量生成论文大纲。
- 大纲包括引言、正文章节和结论。

#### （3）生成正文内容
- 对每个章节，调用 OpenAI API 生成详细的 LaTeX 格式正文内容。
- 确保每个章节的内容符合学术规范，并扩展至指定字数。

#### （4）生成引言、结论、摘要和标题
- 根据生成的正文内容，分别调用 OpenAI API 生成引言、结论、摘要和标题。
- 确保每个部分的内容与正文逻辑一致。

#### （5）处理 LaTeX 文件
- 将生成的 LaTeX 内容插入到模板文件中。
- 替换模板中的占位符（如标题、摘要、正文等）为实际内容。

#### （6）编译 PDF
- 调用 LaTeX 编译器（如 TinyTeX）将 LaTeX 文件编译为 PDF。
- 生成的 PDF 文件保存在 `output` 文件夹中。

### 3. **关键技术**
#### （1）OpenAI API 调用
- 使用 OpenAI 的 `chat.completions.create` 方法生成论文内容。
- 通过设置 `temperature` 参数控制生成内容的随机性和创造性。

#### （2）LaTeX 模板处理
- 使用 LaTeX 模板文件（如 `example.tex`）作为论文的基础结构。
- 通过字符串替换将生成的内容插入到模板中。

#### （3）PDF 编译
- 使用 TinyTeX 或本地安装的 LaTeX 编译器（如 `pdflatex`）编译 LaTeX 文件。
- 确保生成的 PDF 文件格式正确。

### 4. **文件结构**
```
project/
├── data/                  # 存储中间文件（如 LaTeX 文件）
├── output/                # 存储最终生成的 PDF 文件
├── cover/                 # 存储 LaTeX 模板文件
├── main.py                # 主程序文件
├── aiessay.py             # 论文生成逻辑文件
└── README.md              # 项目说明文件
```

### 5. **依赖项
- **Python 3.x**
- **第三方库**：
  - `openai`：用于调用 OpenAI API。
  - `tkinter`：用于构建图形化界面。
  - `subprocess`：用于调用 LaTeX 编译器。
  - `os` 和 `shutil`：用于文件操作。
  - `re`：用于正则表达式处理。

### 6. **使用方法
1. **安装依赖**：
   ```bash
   pip install openai
   ```
2. **配置 API**：
   - 在 Kimi 或其他 OpenAI 平台注册并获取 API 地址和密钥。
   - 在界面中输入 API 相关信息。
3. **运行程序**：
   ```bash
   python main.py
   ```
4. **填写信息**：
   - 在图形化界面中输入个人信息、论文主题和相关内容。
5. **生成论文**：
   - 点击“生成论文”按钮，等待程序自动生成并编译 PDF。
6. **查看结果**：
   - 在 `output` 文件夹中查看生成的 PDF 文件。

### 7. **注意事项
- 确保 API 地址和密钥正确，否则无法调用 KIMI API。
- 如果未安装 LaTeX 编译器，请安装 TinyTeX 或其他 LaTeX 发行版。
- 生成的论文内容仅供参考，建议用户根据实际需求进行修改。
### 不足and更新
 - 没办法支持数据和公式
 - 太臃肿，我要想办法怎么办才可以不用这个编译器
