param name string
param location string
param tags object

// Los secretos gdrive-* son externos: los escribe scripts/obtener_token_drive.py --keyvault después de la fase 1
resource vault 'Microsoft.KeyVault/vaults@2024-11-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    publicNetworkAccess: 'Enabled'
  }
}

output name string = vault.name
output uri string = vault.properties.vaultUri
