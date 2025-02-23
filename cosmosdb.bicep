param accountName string = 'cosmos-${uniqueString(resourceGroup().id)}'

param location string = resourceGroup().location

param databaseName string 

param containerName string

resource account 'Microsoft.DocumentDB/databaseAccounts@2024-11-15' = { 

  name: toLower(accountName)
  location: location
  properties: { 
    enableFreeTier: true
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {defaultConsistencyLevel: 'Session'}
    locations: [{locationName: location}]

  }
}

resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-11-15' = { 
  
  parent: account
  name: databaseName
  properties: { 
    resource: {id: databaseName}
    options: { 
      throughput: 1000
    }
  }
}

resource container 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-11-15' = { 

  parent: database
  name: containerName
  properties: { 
    resource: {
      id: containerName
      partitionKey: {paths: ['/id'], kind: 'Hash'}
      indexingPolicy: { 
        automatic: true
        includedPaths: [{path: '/*'}]
        excludedPaths: [{path: '/"systemMetadata"/*'}]
      }
    }
    options: { 
      throughput: 400
    }
  }
}

output location string = location
output accountName string = account.name
output databaseName string = database.name
output containerName string = container.name
