

---

# 🤖 OpenSource AI Tool

![Project Banner](https://raw.githubusercontent.com/Laszlobeer/Dungeo_ai_lan_play/main/yyqWt5B%20-%20Imgur.png)

## 🌟 What is This Project?

**OpenSource AI Dungeon Adventure** is a free and open-source interactive text adventure project with **AI-generated storytelling** and optional **AllTalk TTS narration support**.

Created with ❤️ for all ages, this project lets you explore, role-play, and create your own story-driven adventure using AI.

> 🛑 **Notice**: This software is free for **personal and educational use only**.
> If you **use it commercially** or **integrate it into monetized/restricted systems**,
> **YOU MUST CREDIT THE ORIGINAL AUTHOR.**

---

## ⚙️ Requirements

* 🐍 Python `3.10`
* 📦 [uv](https://docs.astral.sh/uv/) (fast Python package installer and project manager)
* 🦙 [Ollama](https://ollama.com/) (for local AI model inference)
* 🧠 [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit) (for GPU acceleration)
* 🧰 git (optional but helpful)
* 🎤 (optional) [AllTalk TTS](https://github.com/erew123/alltalk_tts) for narrated voice output

---

## 📦 Installation

### 1️⃣ Install uv (if not already installed)

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip (slower)
pip install uv
```

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/Laszlobeer/Dungeo_ai.git
cd Dungeo_ai
```

### 3️⃣ Install Dependencies with uv

```bash
uv sync
```

This will automatically:

* Download and use Python 3.10.19
* Create a virtual environment in `.venv/`
* Install all required dependencies

> 💡 The project is configured to use Python 3.10.19 specifically. uv will download it automatically if not available on your system.

---

## 🚀 Usage

### 🧪 Start the Adventure

```bash
uv run python main.py
```

**OR** (after the first run, you can also use):

```bash
uv run main.py
```

### 🖥️ 图形界面版本

项目提供两个图形界面版本：

#### GUI 模式
```bash
# 现代化 GUI（推荐）
uv run python gui.py

# 经典 GUI
uv run python dungeonaigui.py
```

**GUI 特性：**
- 🎨 现代化界面设计
- 🎭 多主题支持（深空、赛博霓虹等）
- 🎛️️ 配置保存和加载
- 🔄 自动保存功能
- 🎚️ 实时角色创建
- 📊 进度显示
- 🔊 TTS 语音合成支持

### 🌍 多语言支持

项目支持多种语言：

- **中文（简体）** - 默认语言
- **English** - 英文版本

#### 切换语言

如需切换到英文版本，修改 `main.py` 文件：

```python
# 将这一行
init_localization('zh_CN')

# 改为
init_localization('en')
```

#### 添加新语言

1. 在 `locales/` 目录下创建新的语言文件（如 `fr.yml`）
2. 参考 `zh_CN.yml` 和 `en.yml` 的格式
3. 修改 `main.py` 中的语言代码

**当前翻译内容包括：**
- ✅ 用户界面文本
- ✅ 游戏类型描述（9种类型）
- ✅ 角色起始描述（200+ 个角色）
- ✅ 地城主系统提示
- ✅ 错误和状态消息
- ✅ 游戏命令帮助
- ✅ GUI 界面文本（gui.py 和 dungeonaigui.py）

**GUI 多语言说明：**
- GUI 界面同样支持中文和英文切换
- 修改 `gui.py` 或 `dungeonaigui.py` 中的 `init_localization('zh_CN')` 为 `init_localization('en')` 即可切换语言
- 所有界面元素都会相应切换语言

### 🛠️ Development Tools

This project includes development tools configured with uv:

```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Type check
uv run mypy .

# Install development dependencies
uv sync --dev
```


---

## 💬 Available Commands

```bash
/? or /help       - Show help message  
/censored         - Toggle NSFW/SFW mode  
/redo             - Regenerate last AI response  
/save             - Save the story to adventure.txt  
/load             - Load adventure from adventure.txt  
/change           - Switch to another Ollama model  
/exit             - Exit the game  
```

---

## 📜 License & Credits

🆓 **MIT License** — Free to use, modify, and distribute.

> **If you:**
>
> * Use this commercially 🏢
> * Integrate into a monetized app 💵
> * Publicly modify/fork it
>
> 👉 **You MUST give credit to the original author.**

### ✍️ Example Credit

```
This project is based on OpenSource AI Tool by [Laszlo](https://github.com/Laszlobeer/Dungeo_ai)

