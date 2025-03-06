pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key'  // Jenkins SSH credentials ID
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

        stage('Merge and Push to Target Branch') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    set -e  # Exit on failure
                    
                    cd repo
                    git fetch --all

                    # Check if TARGET_BRANCH exists
                    if git ls-remote --heads origin ${TARGET_BRANCH} | grep ${TARGET_BRANCH}; then
                        echo "Switching to ${TARGET_BRANCH}..."
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH} --rebase
                    else
                        echo "Target branch does not exist, creating ${TARGET_BRANCH}..."
                        git checkout -b ${TARGET_BRANCH}
                        git push -u origin ${TARGET_BRANCH}
                    fi

                    echo "Merging ${SOURCE_BRANCH} into ${TARGET_BRANCH}..."
                    git merge origin/${SOURCE_BRANCH} --no-ff -m "Automated merge from ${SOURCE_BRANCH} to ${TARGET_BRANCH}" || {
                        echo "Merge conflict detected! Resolving automatically..."
                        git reset --hard origin/${TARGET_BRANCH}
                        exit 1
                    }

                    echo "Pushing changes to ${TARGET_BRANCH}..."
                    git push origin ${TARGET_BRANCH} || {
                        echo "Push failed! Trying with --force..."
                        git push --force origin ${TARGET_BRANCH}
                    }
                    '''
                }
            }
        }
    }
}
