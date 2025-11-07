pipeline {
    agent any
    environment {
        HARBOR_URL = "127.0.0.1:8081"  // 使用实际的 Harbor 地址
        HARBOR_PROJECT = "cifar"
        IMAGE_NAME = "${HARBOR_URL}/${HARBOR_PROJECT}/cifar-api"
        IMAGE_TAG = "v${BUILD_NUMBER}"
        KUBECONFIG = credentials('k8s-config')
    }

    stages {
        stage('Build Docker Image') {
            steps {
                echo "🔧 开始构建 CIFAR-10 镜像..."
                script {
                    def dockerContext = '/var/jenkins_home/workspace/CIFAR10-CI-CD-Pipeline'
                    sh "docker build --no-cache -t ${IMAGE_NAME}:${IMAGE_TAG} ${dockerContext}"
                }
            }
        }

        stage('Push to Harbor') {
            steps {
                echo "🚀 推送镜像到 Harbor..."
                withCredentials([usernamePassword(credentialsId: 'harbor-cred', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    sh """
                        docker login ${HARBOR_URL} -u ${USER} -p ${PASS}
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                    """
                }
            }
        }

        stage('Deploy to K8s') {
            steps {
                echo "⚙️ 更新 K8s CIFAR-10 部署（无 YAML 版本）..."
                sh """
                    if kubectl --kubeconfig=${KUBECONFIG} get deployment cifar10-deployment -n default > /dev/null 2>&1; then
                        echo "🔁 检测到现有部署，更新镜像..."
                        kubectl --kubeconfig=${KUBECONFIG} set image deployment/cifar10-deployment cifar10-container=${IMAGE_NAME}:${IMAGE_TAG} -n default
                    else
                        echo "🆕 未检测到部署，创建新的部署..."
                        kubectl --kubeconfig=${KUBECONFIG} create deployment cifar10-deployment --image=${IMAGE_NAME}:${IMAGE_TAG} -n default
                        kubectl --kubeconfig=${KUBECONFIG} expose deployment cifar10-deployment --port=5000 --target-port=5000 --type=NodePort -n default
                    fi
                    echo "✅ 当前镜像版本：${IMAGE_TAG}"
                """
            }
        }

        stage('Verify Deployment') {
            steps {
                echo "🔍 验证新版本部署..."
                sh "kubectl --kubeconfig=${KUBECONFIG} get pods -l app=cifar10-api -o wide || kubectl --kubeconfig=${KUBECONFIG} get pods -n default -o wide"
            }
        }
    }

    post {
        success {
            echo "✅ CIFAR-10 部署更新成功！镜像版本：${IMAGE_TAG}"
        }
        failure {
            echo "❌ 流水线执行失败，请检查 Jenkins 控制台日志。"
        }
    }
}
