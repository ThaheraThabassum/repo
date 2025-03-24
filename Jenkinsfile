pipeline {
    agent any
    environment {
        WORKSPACE_DIR = "${WORKSPACE}"
        LOCAL_EXCEL_FILE = "${WORKSPACE_DIR}/ui.xlsx"

        SOURCE_REPO = 'git@github.com:algonox/ACE-Camunda-DevOps.git'
        SOURCE_BRANCH = 'kmb_ui'
        SOURCE_REPO_DIR = "${WORKSPACE}/kmb_ui"

        SSH_KEY = 'jenkins-ssh-key1'
        UAT_SSH_KEY = '08cc52e2-f8f2-4479-87eb-f8307f8d23a8'  // UAT SSH Key stored in Jenkins credentials
        REMOTE_USER = 'thahera'
        REMOTE_HOST = '65.1.176.9'
        TARGET_PATH = '/opt/lampp/htdocs_dummy'  // Update this to the actual deployment path
    }
    stages {
        stage('Prepare Source Repository') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "Preparing source repository..."
                        if [ -d "${SOURCE_REPO_DIR}/.git" ]; then
                            echo "Repository exists. Fetching latest changes..."
                            cd ${SOURCE_REPO_DIR}
                            git fetch --all
                            git reset --hard origin/${SOURCE_BRANCH}
                            git clean -fd
                            git checkout ${SOURCE_BRANCH}
                            git pull origin ${SOURCE_BRANCH}
                        else
                            echo "Cloning repository..."
                            git clone --branch ${SOURCE_BRANCH} --depth 1 ${SOURCE_REPO} ${SOURCE_REPO_DIR}
                        fi
                    '''
                }
            }
        }

        stage('Read Excel and Transfer Builds') {
            steps {
                script {
                    def builds = readExcelUsingGroovy(LOCAL_EXCEL_FILE)
                    if (builds.isEmpty()) {
                        error "Excel file is empty or could not be read!"
                    }
                    builds.each { buildName ->
                        transferBuild(buildName)
                    }
                }
            }
        }
    }
}

def readExcelUsingGroovy(filePath) {
    def builds = []
    try {
        def excelFile = new File(filePath)
        if (!excelFile.exists()) {
            error "Excel file not found: ${filePath}"
        }

        def workbook = new org.apache.poi.xssf.usermodel.XSSFWorkbook(new FileInputStream(excelFile))
        def sheet = workbook.getSheetAt(0)  // Read the first sheet

        for (row in sheet.rowIterator()) {
            def buildName = row.getCell(0)?.toString()?.trim()
            if (buildName) {
                builds.add(buildName)
            }
        }
        workbook.close()
    } catch (Exception e) {
        error "Error reading Excel file: ${e.message}"
    }
    return builds
}

def transferBuild(buildName) {
    stage("Transferring ${buildName}") {
        steps {
            sshagent(credentials: [env.UAT_SSH_KEY]) {
                script {
                    sh """
                        set -e
                        echo "Archiving ${buildName} from repository..."
                        cd ${env.SOURCE_REPO_DIR}
                        git archive --format=zip --output=${WORKSPACE}/${buildName}.zip HEAD:${buildName}

                        echo "Transferring ${buildName}.zip to ${env.REMOTE_HOST}..."
                        scp -o StrictHostKeyChecking=no ${WORKSPACE}/${buildName}.zip ${env.REMOTE_USER}@${env.REMOTE_HOST}:${env.TARGET_PATH}/
                        echo "Transfer completed for ${buildName}."
                    """
                }
            }
        }
    }
}
