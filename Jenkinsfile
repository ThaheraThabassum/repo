pipeline {
    agent any

    environment {
        GIT_CREDENTIALS_ID = 'your-git-credentials-id' // Update with Jenkins credentials ID
        SOURCE_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        TARGET_REPO = 'git@github.com:ThaheraThabassum/testing.git'
        BRANCH_NAME = 'main'
    }

    stages {
        stage('Checkout Source Repo') {
            steps {
                script {
                    sh '''
                    rm -rf source-repo
                    git clone --depth=1 --branch $BRANCH_NAME $SOURCE_REPO source-repo
                    '''
                }
            }
        }

        stage('Prepare Target Repo') {
            steps {
                script {
                    sh '''
                    rm -rf target-repo
                    git clone --depth=1 $TARGET_REPO target-repo || {
                        echo "Target repo is empty. Initializing..."
                        git init target-repo
                        cd target-repo
                        git checkout -b $BRANCH_NAME
                        touch .gitkeep
                        git add .gitkeep
                        git commit -m "Initial commit to create branch"
                        git remote add origin $TARGET_REPO
                        git push origin $BRANCH_NAME
                    }
                    '''
                }
            }
        }

        stage('Copy Specific Files/Folders') {
            steps {
                script {
                    def filesToCopy = ['file1.txt', 'file2.txt', 'folder1'] // Modify as needed
                    for (file in filesToCopy) {
                        sh "cp -r source-repo/${file} target-repo/ || echo 'Skipping missing file: ${file}'"
                    }
                }
            }
        }

        stage('Commit & Push to Target Repo') {
            steps {
                script {
                    sh '''
                    cd target-repo
                    git add .
                    git commit -m "Sync files from source repo"
                    git push origin $BRANCH_NAME
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline executed successfully!"
        }
        failure {
            echo "Pipeline failed. Check logs for errors."
        }
    }
}
