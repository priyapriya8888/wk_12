pipeline {
    agent any
   
    stages {

        stage('Run Selenium Tests with pytest') {
    steps {
        echo "Running Selenium Tests using pytest"

        // Use full Python path to ensure Jenkins recognizes it
        bat '"C:\\Users\\Vishnupriya\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m pip install -r requirements.txt'
        bat '"C:\\Users\\Vishnupriya\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m pytest -v'
    }
}


        stage('Build Docker Image') {
            steps {
                echo "Build Docker Image"
                bat "docker build -t seleniumdemoapp:v1 ."
            }
        }

        stage('Docker Login') {
            steps {
                // ⚠ Tip: Use Jenkins credentials instead of hardcoding password
                bat 'docker login -u vishnupriya68 -p "Shivapriya123@"'
            }
        }

        stage('Push Docker Image to Docker Hub') {
            steps {
                echo "Push Docker Image to Docker Hub"
                bat "docker tag seleniumdemoapp:v1 vishnupriya68/sample1:seleniumtestimage"
                bat "docker push vishnupriya68/sample1:seleniumtestimage"
            }
        }

        stage('Deploy to Kubernetes') { 
            steps { 
                echo "Deploying to Kubernetes cluster"

                // ✅ Add kubeconfig environment variable
                bat '''
                set KUBECONFIG=C:\\Users\\Vishnupriya\\.kube\\config
                kubectl cluster-info
                kubectl apply -f deployment.yaml
                kubectl apply -f service.yaml
                '''
            } 
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Please check the logs.'
        }
    }
}
