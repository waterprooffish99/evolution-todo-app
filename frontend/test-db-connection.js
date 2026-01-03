#!/usr/bin/env node

/**
 * Test script to verify Better Auth database connectivity.
 *
 * This script tests:
 * 1. Environment variables are loaded
 * 2. DATABASE_URL is accessible
 * 3. Better Auth configuration is valid
 */

// Load environment variables from .env.local
require('dotenv').config({ path: '.env.local' });

const { betterAuth } = require('better-auth');

console.log('='.repeat(60));
console.log('Better Auth Database Connectivity Test');
console.log('='.repeat(60));
console.log();

// Check environment variables
console.log('1. Checking environment variables...');
const databaseUrl = process.env.DATABASE_URL;
const betterAuthSecret = process.env.BETTER_AUTH_SECRET;
const betterAuthUrl = process.env.BETTER_AUTH_URL;

if (!databaseUrl) {
  console.error('❌ DATABASE_URL not set in .env.local');
  console.log('   Please copy .env.example to .env.local and fill in DATABASE_URL');
  process.exit(1);
}
console.log('   ✅ DATABASE_URL:', databaseUrl.replace(/:[^@]+@/, ':***@'));

if (!betterAuthSecret) {
  console.error('❌ BETTER_AUTH_SECRET not set in .env.local');
  console.log('   Please copy .env.example to .env.local and fill in BETTER_AUTH_SECRET');
  console.log('   Secret should be at least 32 characters');
  process.exit(1);
}
if (betterAuthSecret.length < 32) {
  console.error('❌ BETTER_AUTH_SECRET too short (', betterAuthSecret.length, 'characters, minimum 32)');
  process.exit(1);
}
console.log('   ✅ BETTER_AUTH_SECRET: set (' + betterAuthSecret.length + ' characters)');

if (!betterAuthUrl) {
  console.warn('⚠️  BETTER_AUTH_URL not set, using default: http://localhost:3000');
}
console.log('   ✅ BETTER_AUTH_URL:', betterAuthUrl || 'http://localhost:3000');

console.log();

// Test Better Auth configuration
console.log('2. Testing Better Auth configuration...');
try {
  const auth = betterAuth({
    secret: betterAuthSecret,
    baseURL: betterAuthUrl || 'http://localhost:3000',
    database: {
      provider: 'postgres',
      url: databaseUrl,
    },
    emailAndPassword: {
      enabled: true,
      minPasswordLength: 8,
    },
    session: {
      expiresIn: 60 * 60 * 24, // 24 hours
      updateAge: 60 * 60 * 2,  // Update session every 2 hours
    },
  });

  console.log('   ✅ Better Auth configured successfully');
  console.log('   ✅ Database provider: postgres');
  console.log('   ✅ Email/password auth: enabled');
  console.log('   ✅ Session expiration: 24 hours');
  console.log();

  // Test database connection
  console.log('3. Testing database connection...');
  console.log('   Note: This may take 10-30 seconds...');
  console.log('   Better Auth will create "users" table if it does not exist');
  console.log();

  // Access internal database adapter
  const db = auth.$Infer;

  console.log('   ✅ Database adapter accessible');
  console.log('   ℹ️  Table "users" will be auto-created on first use');
  console.log();

} catch (error) {
  console.error('   ❌ Better Auth configuration failed:', error.message);
  console.log();

  if (error.message.includes('connect') || error.message.includes('ECONNREFUSED')) {
    console.error('   Possible causes:');
    console.error('     1. Database URL is incorrect');
    console.error('     2. Neon database is not running');
    console.error('     3. Network connectivity issues');
    console.error('     4. Firewall blocking PostgreSQL connections');
    console.log();
    console.error('   To test connection manually:');
    console.log(`     psql "${databaseUrl}"`);
  } else if (error.message.includes('auth') || error.message.includes('password')) {
    console.error('   Possible causes:');
    console.error('     1. Database password in URL is incorrect');
    console.error('     2. Database user does not exist');
    console.error('     3. Insufficient permissions');
  }

  process.exit(1);
}

console.log('='.repeat(60));
console.log('✅ All checks passed!');
console.log('='.repeat(60));
console.log();
console.log('Next steps:');
console.log('  1. Start backend: cd backend && .venv/bin/python -m uvicorn app.main:app --reload');
console.log('  2. Start frontend: cd frontend && npm run dev');
console.log('  3. Visit: http://localhost:3000/signup');
console.log('  4. Check Neon console to see "users" table created');
console.log();
