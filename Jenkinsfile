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
        stage('Prepare Repository') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    echo "Checking if repository already exists..."
                    if [ -d "repo/.git" ]; then
                        echo "Repository exists. Fetching latest changes..."
                        cd repo
                        git fetch --all
                        git reset --hard  # Reset uncommitted changes
                        git clean -fd     # Remove untracked files
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

        stage('Backup Existing Files (If Present)') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    cd repo
                    git checkout ${TARGET_BRANCH} || git checkout -b ${TARGET_BRANCH}
                    git pull origin ${TARGET_BRANCH} || echo "Target branch not found. Creating it."

                    TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                    echo "Checking files for backup..."
                    for file in ${FILES_TO_COPY}; do
                        if [ -e "$file" ]; then
                            BACKUP_FILE="${file}_$TIMESTAMP"
                            mv "$file" "$BACKUP_FILE"
                            echo "Backup created: $BACKUP_FILE"

                            # Add backup file to Git
                            git add "$BACKUP_FILE"
                            git commit -m "Backup created: $BACKUP_FILE"
                            git push origin ${TARGET_BRANCH}
                        else
                            echo "No existing file found for $file, skipping backup."
                        fi
                    done
                    '''
                }
            }
        }

        stage('Copy Files to Target Branch') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    cd repo
                    git checkout ${TARGET_BRANCH}

                    echo "Copying specific files from ${SOURCE_BRANCH} to ${TARGET_BRANCH}..."
                    git checkout ${SOURCE_BRANCH} -- ${FILES_TO_COPY}

                    echo "Committing changes..."
                    git add ${FILES_TO_COPY}
                    git commit -m "Backup (if exists) & Copy: ${FILES_TO_COPY} from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"

                    echo "Pushing changes to ${TARGET_BRANCH}..."
                    git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
