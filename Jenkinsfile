pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'  // Branch to copy files from
        TARGET_BRANCH = 'automate'  // Branch to receive files
        SSH_KEY = 'jenkins-ssh-key1'  // Ensure this is the correct SSH credential
        FILES_TO_COPY = "new_testing"  // List of specific files/folders to copy
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

        stage('Copy Specific Files to Target Branch') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    cd repo
                    git checkout ${TARGET_BRANCH}
                    git pull origin ${TARGET_BRANCH}

                    echo "Copying specific files from ${SOURCE_BRANCH} to ${TARGET_BRANCH}..."
                    git checkout ${SOURCE_BRANCH} -- ${FILES_TO_COPY}

                    echo "Committing changes..."
                    git add ${FILES_TO_COPY}
                    git commit -m "Copying specific files from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"

                    echo "Pushing changes to ${TARGET_BRANCH}..."
                    git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
