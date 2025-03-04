pipeline {
    agent any
    environment {
        GIT_REPO = 'https://github.com/ThaheraThabassum/repo.git'
        SSH_KEY = 'jenkins-ssh-key'  // The ID you set in Jenkins for SSH key
    }
    stages {
        stage('Checkout Code') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    git clone ${GIT_REPO}
                    cd automate  # Replace with your repo name
                    git checkout repo
                    git pull origin repo
                    '''
                }
            }
        }

        stage('Merge and Push to UAT') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    cd automate  # Replace with your repo name
                    git checkout automate
                    git pull origin automate
                    git merge repo -m "Automated merge from develop to uat"
                    git push origin automate
                    '''
                }
            }
        }
    }
}
