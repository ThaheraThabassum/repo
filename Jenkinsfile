pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'  // Jenkins SSH credentials ID
    }
    stages {
        stage('Check SSH Credentials') {
            steps {
                script {
                    echo "Checking SSH credentials..."
                    def creds = credentials(SSH_KEY)
                    echo "Using SSH key ID: ${creds}"
                }
            }
        }

        stage('Clone Repository') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    echo "Testing SSH connection..."
                    ssh -o StrictHostKeyChecking=no -T git@github.com
                    
                    echo "Cloning repository..."
                    git clone ${GIT_REPO} repo
                    cd repo
                    git checkout ${SOURCE_BRANCH}
                    git pull origin ${SOURCE_BRANCH}
                    '''
                }
            }
        }
    }
}
