pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_TO_COPY = "new_testing"  // Change to the exact file/folder you want to copy
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
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}
                    else
                        echo "Cloning repository..."
                        git clone ${GIT_REPO} repo
                        cd repo
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}
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
                    TIMESTAMP=$(date +"%d_%m_%y %H:%M:%S")

                    echo "Checking if ${FILES_TO_COPY} exists..."
                    if [ -e "${FILES_TO_COPY}" ]; then
                        BACKUP_FILE="${FILES_TO_COPY}_${TIMESTAMP}"
                        mv ${FILES_TO_COPY} ${BACKUP_FILE}
                        git add ${BACKUP_FILE}
                        git commit -m "Backup existing ${FILES_TO_COPY} as ${BACKUP_FILE}"
                        git push origin ${TARGET_BRANCH}
                        echo "Backup created: ${BACKUP_FILE}"
                    else
                        echo "No existing file to backup."
                    fi

                    echo "Copying new files from ${SOURCE_BRANCH} to ${TARGET_BRANCH}..."
                    git checkout ${SOURCE_BRANCH} -- ${FILES_TO_COPY}

                    echo "Committing new files..."
                    git add ${FILES_TO_COPY}
                    git commit -m "Copy new ${FILES_TO_COPY} from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"

                    echo "Pushing changes to ${TARGET_BRANCH}..."
                    git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
