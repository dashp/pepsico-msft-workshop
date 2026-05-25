// Key Vault for per-team secrets (AOAI endpoint/key, SQL fqdn, AML shared keys).

param team string
param location string
param tenantId string
param adminObjectId string
param tags object

var kvName = 'kv-pepsi-ws-${team}'

resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: kvName
  location: location
  tags: tags
  properties: {
    tenantId: tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enablePurgeProtection: false
    publicNetworkAccess: 'Enabled'
  }
}

// Grant the workshop admin the "Key Vault Administrator" role for management.
resource adminRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: kv
  name: guid(kv.id, adminObjectId, 'kv-admin')
  properties: {
    principalId: adminObjectId
    principalType: 'User'
    // Key Vault Administrator
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '00482a5a-887f-4fb3-b363-3b7fe8e74483'
    )
  }
}

// Pre-create empty secret slots so the loader scripts don't fail.
// Actual values are set out-of-band by the instructor.
var seedSecrets = [
  'aoai-endpoint'
  'aoai-key'
  'sql-server-fqdn'
  'aml-shared-uri'
  'aml-shared-key'
]

resource secrets 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = [for s in seedSecrets: {
  parent: kv
  name: s
  properties: {
    value: 'PLACEHOLDER'
    attributes: {
      enabled: true
    }
  }
}]

output keyVaultName string = kv.name
output keyVaultUri string = kv.properties.vaultUri
