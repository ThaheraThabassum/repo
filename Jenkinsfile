pipeline {
    agent any

    environment {
        SOURCE_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        TARGET_REPO = 'git@github.com:ThaheraThabassum/testing.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'destination-branch'
        SSH_KEY = 'jenkins-ssh-key1'
    }

    stages {
        stage('Setup SSH Key') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: SSH_KEY, keyFileVariable: 'SSH_KEY_FILE')]) {
                        sh '''
                            mkdir -p ~/.ssh
                            cp $SSH_KEY_FILE ~/.ssh/id_rsa
                            chmod 600 ~/.ssh/id_rsa
                            ssh-keyscan github.com >> ~/.ssh/known_hosts
                        '''
                    }
                }
            }
        }

        stage('Checkout Source Repo') {
            steps {
                script {
                    sh 'rm -rf source-repo'
                    sh "git clone --depth=1 --branch ${SOURCE_BRANCH} ${SOURCE_REPO} source-repo"
                    sh "ls -l source-repo" // Debug output: list files in source repo
                }
            }
        }

        stage('Prepare Target Repo') {
            steps {
                script {
                    sh 'rm -rf target-repo'
                    sh "git clone --depth=1 ${TARGET_REPO} target-repo || true"

                    dir('target-repo') {
                        def branchExists = sh(script: "git ls-remote --heads ${TARGET_REPO} ${TARGET_BRANCH} | wc -l", returnStdout: true).trim()

                        if (branchExists == '0') {
                            echo "Branch ${TARGET_BRANCH} does not exist in target repo. Creating..."
                            sh "git checkout -b ${TARGET_BRANCH}"
                            sh "touch .gitkeep"
                            sh "git add .gitkeep"
                            sh "git commit -m 'Initial commit to create branch'"
                            sh "git push origin ${TARGET_BRANCH}"
                        } else {
                            sh "git checkout ${TARGET_BRANCH}"
                            sh "git pull origin ${TARGET_BRANCH}"
                        }
                    }
                }
            }
        }

        stage('Read File List & Copy Files') {
            steps {
                script {
                    def fileListPath = 'source-repo/file_list.txt'
                    def filesToCopy = sh(script: "cat ${fileListPath}", returnStdout: true).trim().split("\n")

                    echo "Contents of file_list.txt: ${filesToCopy}" // Debug output

                    for (file in filesToCopy) {
                        echo "Copying source-repo/${file} to target-repo/" // Debug output
                        sh "cp -r source-repo/${file} target-repo/"
                    }
                }
            }
        }

        stage('Commit & Push to Target Repo') {
            steps {
                script {
                    dir('target-repo') {
                        sh "git config user.email 'jenkins@yourdomain.com'"
                        sh "git config user.name 'Jenkins CI'"
                        sh "git add ."
                        sh "git commit -m 'Syncing files from source to target repo' || echo 'No changes to commit'"
                        sh "git push origin ${TARGET_BRANCH}"
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed. Please check logs."
        }
    }
}
