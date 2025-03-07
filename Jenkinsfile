pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_TO_COPY = "new_testing"
    }
    stages {
        stage('Prepare Repository') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    if [ -d "repo/.git" ]; then
                        echo "Repository already exists. Fetching latest changes..."
                        cd repo
                        git reset --hard
                        git clean -fd
                        git fetch --all
                        git checkout ${SOURCE_BRANCH}
                        git pull origin ${SOURCE_BRANCH}
                    else
                        echo "Cloning repository..."
                        git clone ${GIT_REPO} repo
                        cd repo
                        git checkout ${SOURCE_BRANCH}
                        git pull origin ${SOURCE_BRANCH}
                    fi
                    '''
                }
            }
        }

        stage('Backup and Copy Files') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    cd repo
                    git checkout ${TARGET_BRANCH}
                    git pull origin ${TARGET_BRANCH}

                    BACKUP_DIR="backup/${TARGET_BRANCH}_$(date +%Y%m%d%H%M%S)"
                    mkdir -p ${BACKUP_DIR}

                    echo "Backing up existing files..."
                    if [ -e "${FILES_TO_COPY}" ]; then
                        mv ${FILES_TO_COPY} ${BACKUP_DIR}/
                        echo "Backup complete: ${BACKUP_DIR}"
                    fi

                    echo "Copying new files from ${SOURCE_BRANCH} to ${TARGET_BRANCH}..."
                    git checkout ${SOURCE_BRANCH} -- ${FILES_TO_COPY}

                    echo "Committing changes..."
                    git add ${FILES_TO_COPY}
                    git commit -m "Backup old files and copy new files from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"

                    echo "Pushing changes to ${TARGET_BRANCH}..."
                    git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
