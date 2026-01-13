# LinkForge 部署指南

## Linux 服务器部署

### 1. 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libmagic1

# CentOS/RHEL
sudo yum install -y file-libs
```

### 2. 创建虚拟环境并安装依赖

```bash
cd /www/wwwroot/LinkForge

# 创建虚拟环境
python3 -m venv /www/server/pyporject_evn/LinkForge

# 激活虚拟环境
source /www/server/pyporject_evn/LinkForge/bin/activate

# 安装基础依赖
pip install -r requirements.txt

# 安装 python-magic (Linux 版本)
pip install python-magic==0.4.27
```

### 3. 配置环境变量

创建 `.env` 文件:

```bash
cp .env.example .env
nano .env
```

修改以下配置:

```env
BASE_URL=http://your-domain.com  # 修改为你的域名
UPLOAD_DIR=uploads
MAX_FILE_SIZE=104857600
DOWNLOAD_TIMEOUT=30
```

### 4. 创建上传目录

```bash
mkdir -p uploads
chmod 755 uploads
```

### 5. 启动服务

#### 使用 Uvicorn (开发/测试)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 使用 Uvicorn + 多进程 (生产环境)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 使用 Gunicorn + Uvicorn Workers (推荐生产环境)

```bash
# 安装 gunicorn
pip install gunicorn

# 启动服务
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 6. 使用 Systemd 管理服务

创建服务文件 `/etc/systemd/system/linkforge.service`:

```ini
[Unit]
Description=LinkForge API Service
After=network.target

[Service]
Type=notify
User=www
Group=www
WorkingDirectory=/www/wwwroot/LinkForge
Environment="PATH=/www/server/pyporject_evn/LinkForge/bin"
ExecStart=/www/server/pyporject_evn/LinkForge/bin/gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
sudo systemctl daemon-reload
sudo systemctl start linkforge
sudo systemctl enable linkforge
sudo systemctl status linkforge
```

### 7. Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /files/ {
        alias /www/wwwroot/LinkForge/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

重启 Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Windows 服务器部署

### 1. 安装依赖

```powershell
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装 python-magic-bin (Windows 版本)
pip install python-magic-bin==0.4.14
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置。

### 3. 启动服务

```powershell
# 开发模式
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Docker 部署

### 1. 创建 Dockerfile

```dockerfile
FROM python:3.12-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir python-magic==0.4.27

# 复制应用代码
COPY . .

# 创建上传目录
RUN mkdir -p uploads

EXPOSE 8000

# 启动应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  linkforge:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./.env:/app/.env
    restart: unless-stopped
    environment:
      - BASE_URL=http://your-domain.com
```

### 3. 启动服务

```bash
docker-compose up -d
```

## 故障排除

### 问题: ModuleNotFoundError: No module named 'magic'

**解决方案:**

1. **Linux 系统:**
   ```bash
   # 安装系统依赖
   sudo apt-get install libmagic1
   
   # 安装 Python 包
   pip install python-magic==0.4.27
   ```

2. **Windows 系统:**
   ```powershell
   pip install python-magic-bin==0.4.14
   ```

3. **如果不需要 MIME 类型检测:**
   
   系统已经做了降级处理,即使不安装 `python-magic`,服务仍可正常运行,只是会依赖文件扩展名和 Content-Type 头来识别文件格式。

### 问题: 上传文件失败

**检查项:**

1. 确保 `uploads` 目录存在且有写入权限
2. 检查 `MAX_FILE_SIZE` 配置是否合适
3. 如果使用 Nginx,检查 `client_max_body_size` 设置

### 问题: 无法访问直链

**检查项:**

1. 确认 `BASE_URL` 配置正确
2. 检查防火墙是否开放端口
3. 如果使用 Nginx,检查静态文件配置

## 性能优化建议

1. **使用多进程/多线程**
   ```bash
   uvicorn main:app --workers 4
   ```

2. **启用 CDN**
   
   将上传的文件托管到 CDN 以提高访问速度。

3. **使用对象存储**
   
   对于大规模部署,建议使用阿里云 OSS、腾讯云 COS 或 AWS S3。

4. **添加缓存**
   
   使用 Redis 缓存文件元数据。

5. **限流保护**
   
   使用 Nginx 或中间件添加请求频率限制。
