# Free Logo Marker

专为独立开发者设计的本地 Logo 自动化生成与处理命令行工具。

## 功能特性

- **AI 图像生成**: 通过 OpenAI 兼容 API 根据文本提示生成 Logo 图片
- **本地去背景**: 使用 `rembg` (U-Net 模型) 在本地离线去除背景，无需 API 费用
- **自动裁剪**: 智能检测内容边界并紧凑裁剪
- **标准输出**: 生成 512x512 透明 PNG 和多分辨率 ICO favicon

## 环境要求

- Python 3.10+
- 依赖: openai, rembg, pillow, python-dotenv, requests, onnxruntime, numba

## 安装

```bash
# 克隆项目
git clone git@github.com:hustyichi/free-logo-marker.git
cd free-logo-marker

# 安装依赖 (推荐使用 uv)
uv sync

# 或使用 pip
pip install -e .
```

## 配置

复制环境变量模板并配置:

```bash
cp .env.example .env
```

编辑 `.env` 文件配置图像生成 API:

```env
# 图像生成 API 配置
GEN_API_BASE_URL=http://127.0.0.1:8045/v1
GEN_API_KEY=not-needed
GEN_MODEL_NAME=gemini-3-pro-image
```

支持的 API 兼容 OpenAI 格式，可使用本地服务 (LocalAI, LM Studio 等) 或在线服务。

## 使用方法

### 三种运行模式

#### 1. 全链路模式 (`--all`)

一键生成并处理，输入 Prompt 直接输出最终资产:

```bash
python main.py --all --prompt "minimalist clock icon, tech startup vibe, blue and white colors" --name mylogo
```

输出:
- `output/mylogo.png` - 512x512 透明背景 Logo
- `output/mylogo_favicon.ico` - 多分辨率 favicon (16x16, 32x32, 48x48, 64x64)

#### 2. 纯生图模式 (`--generate`)

仅生成原始图片，适合批量生成后人工筛选:

```bash
python main.py --generate --prompt "abstract geometric letter M, corporate style" --name logo_v1
```

输出:
- `assets/logo_v1_raw.png` - AI 生成的原始图片

#### 3. 纯处理模式 (`--process`)

处理已有的本地图片，适合手动修改后的原图:

```bash
python main.py --process --input assets/logo_v1_raw.png --name final_logo
```

输出:
- `output/final_logo.png`
- `output/final_logo_favicon.ico`

### 命令行参数

| 参数 | 必需 | 说明 |
|------|------|------|
| `--generate` | 是 (三选一) | 仅生成图片 |
| `--process` | 是 (三选一) | 仅处理图片 |
| `--all` | 是 (三选一) | 生成并处理 |
| `--prompt` | 生成模式必需 | 文本提示词 |
| `--input` | 处理模式必需 | 输入图片路径 |
| `--name` | 否 | 输出文件名 (默认: logo) |

## 目录结构

```
free-logo-marker/
├── app/
│   ├── generate_logo.py    # 图像生成模块
│   └── process_logo.py     # 图像处理模块
├── assets/                  # AI 生成的原始图片
├── output/                  # 处理后的最终资产
├── main.py                  # CLI 入口
├── pyproject.toml           # 项目配置
├── .env.example             # 环境变量模板
└── .env                     # 环境变量配置
```

## 注意事项

### 首次运行

`rembg` 首次执行时会自动下载约 170MB 的模型权重文件到 `~/.u2net/` 目录。下载过程中程序会显示提示，请耐心等待。

### Prompt 建议

为获得最佳去背景效果，系统会自动在 Prompt 中添加风格要求:
- 扁平化 2D 矢量风格
- 纯色背景 (白色)
- 无阴影
- 高对比度

建议在输入 Prompt 时专注于 Logo 的主题和风格描述。

## 许可证

MIT License
