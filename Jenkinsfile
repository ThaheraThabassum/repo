pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'  // Use SSH URL
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key'  // SSH credentials stored in Jenkins
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
                    
                    # Checkout automate branch or create it if not exists
                    if git show-ref --verify --quiet refs/heads/${TARGET_BRANCH}; then
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}
                    else
                        git checkout -b ${TARGET_BRANCH}
                    fi

                    # Merge changes from main to automate
                    git merge ${SOURCE_BRANCH} --no-ff -m "Automated merge from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"

                    # Push changes
                    git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
