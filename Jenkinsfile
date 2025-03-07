pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_TO_COPY = "new_testing"  // Change this to the exact file/folder name
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
                    TIMESTAMP=$(date +%d%m%y)

                    echo "Checking if ${FILES_TO_COPY} exists in automate branch..."
                    if [ -e "${FILES_TO_COPY}" ]; then
                        BACKUP_FILE="${FILES_TO_COPY}_backup_${TIMESTAMP}"
                        mv ${FILES_TO_COPY} ${BACKUP_FILE}
                        git add ${BACKUP_FILE}
                        git commit -m "Backup existing ${FILES_TO_COPY} as ${BACKUP_FILE}"
                        git push origin ${TARGET_BRANCH}
                        echo "Backup created: ${BACKUP_FILE}"
                    else
                        echo "No existing file to backup."
                    fi

                    echo "Fetching latest changes from ${SOURCE_BRANCH}..."
                    git checkout ${SOURCE_BRANCH}
                    git pull origin ${SOURCE_BRANCH} --rebase

                    echo "Checking if ${FILES_TO_COPY} exists in ${SOURCE_BRANCH}..."
                    if [ -e "${FILES_TO_COPY}" ]; then
                        echo "Copying new files from ${SOURCE_BRANCH} to ${TARGET_BRANCH}..."
                        git checkout ${SOURCE_BRANCH} -- ${FILES_TO_COPY}

                        echo "Switching to ${TARGET_BRANCH}..."
                        git checkout ${TARGET_BRANCH}

                        echo "Staging copied files..."
                        git add ${FILES_TO_COPY}
                        git status  # Debugging step

                        echo "Checking for changes..."
                        git diff --cached --exit-code || CHANGES="yes"

                        if [ "$CHANGES" = "yes" ]; then
                            git commit -m "Copy new ${FILES_TO_COPY} from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                            echo "Pushing changes to ${TARGET_BRANCH}..."
                            git push origin ${TARGET_BRANCH}
                        else
                            echo "No new changes detected. Skipping commit."
                        fi
                    else
                        echo "File ${FILES_TO_COPY} does not exist in ${SOURCE_BRANCH}. Skipping copy."
                    fi
                    '''
                }
            }
        }
    }
}
