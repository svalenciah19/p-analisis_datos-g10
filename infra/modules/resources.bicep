// Orquesta todos los módulos dentro del resource group. Los nombres vienen del plan (prepare-plan.json.naming).
param location string
param tags object
param deployerObjectId string
param containerImage string
param githubRepository string
param githubEnvironment string

var names = {
  logAnalytics: 'log-p-analisis-dev-44e9'
  environment: 'cae-p-analisis-dev-44e9'
  job: 'caj-p-analisis-dev-44e9'
  acr: 'crpanalisisdev44e9'
  storage: 'stpanalisisdev44e9'
  keyVault: 'kv-p-analisis-dev-44e9'
  jobIdentity: 'id-p-analisis-dev-44e9'
  githubIdentity: 'id-gh-p-analisis-dev-44e9'
}

module identities './identities.bicep' = {
  name: 'identities'
  params: {
    location: location
    tags: tags
    jobIdentityName: names.jobIdentity
    githubIdentityName: names.githubIdentity
    githubRepository: githubRepository
    githubEnvironment: githubEnvironment
  }
}

module logAnalytics './log-analytics.bicep' = {
  name: 'log-analytics'
  params: {
    name: names.logAnalytics
    location: location
    tags: tags
  }
}

module acr './container-registry.bicep' = {
  name: 'container-registry'
  params: {
    name: names.acr
    location: location
    tags: tags
  }
}

module storage './storage.bicep' = {
  name: 'storage'
  params: {
    name: names.storage
    location: location
    tags: tags
  }
}

module keyVault './key-vault.bicep' = {
  name: 'key-vault'
  params: {
    name: names.keyVault
    location: location
    tags: tags
  }
}

module roles './role-assignments.bicep' = {
  name: 'role-assignments'
  params: {
    acrName: acr.outputs.name
    keyVaultName: keyVault.outputs.name
    storageName: storage.outputs.name
    jobIdentityPrincipalId: identities.outputs.jobPrincipalId
    githubIdentityPrincipalId: identities.outputs.githubPrincipalId
    deployerObjectId: deployerObjectId
  }
}

module job './container-apps-job.bicep' = {
  name: 'container-apps-job'
  params: {
    location: location
    tags: tags
    environmentName: names.environment
    jobName: names.job
    logAnalyticsName: logAnalytics.outputs.name
    containerImage: containerImage
    acrLoginServer: acr.outputs.loginServer
    jobIdentityId: identities.outputs.jobIdentityId
    jobIdentityClientId: identities.outputs.jobClientId
    keyVaultName: keyVault.outputs.name
    storageBlobEndpoint: storage.outputs.blobEndpoint
    storageContainerName: storage.outputs.containerName
  }
  dependsOn: [
    roles
  ]
}

output acrLoginServer string = acr.outputs.loginServer
output acrName string = acr.outputs.name
output jobName string = job.outputs.name
output keyVaultName string = keyVault.outputs.name
output storageBlobEndpoint string = storage.outputs.blobEndpoint
output githubIdentityClientId string = identities.outputs.githubClientId
output jobIdentityClientId string = identities.outputs.jobClientId
