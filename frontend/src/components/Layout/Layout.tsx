/**
 * Main Layout Component with Oracle Redwood Design System Navigation
 * Implements WCAG 2.1 AA accessibility standards
 */

import React from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import {
  HomeIcon,
  DocumentTextIcon,
  CommandLineIcon,
  ChartBarIcon,
  UserGroupIcon,
  CogIcon,
  PowerIcon,
} from '@heroicons/react/24/outline'

import { useAuth } from '../../contexts/AuthContext'

interface NavigationItem {
  name: string
  href: string
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>
  permission?: string
}

const Layout: React.FC = () => {
  const { state, logout, hasPermission } = useAuth()
  const location = useLocation()

  const navigation: NavigationItem[] = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Reports', href: '/reports', icon: DocumentTextIcon, permission: 'reports:read' },
    { name: 'Queries', href: '/queries', icon: CommandLineIcon, permission: 'queries:execute' },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon, permission: 'data:read' },
    { name: 'Users', href: '/users', icon: UserGroupIcon, permission: 'users:manage' },
    { name: 'Settings', href: '/settings', icon: CogIcon },
  ]

  const filteredNavigation = navigation.filter(
    (item) => !item.permission || hasPermission(item.permission)
  )

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Skip to main content link */}
      <a
        href="#main-content"
        className="skip-link focus:top-6"
        aria-label="Skip to main content"
      >
        Skip to main content
      </a>

      {/* Sidebar Navigation */}
      <nav
        className="w-64 bg-white shadow-sm border-r border-gray-200 flex flex-col"
        aria-label="Main navigation"
      >
        {/* Logo and Brand */}
        <div className="flex items-center px-6 py-4 border-b border-gray-200">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">O</span>
            </div>
            <div className="ml-3">
              <h1 className="text-lg font-semibold text-gray-900">Oatie</h1>
              <p className="text-xs text-gray-500">AI Reporting Platform</p>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <div className="flex-1 px-4 py-6">
          <ul className="space-y-2" role="list">
            {filteredNavigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={`group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${
                      isActive
                        ? 'bg-indigo-50 text-indigo-700 border-indigo-700'
                        : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                    aria-current={isActive ? 'page' : undefined}
                  >
                    <item.icon
                      className={`mr-3 h-5 w-5 ${
                        isActive ? 'text-indigo-500' : 'text-gray-400 group-hover:text-gray-500'
                      }`}
                      aria-hidden="true"
                    />
                    {item.name}
                  </Link>
                </li>
              )
            })}
          </ul>
        </div>

        {/* User Profile and Logout */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center mb-3">
            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-gray-700">
                {state.user?.full_name?.[0] || state.user?.username?.[0] || 'U'}
              </span>
            </div>
            <div className="ml-3 flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {state.user?.full_name || state.user?.username}
              </p>
              <p className="text-xs text-gray-500 truncate">{state.user?.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-md hover:bg-gray-50 hover:text-gray-900 transition-colors duration-200"
            aria-label="Sign out of your account"
          >
            <PowerIcon className="mr-3 h-5 w-5 text-gray-400" aria-hidden="true" />
            Sign Out
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden" id="main-content">
        {/* Top Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold text-gray-900">
              {navigation.find((item) => item.href === location.pathname)?.name || 'Dashboard'}
            </h1>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                Welcome, {state.user?.full_name || state.user?.username}
              </span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-auto p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default Layout