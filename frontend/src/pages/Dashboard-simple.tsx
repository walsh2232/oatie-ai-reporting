/**
 * Simplified Dashboard Component for Development
 */

import axios from 'axios'
import { useEffect, useState } from 'react'

interface ApiStatus {
    status: string
    oracle_integration: string
    timestamp: string
}

interface OracleFeatures {
    implementation_status: string
    features: Record<string, { status: string }>
}

const Dashboard = () => {
    const [apiStatus, setApiStatus] = useState<ApiStatus | null>(null)
    const [oracleFeatures, setOracleFeatures] = useState<OracleFeatures | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch API health status
                const healthResponse = await axios.get('/api/health')
                setApiStatus(healthResponse.data)

                // Fetch Oracle features
                const featuresResponse = await axios.get('/api/v1/oracle/features')
                setOracleFeatures(featuresResponse.data)
            } catch (error) {
                console.error('Error fetching data:', error)
            } finally {
                setLoading(false)
            }
        }

        fetchData()
    }, [])

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading dashboard...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="p-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">
                    Oatie AI Reporting Platform
                </h1>
                <p className="text-gray-600 mt-2">
                    Oracle BI Publisher Integration Dashboard
                </p>
            </div>

            {/* Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {/* API Status Card */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        API Status
                    </h3>
                    {apiStatus ? (
                        <div className="space-y-2">
                            <div className="flex items-center">
                                <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                                <span className="text-sm text-gray-600">Status: {apiStatus.status}</span>
                            </div>
                            <div className="flex items-center">
                                <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
                                <span className="text-sm text-gray-600">Oracle: {apiStatus.oracle_integration}</span>
                            </div>
                        </div>
                    ) : (
                        <p className="text-red-600">Unable to fetch API status</p>
                    )}
                </div>

                {/* Oracle Integration Card */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        Oracle BI Publisher
                    </h3>
                    {oracleFeatures ? (
                        <div className="space-y-2">
                            <div className="text-sm font-medium text-green-600">
                                {oracleFeatures.implementation_status}
                            </div>
                            <div className="text-xs text-gray-500">
                                {Object.keys(oracleFeatures.features).length} features implemented
                            </div>
                        </div>
                    ) : (
                        <p className="text-red-600">Unable to fetch Oracle status</p>
                    )}
                </div>

                {/* Quick Actions Card */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        Quick Actions
                    </h3>
                    <div className="space-y-2">
                        <button className="w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded">
                            View API Documentation
                        </button>
                        <button className="w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded">
                            Test Oracle Connection
                        </button>
                        <button className="w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded">
                            Generate Report
                        </button>
                    </div>
                </div>
            </div>

            {/* Oracle Features Details */}
            {oracleFeatures && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                    <div className="p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">
                            Oracle BI Publisher Features
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {Object.entries(oracleFeatures.features).map(([key, feature]) => (
                                <div key={key} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                                    <span className="text-sm font-medium text-gray-700 capitalize">
                                        {key.replace(/_/g, ' ')}
                                    </span>
                                    <span className="text-sm text-green-600 font-medium">
                                        {feature.status}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* API Endpoints */}
            <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        Available Endpoints
                    </h3>
                    <div className="space-y-2">
                        <a
                            href="/api/docs"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded border border-blue-200"
                        >
                            📖 Interactive API Documentation (/docs)
                        </a>
                        <a
                            href="/api/health"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded border border-blue-200"
                        >
                            🏥 Health Check (/health)
                        </a>
                        <a
                            href="/api/v1/oracle/features"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded border border-blue-200"
                        >
                            🔧 Oracle Features (/api/v1/oracle/features)
                        </a>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Dashboard
