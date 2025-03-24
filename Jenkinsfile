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
                    def excelData = readExcel file: LOCAL_EXCEL_FILE
                    excelData.each { row ->
                        def buildName = row[0]  // First column in Excel contains the build name
                        transferBuild(buildName)
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
                        git archive --remote=${env.GIT_REPO} ${env.GIT_BRANCH} ${buildName}.zip | tar -x
                        scp -o StrictHostKeyChecking=no ${buildName}.zip ${env.REMOTE_USER}@${env.REMOTE_HOST}:${env.TARGET_PATH}/
                    """
                }
            }
        }
    }
}
