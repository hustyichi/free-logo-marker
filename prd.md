
# 产品需求与实现方案： free logo marker

**版本：** V1.0 (Local-First Edition)
**定位：** 专为独立开发者设计的、解耦的本地 Logo 自动化生成与处理命令行工具。

## 一、 产品概述

在敏捷探索海外市场产品或快速构建 MVP 时，繁琐的视觉资产准备工作往往会打断开发心流。本工具旨在提供一个纯本地运行、零运维成本的 CLI 脚本。它将“AI 生图”与“图像后期处理”完全解耦，既支持一键从文本生成标准 Web 资产，也支持将手工挑选/修改过的原图丢入处理管线，最大化灵活性。

## 二、 核心需求说明 (业务逻辑)

### 2.1 解耦的工作流设计

工具必须支持三种独立的运行模式，通过命令行参数进行控制：

1. **纯生图模式 (`--generate`)**：仅调用大模型 API 根据 Prompt 生成带有纯色背景的原始图片，保存至本地。适用于批量生成、人工筛选的场景。
2. **纯处理模式 (`--process`)**：读取本地指定的原始图片，执行无网去背、边界裁剪、尺寸标准化及格式转换。适用于对 AI 原图进行了人工微调，或直接处理其他渠道来源图片的场景。
3. **全链路模式 (`--all`)**：串联上述两步，一键输入 Prompt，直接输出最终的透明 PNG 和多分辨率 ICO。

### 2.2 核心处理规范

* **AI 生成规范**：必须在 Prompt 层面强制要求输出扁平化、纯色背景（如纯白）、无阴影的 2D 矢量风格图像，以保证后续本地 U-Net 模型抠图的成功率。
* **图像裁剪规范**：去背后的图像必须动态获取真实物理边界（Bounding Box）并进行紧凑裁剪，彻底消除四周的透明留白。
* **输出资产规范**：
* **主 Logo**：`{name}.png`，512x512 像素，透明背景，主体居中且预留 5% 左右的安全边距（Safe Area）。
* **Favicon**：`{name}_favicon.ico`，必须在单个文件中封包 16x16, 32x32, 48x48, 64x64 四种标准分辨率，并使用高质量重采样算法（Lanczos）防止缩放模糊。



## 三、 技术架构与实现方案

### 3.1 技术栈选型

* **语言**：Python 3.10+
* **交互接口**：`argparse`（标准库，用于构建 CLI 命令）。
* **外部 API (生图)**：`requests` 库调用合适的 AI 生图 API。
* **本地深度学习抠图**：`rembg`。底层基于 U-Net 架构（如 u2net 模型），完全在本地离线推理，去背边缘平滑且无需 API 费用。
* **图像几何操作**：`Pillow (PIL)`。负责读取二进制流、执行 `.getbbox()` 裁剪、Alpha 通道处理及 `.ico` 多尺寸封包。

### 3.2 目录结构规划

```text
free-logo-marker/
├── app/
│   ├── generate_logo.py     # 图像生成流程 
|   ├── process_logo.py      # 图像处理流程
├── pypeoject.toml           # 依赖清单 (rembg, pillow, requests)
├── .env                     # 存储 API 密钥 (FAL_KEY)
├── assets/                  # AI 生成的原始图片存放区
└── output/                  # 最终处理完毕的 png 和 ico 存放区

```

### 3.3 关键执行逻辑与异常处理
1. **模型按需下载**：`rembg` 首次在本地执行 `--process` 时，会自动从 GitHub 下载大约 170MB 的权重文件（存放于 `~/.u2net/`）。实现方案中需在文档或终端输出中给予用户明确的“正在下载模型”提示，避免误以为程序卡死。
2. **输入校验**：在执行 `--process` 时，必须强校验 `--input` 对应的本地文件是否存在，若不存在则抛出友好的路径错误提示。


### 3.4 图像生成支持方案
目前需要支持本次直接生成图像

```python
from openai import OpenAI
 
 client = OpenAI(
     base_url="http://127.0.0.1:8045/v1",
     api_key=""
 )
 
 response = client.chat.completions.create(
     model="gemini-3-pro-image",
     # 方式 1: 使用 size 参数 (推荐)
     # 支持: "1024x1024" (1:1), "1280x720" (16:9), "720x1280" (9:16), "1216x896" (4:3)
     extra_body={ "size": "1024x1024" },
     
     # 方式 2: 使用模型后缀
     # 例如: gemini-3-pro-image-16-9, gemini-3-pro-image-4-3
     # model="gemini-3-pro-image-16-9",
     messages=[{
         "role": "user",
         "content": "Draw a futuristic city"
     }]
 )
 
 print(response.choices[0].message.content)
```

后续需要支持其他类型的图像生成，比如其他线上的图像生成服务


## 四、 落地与使用示例

一旦代码编写完成，日常开发中可以通过终端极其高效地调用：

**场景 1：为新项目一键生成完整资产**

```bash
python logo_pipeline.py --all --prompt "minimalist clock icon, tech startup vibe, blue and white colors"

```

*预期结果*：在 `output/` 目录下瞬间得到 `logo.png` 和 `favicon.ico`，可直接拖入前端工程。

**场景 2：先生成几张看看效果（不处理）**

```bash
python logo_pipeline.py --generate --prompt "abstract geometric letter M, corporate style"
```

**场景 3：处理一张在 Photoshop 里精修过的原图**

```bash
python logo_pipeline.py --process --input "assets/logo.png"

```
