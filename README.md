## 项目简介

本项目的核心目标是实现基于 Jenkins 的 AI 模型自动化部署流程，并通过集成 Prometheus 和 Grafana 完成集群资源的实时监控。

项目通过 Jenkins 完成从模型代码提交到 Docker 镜像构建，再到镜像推送至 Harbor 和自动部署到 Kubernetes 集群的全流程自动化。使用 Helm 安装 Prometheus 和 Grafana，实现 Kubernetes 集群的性能监控，实时收集 CPU、内存、Pod 使用情况等指标，帮助分析集群运行状态。

本项目为 AI 平台服务实现了自动化部署和实时监控，确保模型服务在生产环境中的可靠性与可扩展性。


## 系统架构

1. **Docker**：容器化应用程序并推送到 **Harbor** 仓库。
2. **Jenkins**：自动化构建和部署流程，包括 Docker 镜像构建、推送 Harbor、部署 Kubernetes 和触发监控。
3. **Harbor**：容器镜像仓库，主要用来存储和管理和推送 Docker 镜像。
4. **Kubernetes**：托管部署应用并管理其生命周期。
5. **Prometheus + Grafana**：集群监控与资源指标采集，使用 Grafana 展示数据并监控容器资源消耗。

<br>
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/9720ee59-b835-468c-90bf-567f331d16ed" /><br> 
<br> 


## 部署步骤

### 1. 配置 Docker 镜像加速器（可选）


加速 Docker 镜像稳定下载，可以在Docker Desktop设置镜像源

```bash
{
  "registry-mirrors": ["https://<your-mirror-address>"]
}
```

<img width="865" height="308" alt="image" src="https://github.com/user-attachments/assets/f048e577-a2bf-4f52-b045-960e5317fe98" />
<br> 

### 2. 安装 Jenkins

#### 2.1 通过道客镜像安装 Jenkins

<img width="865" height="320" alt="image" src="https://github.com/user-attachments/assets/01c69e05-5878-4ba9-b789-ff65420961f8" />
<br> 

运行以下命令启动 Jenkins 容器：

```bash

docker run -d \
  --name jenkins \
  --user root \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.kube/config:/root/.kube/config \
  -e JAVA_OPTS="-Dhudson.model.DownloadService.noSignatureCheck=true -Dcom.sun.net.ssl.checkRevocation=false" \
  docker.m.daocloud.io/jenkins/jenkins:lts

```

#### 2.2 获取 Jenkins 初始密码

获取管理员密码以便登录 Jenkins：
```bash
docker exec -it jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```
登录地址：http://localhost:8080

<img width="865" height="26" alt="image" src="https://github.com/user-attachments/assets/59d3133f-8c46-4c6c-9acf-49899bc1a71b" />

<img width="859" height="413" alt="image" src="https://github.com/user-attachments/assets/7c7193ae-4a86-4d28-85c5-8b7757d2ebea" />
<br>

#### 2.3 更新插件源

在尝试下载 Jenkins 插件（如 Pipeline 和 Credentials Binding）时，遇到无法下载的情况，可尝试更新 Jenkins 更新源 URL，使用最新的源地址：
```bash
https://updates.jenkins.io/current/update-center.json
```

<img width="865" height="771" alt="image" src="https://github.com/user-attachments/assets/d9ed4db3-205c-4b7e-9275-00452e94fa30" />

<img width="865" height="167" alt="image" src="https://github.com/user-attachments/assets/452edda9-66cb-434c-ad1d-45932d46a37b" />
<br>

### 3. 安装与配置 Harbor

#### 3.1 下载并解压 Harbor 离线安装包
```bash
github.com/goharbor/harbor/releases/tag/v2.14.0
```
<img width="865" height="575" alt="image" src="https://github.com/user-attachments/assets/cbd75427-00a7-4a11-81fe-76cbeebbc21b" />

#### 3.2 配置 Harbor

```bash
hostname: localhost
port: 8081
harbor_admin_password: 11223344
```

<img width="865" height="421" alt="image" src="https://github.com/user-attachments/assets/96a39db5-0ad7-46c6-981d-4cc97ce1ea97" />

<img width="865" height="943" alt="image" src="https://github.com/user-attachments/assets/d87a8c0a-4b7f-40df-ad50-b1278cf996d4" />
<br>
<br>

#### 3.3 安装 Harbor

运行安装脚本：
```bash
sudo ./install.sh
```
<img width="865" height="232" alt="image" src="https://github.com/user-attachments/assets/f48889b9-2c4d-4c0d-9be4-d325f8c350e3" />

<img width="865" height="214" alt="image" src="https://github.com/user-attachments/assets/020a454f-5522-4d46-9800-ef95ccaf4900" />
<br>
<br>

#### 3.4 登录 Harbor

```bash
docker login localhost:8081
```
<img width="865" height="94" alt="image" src="https://github.com/user-attachments/assets/dbc069cc-7dd5-4a10-8ed3-97bd3824af0e" />
<br>
<br>

#### 3.5 推送镜像至 Harbor

打标签并推送镜像：

```bash
docker tag mnist:api-v1 localhost:8081/mnist/mnist-api:v1
docker push localhost:8081/mnist/mnist-api:v1
```

<img width="865" height="208" alt="image" src="https://github.com/user-attachments/assets/aedf3919-3873-4fa1-951e-0bb76e6795f3" />
<br>

登录 http://localhost:8081 验证镜像是否成功推送。

