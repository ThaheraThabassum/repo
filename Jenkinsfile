pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_LIST_FILE = "files_to_deploy.txt"
        EXCEL_FILE = "files_to_deploy.xlsx"
        PYTHON_VENV = "venv"
    }
    stages {
        stage('Prepare Repository') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "Checking if repository already exists..."
                        if [ -d "repo/.git" ]; then
                            echo "Repository found. Fetching latest changes..."
                            cd repo
                            git fetch --all
                            git reset --hard
                            git clean -fd
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

        stage('Setup Python Virtual Environment') {
            steps {
                script {
                    sh '''
                        echo "Checking if python3-venv is installed..."
                        if ! dpkg -l | grep -q python3-venv; then
                            echo "python3-venv is missing. Installing..."
                            sudo apt update
                            sudo apt install -y python3-venv
                        fi

                        echo "Creating Python virtual environment..."
                        python3 -m venv ${PYTHON_VENV}
                        source ${PYTHON_VENV}/bin/activate
                        pip install --upgrade pip
                        pip install pandas numpy openpyxl
                    '''
                }
            }
        }

        stage('Extract Deployment List from Excel') {
            steps {
                script {
                    sh '''
                        echo "Extracting deployment list from Excel..."
                        source ${PYTHON_VENV}/bin/activate

                        python3 - <<EOF
import pandas as pd

df = pd.read_excel("${EXCEL_FILE}", engine='openpyxl')
deploy_files = df[df['deploy_or_not'].str.lower() == 'yes']['file/folders path'].dropna()

deploy_files.to_csv("${FILES_LIST_FILE}", index=False, header=False)

print("Deployment list generated: ${FILES_LIST_FILE}")
EOF
                    '''
                }
            }
        }

        stage('Cleanup Python Virtual Environment') {
            steps {
                sh '''
                    echo "Cleaning up virtual environment..."
                    rm -rf ${PYTHON_VENV}
                '''
            }
        }
    }
}
