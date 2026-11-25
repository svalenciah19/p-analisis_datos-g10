targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Prefijo de recursos: {proyecto}-{env}-{sufijo}')
param environmentName string

@minLength(1)
param location string

param sessionId string

param deployedBy string

// Se pasa en main.parameters.json; utcNow() como valor por defecto rompe el blade del portal
param createdAt string

@description('Object ID del usuario que despliega (recibe Key Vault Secrets Officer)')
param deployerObjectId string

@description('Imagen del job. Vacío = imagen placeholder (fase 1)')
param containerImage string = ''

@description('Propietario y repositorio de GitHub con sus IDs inmutables, como aparecen en el subject OIDC')
param githubRepository string = 'svalenciah19@197932907/p-analisis_datos-g10@1445106353'

@description('Entorno de GitHub Actions autorizado por OIDC')
param githubEnvironment string = 'test'

var tags = {
  'app-onboard-skill': 'true'
  'app-onboard-session-id': sessionId
  'created-at': createdAt
  environment: environmentName
  'deployed-by': deployedBy
}

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: tags
}

module resources './modules/resources.bicep' = {
  name: 'resources'
  scope: rg
  params: {
    location: location
    tags: tags
    deployerObjectId: deployerObjectId
    containerImage: containerImage
    githubRepository: githubRepository
    githubEnvironment: githubEnvironment
  }
}

output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_CONTAINER_REGISTRY_LOGIN_SERVER string = resources.outputs.acrLoginServer
output AZURE_CONTAINER_REGISTRY_NAME string = resources.outputs.acrName
output AZURE_JOB_NAME string = resources.outputs.jobName
output AZURE_KEY_VAULT_NAME string = resources.outputs.keyVaultName
output AZURE_STORAGE_BLOB_ENDPOINT string = resources.outputs.storageBlobEndpoint
output GITHUB_AZURE_CLIENT_ID string = resources.outputs.githubIdentityClientId
output JOB_IDENTITY_CLIENT_ID string = resources.outputs.jobIdentityClientId
