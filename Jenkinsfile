pipeline {
    agent any

    environment {
        TARGET_BRANCH = "test"
        TARGET_REPO = "git@github.com:ThaheraThabassum/testing.git"
        SOURCE_REPO = "git@github.com:ThaheraThabassum/repo.git"
    }

    stages {
        stage('Setup SSH Key') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: 'your-ssh-key-id', keyFileVariable: 'SSH_KEY_FILE')]) {
                        sh '''
                            mkdir -p /var/lib/jenkins/.ssh
                            cp $SSH_KEY_FILE /var/lib/jenkins/.ssh/id_rsa
                            chmod 600 /var/lib/jenkins/.ssh/id_rsa
                            ssh-keyscan github.com >> /var/lib/jenkins/.ssh/known_hosts
                        '''
                    }
                }
            }
        }

        stage('Checkout Source Repo') {
            steps {
                script {
                    sh '''
                        rm -rf source-repo
                        git clone --depth=1 --branch main $SOURCE_REPO source-repo
                    '''
                }
            }
        }

        stage('Prepare Target Repo') {
            steps {
                script {
                    sh '''
                        rm -rf target-repo
                        git clone --depth=1 $TARGET_REPO target-repo
                        cd target-repo

                        # Check if the branch exists, if not create it
                        if git ls-remote --heads origin $TARGET_BRANCH | grep $TARGET_BRANCH; then
                            echo "Branch $TARGET_BRANCH exists. Checking it out..."
                            git checkout $TARGET_BRANCH
                        else
                            echo "Branch $TARGET_BRANCH does not exist. Creating it..."
                            git checkout -b $TARGET_BRANCH
                            git push origin $TARGET_BRANCH
                        fi
                    '''
                }
            }
        }

        stage('Read File List & Copy Files') {
            steps {
                script {
                    sh '''
                        cd source-repo
                        FILES=$(ls)
                        cd ../target-repo

                        for FILE in $FILES; do
                            cp -r ../source-repo/$FILE .
                        done
                    '''
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
                        git push origin $TARGET_BRANCH
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
            echo "Pipeline failed. Please check logs."
        }
    }
}
