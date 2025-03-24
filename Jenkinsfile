pipeline {
    agent any
    environment {
        WORKSPACE_DIR = "${WORKSPACE}"
        LOCAL_EXCEL_FILE = "${WORKSPACE_DIR}/ui.xlsx"

        GIT_REPO = 'git@github.com:algonox/ACE-Camunda-DevOps.git'
        GIT_BRANCH = 'kmb_ui'

        UAT_SSH_KEY = '08cc52e2-f8f2-4479-87eb-f8307f8d23a8'  // UAT SSH Key stored in Jenkins credentials
        REMOTE_USER = 'thahera'
        REMOTE_HOST = '65.1.176.9'
        TARGET_PATH = '/opt/lampp/htdocs_dummy'  // Update this to the actual deployment path
    }
    stages {
        stage('Read Excel and Transfer Builds') {
            steps {
                script {
                    try {
                        def excelData = readExcel file: LOCAL_EXCEL_FILE
                        if (excelData.isEmpty()) {
                            error "Excel file is empty or couldn't be read!"
                        }
                        excelData.each { row ->
                            def buildName = row[0]?.trim()
                            if (buildName) {
                                transferBuild(buildName)
                            } else {
                                echo "Skipping empty row in Excel."
                            }
                        }
                    } catch (Exception e) {
                        error "Failed to read Excel file: ${e.message}"
                    }
                }
            }
        }
    }
}

def transferBuild(buildName) {
    stage("Transferring ${buildName}") {
        steps {
            sshagent(credentials: [env.UAT_SSH_KEY]) {
                script {
                    sh """
                        set -e
                        echo "Fetching ${buildName}.zip from Git repository..."
                        git archive --format=zip --remote=${env.GIT_REPO} ${env.GIT_BRANCH} ${buildName}.zip -o ${buildName}.zip

                        if [ -f ${buildName}.zip ]; then
                            echo "Transferring ${buildName}.zip to ${env.REMOTE_HOST}..."
                            scp -o StrictHostKeyChecking=no ${buildName}.zip ${env.REMOTE_USER}@${env.REMOTE_HOST}:${env.TARGET_PATH}/
                            echo "Transfer completed for ${buildName}."
                        else
                            echo "Build ${buildName}.zip not found, skipping transfer."
                        fi
                    """
                }
            }
        }
    }
}
