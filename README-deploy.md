# AWS Lambda 部署脚本说明

## 概述

`dev-env-deploy.sh` 脚本用于将 `src/configs/conf.py` 中定义的环境变量配置部署到 AWS Lambda 函数。

## 脚本功能

该脚本会：
1. 读取 `conf.py` 中所有 `os.getenv()` 的默认值
2. 将这些值作为环境变量设置到 AWS Lambda 函数 `ft-gateway-dev-app`
3. 提供成功/失败的反馈信息

## 使用方法

### 基本用法
```bash
./dev-env-deploy.sh
```

### 指定 AWS 账户
```bash
./dev-env-deploy.sh -a your-aws-profile
# 或者
./dev-env-deploy.sh --account your-aws-profile
```

## 环境变量说明

### 基础配置
- `STAGE`: 环境阶段 (dev)
- `TESTING`: 测试模式 (dev)

### 微服务区域主机地址
- `REGION_HOST_AUTH`: 认证服务地址
- `REGION_HOST_MATCH`: 匹配服务地址
- `REGION_HOST_SEARCH`: 搜索服务地址
- `REGION_HOST_MEDIA`: 媒体服务地址
- `REGION_HOST_PAYMENT`: 支付服务地址

### HTTP 连接配置
- `TIMEOUT`: HTTP 超时时间 (10.0秒)
- `MAX_CONNECTS`: 最大连接数 (20)
- `MAX_KEEPALIVE_CONNECTS`: 最大保持连接数 (10)
- `KEEPALIVE_EXPIRY`: 保持连接过期时间 (30.0秒)

### DynamoDB 缓存配置
- `DDB_PREFIX`: DynamoDB 表前缀 (ft_dev_)
- `TABLE_CACHE`: 缓存表名 (cache)
- `DDB_CONNECT_TIMEOUT`: 连接超时 (10秒)
- `DDB_READ_TIMEOUT`: 读取超时 (30秒)
- `DDB_MAX_ATTEMPTS`: 最大重试次数 (5)

### Redis 配置
- `REDIS_HOST`: Redis 主机 (localhost)
- `REDIS_PORT`: Redis 端口 (6379)
- `REDIS_USERNAME`: Redis 用户名 (空)
- `REDIS_PASSWORD`: Redis 密码 (空)

### 探针配置
- `PROBE_CYCLE_SECS`: 探针周期 (3秒)

### JWT 配置
- `JWT_SECRET`: JWT 密钥 (需要设置)
- `JWT_ALGORITHM`: JWT 算法 (HS256)
- `TOKEN_EXPIRE_TIME`: Token 过期时间 (604800秒 = 7天)

### TTL 配置
- `REQUEST_INTERVAL_TTL`: 请求间隔 TTL (20秒)
- `SHORT_TERM_TTL`: 短期 TTL (300秒 = 5分钟)
- `LONG_TERM_TTL`: 长期 TTL (1209600秒 = 14天)
- `STAR_TRACKER_TTL`: 星标追踪 TTL (300秒 = 5分钟)

### 其他配置
- `MAX_TAGS`: 最大标签数 (7)
- `FT_BUCKET`: S3 存储桶 (foreign-teacher)
- `MULTIPART_THRESHOLD`: 多部分上传阈值 (512MB)
- `MAX_CONCURRENCY`: 最大并发数 (10)
- `MULTIPART_CHUNKSIZE`: 多部分上传块大小 (128MB)

### 搜索 URL 路径
- `SEARCH_JOB_URL_PATH`: 工作搜索路径 (/api/v1/search/jobs)
- `SEARCH_RESUME_URL_PATH`: 简历搜索路径 (/api/v1/search/resumes)

### AWS 配置
- `AWS_ACCESS_KEY`: AWS 访问密钥 (需要设置)
- `AWS_SECRET_ACCESS_KEY`: AWS 秘密密钥 (需要设置)

### 申请状态配置
- `MY_STATUS_OF_COMPANY_APPLY`: 公司申请状态 (confirm)
- `STATUS_OF_COMPANY_APPLY`: 公司申请状态 (空)
- `MY_STATUS_OF_COMPANY_REACTION`: 公司反应状态 (confirm,pending)
- `STATUS_OF_COMPANY_REACTION`: 公司反应状态 (confirm)
- `MY_STATUS_OF_TEACHER_APPLY`: 教师申请状态 (confirm)
- `STATUS_OF_TEACHER_APPLY`: 教师申请状态 (空)
- `MY_STATUS_OF_TEACHER_REACTION`: 教师反应状态 (confirm,pending)
- `STATUS_OF_TEACHER_REACTION`: 教师反应状态 (confirm)

## 注意事项

1. **敏感信息**: 以下环境变量需要手动设置，不应使用默认值：
   - `JWT_SECRET`
   - `AWS_ACCESS_KEY`
   - `AWS_SECRET_ACCESS_KEY`
   - `REDIS_USERNAME`
   - `REDIS_PASSWORD`

2. **环境特定配置**: 某些配置可能需要根据实际部署环境进行调整，如：
   - 微服务地址
   - 数据库连接参数
   - 缓存配置

3. **权限要求**: 执行脚本的 AWS 用户需要有更新 Lambda 函数配置的权限。

## 故障排除

如果脚本执行失败，请检查：
1. AWS CLI 是否正确配置
2. 是否有足够的权限更新 Lambda 函数
3. Lambda 函数名称是否正确
4. 网络连接是否正常





