# 百度iCode部署指南

## 📍 项目概述
WordsProject-forstudent 是一个基于Flask的词汇学习Web应用，已在GitHub上托管，现需要在百度iCode上进行部署。

## 🔧 技术栈
- Python 3.8+
- Flask Web框架
- SQLite数据库
- HTML/CSS/JavaScript前端
- Docker容器支持

## 📦 部署到百度iCode步骤

### 1. 准备代码
项目代码已包含：
- 完整的Flask应用结构
- Dockerfile和docker-compose.yml
- requirements.txt依赖文件
- 数据库初始化脚本
- 完整的版权文件(LICENSE, AUTHORS, CREDITS.md)

### 2. 百度iCode配置

#### 2.1 创建新仓库
1. 登录百度iCode (https://icode.baidu.com)
2. 点击"新建项目"
3. 填写项目信息：
   - 项目路径：`personal-code/wordsproject_forstudent`
   - 项目名称：`WordsProject-forstudent`
   - 项目描述：词汇学习Web应用
   - 项目类型：选择**Python Web应用**

#### 2.2 仓库设置
1. 开启Git仓库
2. 配置部署环境：
   - Python版本：3.8+（建议3.11）
   - 开启Web服务功能
   - 配置启动命令：`flask run --host=0.0.0.0 --port=8080`
   - 工作目录：`/opt/wordsproject`

#### 2.3 环境变量（如支持）
```bash
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///data/users.db
```

### 3. 推送代码
如果Git远程已配置，使用：
```bash
git push baidu main
```

如果没有配置，按以下步骤：
```bash
# 重新添加远程仓库
git remote remove baidu  # 如已存在
git remote add baidu https://icode.baidu.com/personal-code/wordsproject_forstudent.git

# 推送代码
git push -u baidu main
```

### 4. 百度iCode特有设置

#### 4.1 构建配置
- **自动构建**：开启（如平台支持）
- **构建命令**：
  ```bash
  pip install -r requirements.txt
  python db_init.py
  ```

#### 4.2 服务发布
- **端口映射**：5000 → 8080
- **访问协议**：HTTP
- **域名绑定**：使用平台提供的临时域名

#### 4.3 数据库配置
由于使用SQLite：
- 需要持久化存储/data目录
- 确保data/users.db可读写

### 5. 验证部署

#### 5.1 健康检查
```bash
curl http://your-icode-domain/health
```
期望返回：`{"status": "healthy"}`

#### 5.2 功能测试
1. 访问主页：检查是否显示"Welcome to WordsProject"
2. 注册功能：测试学生注册流程
3. 登录功能：验证用户登录

### 6. 常见问题

#### 6.1 构建失败
- 检查requirements.txt是否有平台不支持的包
- 确保Python版本满足要求
- 查看构建日志中的具体错误

#### 6.2 运行失败
- 检查环境变量是否正确设置
- 确认端口配置
- 查看应用日志

#### 6.3 数据库问题
- SQLite文件权限问题
- 数据库路径配置错误

### 7. 生产建议

#### 7.1 安全配置
- 使用环境变量存储敏感信息
- 设置强密码策略
- 定期备份数据库

#### 7.2 性能优化
- 启用Gunicorn代替开发服务器
- 配置Nginx反向代理
- 设置静态文件缓存

#### 7.3 监控维护
- 配置错误日志收集
- 设置访问日志
- 定期检查依赖安全更新

### 8. 联系信息

项目作者信息请查看：
- [AUTHORS](AUTHORS) - 作者和责任说明
- [CREDITS.md](CREDITS.md) - 项目贡献者列表
- [LICENSE](LICENSE) - MIT许可证

## 📞 支持
如遇到部署问题，请检查：
1. 构建日志中的详细错误信息
2. 百度iCode官方文档
3. 项目README.md中的快速开始指南
```

## 🚀 快速验证
在本地测试成功后，再部署到百度iCode：
```bash
# 本地测试
flask run
# 访问 http://localhost:5000
```

祝您部署顺利！