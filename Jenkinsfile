pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'  // Use SSH URL if using SSH authentication
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key'  // The Jenkins credential ID for SSH key
    }
    stages {
        stage('Checkout Source Branch') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    rm -rf repo  # Ensure a clean workspace
                    git clone ${GIT_REPO}
                    cd repo
                    git checkout ${SOURCE_BRANCH}
                    git pull origin ${SOURCE_BRANCH}
                    '''
                }
            }
        }

        stage('Merge and Push to Target Branch') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    cd repo
                    git checkout ${TARGET_BRANCH} || git checkout -b ${TARGET_BRANCH}
                    git pull origin ${TARGET_BRANCH}
                    git merge ${SOURCE_BRANCH} --no-ff -m "Automated merge from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                    
                    # Push the merged changes
                    git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
