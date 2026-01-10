"use client";

/**
 * Admin Portal Page
 * Main admin dashboard with navigation to admin features
 */

import React from 'react';
import { UserManagement } from '@/components/admin/UserManagement';

export default function AdminPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Admin Portal</h1>

          {/* Admin Navigation */}
          <nav className="mb-6">
            <ul className="flex space-x-4 border-b border-gray-200">
              <li>
                <a
                  href="#users"
                  className="px-4 py-2 text-sm font-medium text-blue-600 border-b-2 border-blue-600"
                >
                  Users
                </a>
              </li>
              <li>
                <a
                  href="#roles"
                  className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700"
                >
                  Roles & Permissions
                </a>
              </li>
              <li>
                <a
                  href="#settings"
                  className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700"
                >
                  Settings
                </a>
              </li>
              <li>
                <a
                  href="#audit"
                  className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700"
                >
                  Audit Logs
                </a>
              </li>
            </ul>
          </nav>

          {/* User Management Section */}
          <section id="users">
            <UserManagement />
          </section>
        </div>
      </div>
    </div>
  );
}


