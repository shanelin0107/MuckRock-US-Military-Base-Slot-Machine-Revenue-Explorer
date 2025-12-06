# 推送到 GitHub 的步骤

## ✅ 已完成
- ✅ Git LFS 已配置
- ✅ 文件已添加并提交
- ✅ 远程仓库已配置：`git@github.com:BU-Spark/ds-muckrock-liberation.git`

## 🔑 步骤 1: 添加 SSH 公钥到 GitHub（必需）

**你的 SSH 公钥：**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIK1gFHaK1ZmzvrznkJWXZz9V8YmeVpo6eWqMS6Y8pZ3d jhuangbp@gmail.com
```

**操作步骤：**
1. 访问：https://github.com/settings/keys
2. 点击 "New SSH key" 按钮
3. Title: 输入 "MacBook Pro" 或任何描述
4. Key: 粘贴上面的公钥
5. 点击 "Add SSH key"

**验证连接：**
```bash
ssh -T git@github.com
```
如果看到 "Hi jhuangbp! You've successfully authenticated..." 就成功了！

## 🚀 步骤 2: 推送到 Team-B-Sprint 分支

添加 SSH 公钥后，运行以下命令：

```bash
cd /Users/jyunru/Desktop/1206
export PATH="$HOME/bin:$PATH"

# 推送到 Team-B-Sprint 分支
git push -u origin main:Team-B-Sprint
```

或者如果你想先切换到 Team-B-Sprint 分支：

```bash
# 获取远程分支信息
git fetch origin

# 切换到 Team-B-Sprint 分支（如果存在）
git checkout -b Team-B-Sprint origin/Team-B-Sprint

# 或者创建新分支并推送
git checkout -b Team-B-Sprint
git push -u origin Team-B-Sprint
```

## 📝 当前提交的文件
- `.gitattributes` - Git LFS 配置文件
- `[Model]_Model_1_20251205_Version_2.ipynb` - 模型文件（已用 Git LFS 跟踪）
- `GIT_LFS_SETUP.md` - 设置文档

## 🔍 检查 Git LFS 状态
```bash
git lfs ls-files  # 查看被 LFS 跟踪的文件
git lfs env       # 查看 LFS 环境配置
```

