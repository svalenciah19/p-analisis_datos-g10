param location string
param tags object
param environmentName string
param jobName string
param logAnalyticsName string
param containerImage string
param acrLoginServer string
param jobIdentityId string
param jobIdentityClientId string
param keyVaultName string
param storageBlobEndpoint string
param storageContainerName string

@description('Cron en UTC. 0 12 * * * = 7:00 a.m. hora de Colombia')
param cronExpression string = '0 12 * * *'

var placeholderImage = 'mcr.microsoft.com/k8se/quickstart-jobs:latest'
var isPlaceholder = empty(containerImage)
var effectiveImage = isPlaceholder ? placeholderImage : containerImage
var keyVaultUrl = 'https://${keyVaultName}.vault.azure.net/secrets'

var googleSecrets = [
  { name: 'gdrive-client-id', env: 'GDRIVE_CLIENT_ID' }
  { name: 'gdrive-client-secret', env: 'GDRIVE_CLIENT_SECRET' }
  { name: 'gdrive-refresh-token', env: 'GDRIVE_REFRESH_TOKEN' }
  { name: 'gdrive-folder-id', env: 'GDRIVE_FOLDER_ID' }
]

var plainEnv = [
  { name: 'AZURE_CLIENT_ID', value: jobIdentityClientId }
  { name: 'AZURE_STORAGE_ACCOUNT_URL', value: storageBlobEndpoint }
  { name: 'AZURE_STORAGE_CONTAINER', value: storageContainerName }
]

// Fase 1 (placeholder): sin secretos de Key Vault porque aún no existen
var secretEnv = [for s in googleSecrets: { name: s.env, secretRef: s.name }]
var secrets = [for s in googleSecrets: { name: s.name, keyVaultUrl: '${keyVaultUrl}/${s.name}', identity: jobIdentityId }]

resource workspace 'Microsoft.OperationalInsights/workspaces@2025-02-01' existing = {
  name: logAnalyticsName
}

// Solo plan Consumption: sin workloadProfiles, private endpoints ni mantenimiento planificado (evita el cargo de gestión)
resource environment 'Microsoft.App/managedEnvironments@2025-01-01' = {
  name: environmentName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: workspace.properties.customerId
        sharedKey: workspace.listKeys().primarySharedKey
      }
    }
  }
}

resource job 'Microsoft.App/jobs@2025-01-01' = {
  name: jobName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${jobIdentityId}': {}
    }
  }
  properties: {
    environmentId: environment.id
    configuration: {
      triggerType: 'Schedule'
      replicaTimeout: 900
      replicaRetryLimit: 1
      scheduleTriggerConfig: {
        cronExpression: cronExpression
        parallelism: 1
        replicaCompletionCount: 1
      }
      registries: isPlaceholder ? [] : [
        {
          server: acrLoginServer
          identity: jobIdentityId
        }
      ]
      secrets: isPlaceholder ? [] : secrets
    }
    template: {
      containers: [
        {
          name: 'extraccion'
          image: effectiveImage
          resources: {
            cpu: json('1')
            memory: '2Gi'
          }
          env: isPlaceholder ? plainEnv : concat(plainEnv, secretEnv)
        }
      ]
    }
  }
}

output name string = job.name
output environmentId string = environment.id
