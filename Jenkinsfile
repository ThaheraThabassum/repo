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
                deleteDir() // Ensure fresh workspace
            }
        }

        stage('Clone Repository') {
            steps {
                sshagent(['jenkins-ssh-key1']) { // Correct SSH credentials usage
                    sh '''
                    echo "Cloning repository..."
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

        stage('Merge and Push to Target Branch') {
            steps {
                sshagent(['jenkins-ssh-key1']) {
                    sh '''
                    set -e  # Exit if any command fails
                    
                    cd repo
                    git fetch --all

                    # Check if TARGET_BRANCH exists remotely
                    if git branch -r | grep "origin/${TARGET_BRANCH}"; then
                        echo "Switching to ${TARGET_BRANCH}..."
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH} --rebase
                    else
                        echo "Creating and pushing ${TARGET_BRANCH}..."
                        git checkout -b ${TARGET_BRANCH}
                        git push -u origin ${TARGET_BRANCH}
                    fi
                    
                    echo "Merging ${SOURCE_BRANCH} into ${TARGET_BRANCH}..."
                    git merge origin/${SOURCE_BRANCH} --no-ff -m "Automated merge from ${SOURCE_BRANCH} to ${TARGET_BRANCH}" || {
                        echo "Merge conflict detected! Attempting to resolve..."
                        git merge --abort
                        exit 1
                    }
                    
                    echo "Pushing changes to ${TARGET_BRANCH}..."
                    git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