<img width="865" height="413" alt="image" src="https://github.com/user-attachments/assets/25e30580-bad6-4f31-8be7-984c1896a6f1" />
<br>

### 4. Jenkins 与 Harbor、Kubernetes 配置与集成

#### 4.1 配置 Docker 和 Kubernetes 客户端

在 Jenkins 容器中安装 Docker 和 Kubernetes 客户端：

```bash
apt update && apt install -y docker.io
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && mv kubectl /usr/local/bin/
```

<img width="865" height="223" alt="image" src="https://github.com/user-attachments/assets/d4081e98-1f26-451e-b25a-ce1ec8f5b58b" />

<img width="865" height="427" alt="image" src="https://github.com/user-attachments/assets/461d1a68-a945-4180-a73e-18e44726007d" />

<img width="865" height="144" alt="image" src="https://github.com/user-attachments/assets/9a999f82-b6ec-4ba4-a198-c44f6d3889ab" />
<br>
<br>

#### 4.2 配置 Jenkins

在 Jenkins 中添加 Harbor 和 Kubernetes 配置信息：

Harbor 凭证：usernamePassword 类型，配置 Harbor 登录凭证。

Kubernetes 配置：Secret file 类型，上传 .kube/config 配置文件。

<img width="865" height="279" alt="image" src="https://github.com/user-attachments/assets/cb965051-a654-4e43-8c93-911a033a3ea5" />
<br>

凭证验证：

<img width="865" height="796" alt="image" src="https://github.com/user-attachments/assets/1a804e2d-d5ca-4350-a6c7-fea41fc8e102" />
<br>
显示 Harbor 凭证加载成功，并列出 Kubernetes 集群中的节点信息。


#### 4.3 创建 Jenkins Pipeline

将本地的项目文件（如 Dockerfile、应用程序脚本等）复制到 Jenkins 环境的工作空间
```bash
docker cp . jenkins:/var/jenkins_home/workspace/CIFAR10-CI-CD-Pipeline
```
<img width="865" height="72" alt="image" src="https://github.com/user-attachments/assets/73423d0d-2b3d-4a0e-8694-b7a307e1f0dd" />
<img width="865" height="33" alt="image" src="https://github.com/user-attachments/assets/fc202361-a09b-4882-95e3-068217e026bd" />
<br>
Jenkins 自动构建镜像

在 Jenkins Pipeline 中，设置自动构建 Docker 镜像，构建完成后将镜像推送到 Harbor 私有仓库，使用 kubectl 命令部署到 Kubernetes 集群，最后验证 Pod 更新成功

<img width="865" height="666" alt="image" src="https://github.com/user-attachments/assets/c0503d79-3618-4e72-889d-570415200417" />
<img width="865" height="838" alt="image" src="https://github.com/user-attachments/assets/45d79556-765b-4b68-b0d8-db00bded2401" />
<img width="865" height="145" alt="image" src="https://github.com/user-attachments/assets/9cc1bd09-84b2-4905-912f-44c4d8f0c5da" />
<br>

CIFAR-10 项目配置类似的 CI/CD 流程，通过 Jenkins 完成镜像构建、推送到 Harbor、部署到 Kubernetes 并验证更新。

<img width="865" height="548" alt="image" src="https://github.com/user-attachments/assets/a7fcdd1e-79f7-44e7-8d2c-c37f331a220a" />
<br>


### 5. 监控系统（Prometheus + Grafana）

#### 5.1 安装 Helm

安装 Helm 包管理工具：

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```
<img width="865" height="188" alt="image" src="https://github.com/user-attachments/assets/a4dc7c45-ae4a-4c08-bc7e-c1174da40707" />
<br>
<br>

#### 5.2 安装 Prometheus 和 Grafana

通过 Helm 安装 Prometheus 和 Grafana：
```bash
helm install monitor ./kube-prometheus-stack-79.2.0.tgz -n monitor --create-namespace
```
<img width="865" height="550" alt="image" src="https://github.com/user-attachments/assets/fd3d0074-3a4f-4575-9fa2-6cd9d1bbb88b" />
<img width="865" height="500" alt="image" src="https://github.com/user-attachments/assets/fa047fcf-a54f-47b9-bfc3-d50d019a3c52" />
<br>
<br>
#### 5.3 配置 Grafana

登录 Grafana Web 界面：http://localhost:3000，导入 Dashboard ID 13332 以查看 Kubernetes 集群监控数据。
<img width="865" height="201" alt="image" src="https://github.com/user-attachments/assets/05b5256e-cb73-4c90-865b-543f0ed29465" />
<img width="865" height="972" alt="image" src="https://github.com/user-attachments/assets/b0069162-5252-4135-814c-9df0a1f3d94c" />
<img width="865" height="1135" alt="image" src="https://github.com/user-attachments/assets/a92e0ef0-5b48-4e50-acaf-c781ad0cd8ba" />
<br>
<br>
#### 5.4 查询 Prometheus 数据
在 Grafana 中使用 Prometheus 查询语句查看资源使用情况：
```bash
container_cpu_usage_seconds_total{namespace="default"}
```
<img width="865" height="177" alt="image" src="https://github.com/user-attachments/assets/efcfb0ab-9c02-4cb3-9b97-cb3fd213bcb1" />
<img width="865" height="496" alt="image" src="https://github.com/user-attachments/assets/66a00879-e064-4304-b4c2-eb7f636cde5c" />






