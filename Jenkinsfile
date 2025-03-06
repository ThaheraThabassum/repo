pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
    }
    stages {
        stage('Clean Workspace') {
            steps {
                echo "Cleaning up previous build data..."
                deleteDir()
            }
        }

        stage('Clone Repository') {
            steps {
                sshagent(['jenkins-ssh-key1']) { // Ensure SSH key is used
                    sh '''
                    echo "Using SSH Key for Git Operations"
                    git clone ${GIT_REPO} repo
                    cd repo

                    echo "Configuring Git User..."
                    git config --global user.email "jenkins@example.com"
                    git config --global user.name "Jenkins CI"

                    echo "Checking out ${SOURCE_BRANCH}..."
                    git checkout ${SOURCE_BRANCH}
                    git pull origin ${SOURCE_BRANCH}
                    '''
                }
            }
        }
    }
}
