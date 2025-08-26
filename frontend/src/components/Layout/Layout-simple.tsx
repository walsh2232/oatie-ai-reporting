/**
 * Simplified Layout Component for Development
 */

import { Link, Outlet, useLocation } from 'react-router-dom'

const Layout = () => {
    const location = useLocation()

    const navigation = [
        { name: 'Dashboard', href: '/' },
        { name: 'Reports', href: '/reports' },
        { name: 'Analytics', href: '/analytics' },
        { name: 'Settings', href: '/settings' },
    ]

    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Sidebar */}
            <nav className="w-64 bg-white shadow-sm border-r border-gray-200">
                <div className="p-6">
                    <h1 className="text-xl font-bold text-gray-900">
                        Oatie AI Platform
                    </h1>
                    <p className="text-sm text-gray-600 mt-1">
                        Oracle BI Publisher Integration
                    </p>
                </div>

                <ul className="space-y-1 px-3">
                    {navigation.map((item) => (
                        <li key={item.name}>
                            <Link
                                to={item.href}
                                className={`
                  flex items-center px-3 py-2 text-sm font-medium rounded-md
                  ${location.pathname === item.href
                                        ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                                        : 'text-gray-700 hover:bg-gray-100'
                                    }
                `}
                            >
                                {item.name}
                            </Link>
                        </li>
                    ))}
                </ul>
            </nav>

            {/* Main content */}
            <main className="flex-1 overflow-hidden">
                <div className="h-full">
                    <Outlet />
                </div>
            </main>
        </div>
    )
}

export default Layout
