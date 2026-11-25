param location string
param tags object
param jobIdentityName string
param githubIdentityName string
param githubRepository string
param githubEnvironment string

resource jobIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: jobIdentityName
  location: location
  tags: tags
}

resource githubIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: githubIdentityName
  location: location
  tags: tags
}

// Permite que GitHub Actions (entorno indicado) obtenga tokens de Azure sin secretos almacenados
resource githubFederation 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2023-01-31' = {
  parent: githubIdentity
  name: 'github-${githubEnvironment}'
  properties: {
    issuer: 'https://token.actions.githubusercontent.com'
    subject: 'repo:${githubRepository}:environment:${githubEnvironment}'
    audiences: [
      'api://AzureADTokenExchange'
    ]
  }
}

output jobIdentityId string = jobIdentity.id
output jobPrincipalId string = jobIdentity.properties.principalId
output jobClientId string = jobIdentity.properties.clientId
output githubPrincipalId string = githubIdentity.properties.principalId
output githubClientId string = githubIdentity.properties.clientId
