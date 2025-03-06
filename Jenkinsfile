pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'  // Ensure this is the correct SSH credential
    }
    stages {
        stage('Clone Repository') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    echo "Cloning repository..."
                    git clone ${GIT_REPO} repo
                    cd repo
                    git checkout ${SOURCE_BRANCH}
                    git pull origin ${SOURCE_BRANCH}
                    '''
                }
            }
        }

        stage('Merge Branches') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    cd repo
                    git checkout -B ${TARGET_BRANCH} origin/${TARGET_BRANCH} || git checkout -b ${TARGET_BRANCH}
                    git merge ${SOURCE_BRANCH} --no-edit
                    git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
