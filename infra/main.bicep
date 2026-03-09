@description('The name of the Azure AI DevOps Agent resource.')
param agentName string = 'ai-devops-agent'

@description('The location of the resources.')
param location string = resourceGroup().location

@description('The name of the Azure OpenAI resource.')
param openAiName string = '${agentName}-openai'

@description('The name of the Cosmos DB resource.')
param cosmosDbName string = '${agentName}-cosmos'

@description('The name of the Function App resource.')
param functionAppName string = '${agentName}-func'

resource openAi 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openAiName
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: openAiName
  }
}

resource gptDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openAi
  name: 'gpt-4o'
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-05-13'
    }
  }
}

resource cosmosDb 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: cosmosDbName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
      }
    ]
  }
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: '${replace(agentName, '-', '')}storage'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}

resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: '${agentName}-plan'
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  properties: {
    reserved: true
  }
}

resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'AZURE_OPENAI_ENDPOINT'
          value: openAi.properties.endpoint
        }
        {
          name: 'AZURE_OPENAI_KEY'
          value: openAi.listKeys().key1
        }
        {
          name: 'COSMOS_DB_CONNECTION_STRING'
          value: cosmosDb.listConnectionStrings().connectionStrings[0].connectionString
        }
      ]
    }
  }
}

output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
