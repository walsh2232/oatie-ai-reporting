/**
 * Apollo GraphQL Client Configuration
 * Optimized for enterprise performance with caching and error handling
 */

import { ApolloClient, InMemoryCache, createHttpLink, from } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { onError } from '@apollo/client/link/error'
import { RetryLink } from '@apollo/client/link/retry'

// HTTP link for GraphQL endpoint
const httpLink = createHttpLink({
  uri: '/graphql',
  credentials: 'include',
})

// Authentication link to add JWT token
const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem('access_token')
  
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    }
  }
})

// Error handling link
const errorLink = onError(({ graphQLErrors, networkError, operation, forward }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) => {
      console.error(
        `GraphQL error: Message: ${message}, Location: ${locations}, Path: ${path}`
      )
    })
  }

  if (networkError) {
    console.error(`Network error: ${networkError}`)
    
    // Handle authentication errors
    if ('statusCode' in networkError && networkError.statusCode === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
  }
})

// Retry link for handling temporary failures
const retryLink = new RetryLink({
  delay: {
    initial: 300,
    max: Infinity,
    jitter: true
  },
  attempts: {
    max: 3,
    retryIf: (error, _operation) => !!error
  }
})

// In-memory cache with type policies for optimal performance
const cache = new InMemoryCache({
  typePolicies: {
    Query: {
      fields: {
        users: {
          merge(existing = [], incoming) {
            return [...existing, ...incoming]
          }
        },
        reports: {
          merge(existing = [], incoming) {
            return [...existing, ...incoming]
          }
        },
        queryExecutions: {
          merge(existing = [], incoming) {
            return [...existing, ...incoming]
          }
        }
      }
    }
  }
})

// Create Apollo Client with enterprise configuration
export const apolloClient = new ApolloClient({
  link: from([retryLink, errorLink, authLink, httpLink]),
  cache,
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all',
      fetchPolicy: 'cache-and-network',
    },
    query: {
      errorPolicy: 'all',
      fetchPolicy: 'cache-first',
    },
    mutate: {
      errorPolicy: 'all',
    },
  },
  connectToDevTools: process.env.NODE_ENV === 'development',
})