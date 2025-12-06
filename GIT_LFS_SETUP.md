# Git LFS 和 GitHub 设置指南

## ✅ 已完成的步骤

1. ✅ Git LFS 已安装并初始化
2. ✅ SSH 密钥已生成
3. ✅ Git 仓库已初始化
4. ✅ .gitattributes 文件已创建（配置了大文件类型）

## 📋 接下来需要完成的步骤

### 步骤 1: 添加 SSH 公钥到 GitHub

SSH 公钥已复制到剪贴板，请按以下步骤操作：

1. 打开浏览器，访问：https://github.com/settings/keys
2. 点击 "New SSH key" 按钮
3. 在 "Title" 中输入一个描述（例如：MacBook Pro）
4. 在 "Key" 中粘贴公钥（已自动复制到剪贴板）
5. 点击 "Add SSH key"

**或者使用命令行验证：**
```bash
ssh -T git@github.com
```
如果看到 "Hi [你的用户名]! You've successfully authenticated..." 就表示成功了。

### 步骤 2: 在 GitHub 上创建 Repository（如果还没有）

1. 访问 https://github.com/new
2. 输入 Repository 名称
3. 选择 Public 或 Private
4. **不要**勾选 "Initialize this repository with a README"
5. 点击 "Create repository"

### 步骤 3: 连接本地仓库到 GitHub

将下面的命令中的 `YOUR_USERNAME` 和 `YOUR_REPO_NAME` 替换为你的实际信息：

```bash
cd /Users/jyunru/Desktop/1206
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
```

### 步骤 4: 添加文件并上传

```bash
# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit with Git LFS"

# 推送到 GitHub（首次推送）
git branch -M main
git push -u origin main
```

## 📝 使用 Git LFS 跟踪大文件

如果你有特定的大文件需要跟踪，可以使用：

```bash
# 跟踪特定文件
git lfs track "*.pkl"
git lfs track "large_file.bin"

# 或者跟踪整个目录
git lfs track "data/*.h5"

# 然后提交 .gitattributes 文件
git add .gitattributes
git commit -m "Configure Git LFS tracking"
```

## 🔍 检查 Git LFS 状态

```bash
# 查看被 LFS 跟踪的文件
git lfs ls-files

# 查看 LFS 配置
git lfs env
```

