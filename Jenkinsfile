pipeline {
    agent any

    environment {
        GIT_REPO = 'https://github.com/ThaheraThabassum/automate.git'
        SSH_KEY = 'jenkins-ssh-key'
    }

    stages {
        stage('Checkout Develop Branch') {
            steps {
                git branch: 'develop', url: "${GIT_REPO}"
            }
        }

        stage('Merge Develop to UAT') {
            steps {
                script {
                    sshagent(credentials: [SSH_KEY]) {
                        sh '''
                        # Configure Git user if not set
                        git config --global user.email "thahera.t@algonox.com"
                        git config --global user.name "thahera"

                        # Checkout UAT branch
                        git checkout automate || git checkout -b automate

                        # Pull latest changes
                        git pull origin automate

                        # Merge develop into uat
                        git merge develop -m "Automated merge of develop into uat"

                        # Push changes to UAT branch
                        git push origin automate
                        '''
                    }
                }
            }
        }
    }
}
