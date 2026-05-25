// PepsiCo x Microsoft Workshop - per-team Day 1 provisioning
// Subscription-scope deployment. Creates a resource group and all per-team resources.

targetScope = 'subscription'

@description('Team identifier, e.g. team01, team02. Lowercase, 3-10 chars.')
@minLength(3)
@maxLength(10)
param team string

@description('Azure region for all resources.')
param location string = 'eastus2'

@description('UPN of the Microsoft Entra admin for the SQL server.')
param aadAdminLogin string

@description('Object ID of the Microsoft Entra admin for the SQL server.')
param aadAdminObjectId string

@description('Tag applied to every resource.')
param tags object = {
  workshop: 'pepsico-msft'
  day: '1'
  team: team
}

var rgName = 'rg-pepsi-ws-${team}'

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgName
  location: location
  tags: tags
}

module storage 'modules/storage.bicep' = {
  name: 'storage-${team}'
  scope: rg
  params: {
    team: team
    location: location
    tags: tags
  }
}

module kv 'modules/keyvault.bicep' = {
  name: 'kv-${team}'
  scope: rg
  params: {
    team: team
    location: location
    tenantId: subscription().tenantId
    adminObjectId: aadAdminObjectId
    tags: tags
  }
}

module sql 'modules/sql.bicep' = {
  name: 'sql-${team}'
  scope: rg
  params: {
    team: team
    location: location
    aadAdminLogin: aadAdminLogin
    aadAdminObjectId: aadAdminObjectId
    tags: tags
  }
}

output resourceGroup string = rg.name
output storageAccount string = storage.outputs.storageAccountName
output keyVault string = kv.outputs.keyVaultName
output sqlServer string = sql.outputs.sqlServerName
output sqlDatabase string = sql.outputs.sqlDatabaseName
