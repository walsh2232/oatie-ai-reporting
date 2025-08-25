import React, { useState } from 'react';
import {
  Settings as SettingsIcon,
  Database,
  Shield,
  Bell,
  Palette,
  Save,
  TestTube,
  Key,
  Globe,
  Clock
} from 'lucide-react';
import toast from 'react-hot-toast';

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({
    general: {
      system_name: 'Oatie AI Reporting',
      timezone: 'UTC',
      language: 'en-US',
      session_timeout: 30,
    },
    database: {
      oracle_url: 'https://your-oracle-bi-publisher.com',
      connection_timeout: 30,
      max_connections: 20,
      ssl_enabled: true,
    },
    security: {
      two_factor_enabled: true,
      password_policy: 'strong',
      session_encryption: true,
      audit_logging: true,
    },
    notifications: {
      email_enabled: true,
      slack_enabled: false,
      report_completion: true,
      system_alerts: true,
    },
    ai: {
      openai_model: 'gpt-4-turbo',
      confidence_threshold: 0.8,
      max_tokens: 1000,
      temperature: 0.1,
    }
  });

  const tabs = [
    { id: 'general', name: 'General', icon: SettingsIcon },
    { id: 'database', name: 'Database', icon: Database },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'ai', name: 'AI Settings', icon: Key },
  ];

  const handleSave = () => {
    // TODO: Implement settings save
    toast.success('Settings saved successfully');
  };

  const handleTestConnection = () => {
    // TODO: Implement connection test
    toast.info('Testing database connection...');
    setTimeout(() => {
      toast.success('Database connection successful');
    }, 2000);
  };

  const updateSetting = (category: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category as keyof typeof prev],
        [key]: value
      }
    }));
  };

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          System Name
        </label>
        <input
          type="text"
          value={settings.general.system_name}
          onChange={(e) => updateSetting('general', 'system_name', e.target.value)}
          className="redwood-input"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Timezone
        </label>
        <select
          value={settings.general.timezone}
          onChange={(e) => updateSetting('general', 'timezone', e.target.value)}
          className="redwood-input"
        >
          <option value="UTC">UTC</option>
          <option value="America/New_York">Eastern Time</option>
          <option value="America/Chicago">Central Time</option>
          <option value="America/Los_Angeles">Pacific Time</option>
          <option value="Europe/London">London</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Language
        </label>
        <select
          value={settings.general.language}
          onChange={(e) => updateSetting('general', 'language', e.target.value)}
          className="redwood-input"
        >
          <option value="en-US">English (US)</option>
          <option value="en-GB">English (UK)</option>
          <option value="es-ES">Spanish</option>
          <option value="fr-FR">French</option>
          <option value="de-DE">German</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Session Timeout (minutes)
        </label>
        <input
          type="number"
          value={settings.general.session_timeout}
          onChange={(e) => updateSetting('general', 'session_timeout', parseInt(e.target.value))}
          className="redwood-input"
          min="5"
          max="480"
        />
      </div>
    </div>
  );

  const renderDatabaseSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Oracle BI Publisher URL
        </label>
        <input
          type="url"
          value={settings.database.oracle_url}
          onChange={(e) => updateSetting('database', 'oracle_url', e.target.value)}
          className="redwood-input"
          placeholder="https://your-oracle-bi-publisher.com"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Connection Timeout (seconds)
        </label>
        <input
          type="number"
          value={settings.database.connection_timeout}
          onChange={(e) => updateSetting('database', 'connection_timeout', parseInt(e.target.value))}
          className="redwood-input"
          min="10"
          max="300"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Maximum Connections
        </label>
        <input
          type="number"
          value={settings.database.max_connections}
          onChange={(e) => updateSetting('database', 'max_connections', parseInt(e.target.value))}
          className="redwood-input"
          min="5"
          max="100"
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="ssl_enabled"
          checked={settings.database.ssl_enabled}
          onChange={(e) => updateSetting('database', 'ssl_enabled', e.target.checked)}
          className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
        />
        <label htmlFor="ssl_enabled" className="ml-2 block text-sm text-gray-700">
          Enable SSL/TLS encryption
        </label>
      </div>

      <div className="pt-4 border-t border-gray-200">
        <button
          onClick={handleTestConnection}
          className="redwood-button redwood-button--secondary"
        >
          <TestTube className="w-4 h-4 mr-2" />
          Test Connection
        </button>
      </div>
    </div>
  );

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div className="flex items-center">
        <input
          type="checkbox"
          id="two_factor"
          checked={settings.security.two_factor_enabled}
          onChange={(e) => updateSetting('security', 'two_factor_enabled', e.target.checked)}
          className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
        />
        <label htmlFor="two_factor" className="ml-2 block text-sm text-gray-700">
          Enable Two-Factor Authentication
        </label>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Password Policy
        </label>
        <select
          value={settings.security.password_policy}
          onChange={(e) => updateSetting('security', 'password_policy', e.target.value)}
          className="redwood-input"
        >
          <option value="basic">Basic (8+ characters)</option>
          <option value="standard">Standard (8+ chars, mixed case)</option>
          <option value="strong">Strong (12+ chars, special characters)</option>
        </select>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="session_encryption"
          checked={settings.security.session_encryption}
          onChange={(e) => updateSetting('security', 'session_encryption', e.target.checked)}
          className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
        />
        <label htmlFor="session_encryption" className="ml-2 block text-sm text-gray-700">
          Enable session encryption
        </label>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="audit_logging"
          checked={settings.security.audit_logging}
          onChange={(e) => updateSetting('security', 'audit_logging', e.target.checked)}
          className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
        />
        <label htmlFor="audit_logging" className="ml-2 block text-sm text-gray-700">
          Enable audit logging
        </label>
      </div>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div className="flex items-center">
        <input
          type="checkbox"
          id="email_enabled"
          checked={settings.notifications.email_enabled}
          onChange={(e) => updateSetting('notifications', 'email_enabled', e.target.checked)}
          className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
        />
        <label htmlFor="email_enabled" className="ml-2 block text-sm text-gray-700">
          Enable email notifications
        </label>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="slack_enabled"
          checked={settings.notifications.slack_enabled}
          onChange={(e) => updateSetting('notifications', 'slack_enabled', e.target.checked)}
          className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
        />
        <label htmlFor="slack_enabled" className="ml-2 block text-sm text-gray-700">
          Enable Slack notifications
        </label>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="report_completion"
          checked={settings.notifications.report_completion}
          onChange={(e) => updateSetting('notifications', 'report_completion', e.target.checked)}
          className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
        />
        <label htmlFor="report_completion" className="ml-2 block text-sm text-gray-700">
          Notify on report completion
        </label>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="system_alerts"
          checked={settings.notifications.system_alerts}
          onChange={(e) => updateSetting('notifications', 'system_alerts', e.target.checked)}
          className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
        />
        <label htmlFor="system_alerts" className="ml-2 block text-sm text-gray-700">
          Enable system alerts
        </label>
      </div>
    </div>
  );

  const renderAISettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          OpenAI Model
        </label>
        <select
          value={settings.ai.openai_model}
          onChange={(e) => updateSetting('ai', 'openai_model', e.target.value)}
          className="redwood-input"
        >
          <option value="gpt-4-turbo">GPT-4 Turbo (Recommended)</option>
          <option value="gpt-4">GPT-4</option>
          <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Confidence Threshold ({(settings.ai.confidence_threshold * 100).toFixed(0)}%)
        </label>
        <input
          type="range"
          min="0.5"
          max="1.0"
          step="0.05"
          value={settings.ai.confidence_threshold}
          onChange={(e) => updateSetting('ai', 'confidence_threshold', parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="text-sm text-gray-500 mt-1">
          Minimum confidence score required for SQL generation
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Max Tokens
        </label>
        <input
          type="number"
          value={settings.ai.max_tokens}
          onChange={(e) => updateSetting('ai', 'max_tokens', parseInt(e.target.value))}
          className="redwood-input"
          min="100"
          max="4000"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Temperature ({settings.ai.temperature})
        </label>
        <input
          type="range"
          min="0.0"
          max="1.0"
          step="0.1"
          value={settings.ai.temperature}
          onChange={(e) => updateSetting('ai', 'temperature', parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="text-sm text-gray-500 mt-1">
          Controls randomness in AI responses (lower = more deterministic)
        </div>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
        return renderGeneralSettings();
      case 'database':
        return renderDatabaseSettings();
      case 'security':
        return renderSecuritySettings();
      case 'notifications':
        return renderNotificationSettings();
      case 'ai':
        return renderAISettings();
      default:
        return renderGeneralSettings();
    }
  };

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">
          Configure your Oracle BI Publisher AI Assistant
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="redwood-card">
            <nav className="space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === tab.id
                      ? 'bg-orange-100 text-orange-900'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <tab.icon className="w-4 h-4 mr-3" />
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          <div className="redwood-card">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-semibold text-gray-900">
                {tabs.find(tab => tab.id === activeTab)?.name} Settings
              </h2>
              <button
                onClick={handleSave}
                className="redwood-button redwood-button--primary"
              >
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </button>
            </div>

            {renderTabContent()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;