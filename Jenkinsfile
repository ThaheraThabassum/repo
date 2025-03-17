pipeline {
    agent any

    environment {
        SOURCE_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        TARGET_REPO = 'git@github.com:ThaheraThabassum/testing.git'
        BRANCH_NAME = 'test'  // Target branch to checkout
    }

    stages {
        stage('Setup SSH Key') {
            steps {
                script {
                    sh '''
                        mkdir -p /var/lib/jenkins/.ssh
                        cp $SSH_KEY_FILE /var/lib/jenkins/.ssh/id_rsa
                        chmod 600 /var/lib/jenkins/.ssh/id_rsa
                        ssh-keyscan github.com >> /var/lib/jenkins/.ssh/known_hosts
                    '''
                }
            }
        }

        stage('Checkout Source Repo') {
            steps {
                script {
                    sh '''
                        rm -rf source-repo
                        git clone --depth=1 --branch main ${SOURCE_REPO} source-repo
                    '''
                }
            }
        }

        stage('Checkout Target Repo') {
            steps {
                script {
                    sh 'rm -rf target-repo'
                    sh "git clone --depth=1 ${TARGET_REPO} target-repo"

                    dir('target-repo') {
                        def branchExists = sh(script: "git ls-remote --heads ${TARGET_REPO} ${BRANCH_NAME} | wc -l", returnStdout: true).trim()

                        if (branchExists == '1') {
                            echo "Branch ${BRANCH_NAME} exists. Checking out..."
                            sh "git fetch origin ${BRANCH_NAME}"
                            sh "git checkout -b ${BRANCH_NAME} origin/${BRANCH_NAME}"
                            sh "git pull origin ${BRANCH_NAME}"
                        } else {
                            error "Branch ${BRANCH_NAME} does not exist. Please create it in the target repository."
                        }
                    }
                }
            }
        }

        stage('Read File List & Copy Files') {
            steps {
                script {
                    sh '''
                        cp -r source-repo/* target-repo/
                    '''
                }
            }
        }

        stage('Commit & Push to Target Repo') {
            steps {
                script {
                    dir('target-repo') {
                        sh '''
                            git add .
                            git commit -m "Sync files from source repo"
                            git push origin ${BRANCH_NAME}
                        '''
                    }
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
