pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'  // Use SSH URL
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key'  // SSH credentials stored in Jenkins
    }
    stages {
        stage('Clone Repository') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    echo "Cleaning workspace..."
                    rm -rf repo  # Ensure a clean workspace
                    
                    echo "Cloning repository..."
                    git clone ${GIT_REPO} repo
                    cd repo
                    
                    echo "Checking out ${SOURCE_BRANCH}..."
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

                    echo "Fetching all branches..."
                    git fetch --all
                    
                    # Ensure TARGET_BRANCH exists or create it
                    if git show-ref --verify --quiet refs/heads/${TARGET_BRANCH}; then
                        echo "Switching to existing ${TARGET_BRANCH} branch..."
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}
                    else
                        echo "Target branch does not exist, creating ${TARGET_BRANCH}..."
                        git checkout -b ${TARGET_BRANCH}
                    fi

                    echo "Merging ${SOURCE_BRANCH} into ${TARGET_BRANCH}..."
                    git merge ${SOURCE_BRANCH} --no-ff -m "Automated merge from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"

                    echo "Pushing changes to ${TARGET_BRANCH}..."
                    git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
