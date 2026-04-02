import { test, expect } from '@playwright/test'

test.describe('Login', () => {
  test('login page renders correctly', async ({ page }) => {
    await page.goto('/login')
    await expect(page.getByRole('heading', { name: /admin login/i })).toBeVisible()
    await expect(page.getByLabel(/email/i)).toBeVisible()
    await expect(page.getByLabel(/password/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible()
  })

  test('login with invalid credentials shows error', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('wrong@example.com')
    await page.getByLabel(/password/i).fill('wrongpassword')
    await page.getByRole('button', { name: /sign in/i }).click()
    await expect(page.getByText(/invalid email or password/i)).toBeVisible()
  })

  test('login with valid credentials redirects to home', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('admin@gmail.com')
    await page.getByLabel(/password/i).fill('admin123')
    await page.getByRole('button', { name: /sign in/i }).click()
    await page.waitForURL('/', { timeout: 10000 })
    await expect(page).toHaveURL('/')
  })

  test('logout button is visible after login', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('admin@gmail.com')
    await page.getByLabel(/password/i).fill('admin123')
    await page.getByRole('button', { name: /sign in/i }).click()
    await page.waitForURL('/')

    await expect(page.getByRole('button', { name: /logout/i })).toBeVisible()
  })

  test('logout clears session and redirects to login', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('admin@gmail.com')
    await page.getByLabel(/password/i).fill('admin123')
    await page.getByRole('button', { name: /sign in/i }).click()
    await page.waitForURL('/')

    await page.getByRole('button', { name: /logout/i }).click()
    await expect(page).toHaveURL(/\/login/)
  })

  test('authenticated user can access protected routes', async ({ page }) => {
    // Login
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('admin@gmail.com')
    await page.getByLabel(/password/i).fill('admin123')
    await page.getByRole('button', { name: /sign in/i }).click()
    await page.waitForURL('/')

    // Try to access a protected route directly
    await page.goto('/flights')
    await expect(page).toHaveURL(/\/flights/)

    // Try another protected route
    await page.goto('/bookings')
    await expect(page).toHaveURL(/\/bookings/)
  })

  test('unauthenticated user cannot access protected routes', async ({ page }) => {
    await page.goto('/flights')
    await expect(page).toHaveURL(/\/login/)
    await page.goto('/hotels')
    await expect(page).toHaveURL(/\/login/)
    await page.goto('/bookings')
    await expect(page).toHaveURL(/\/login/)
  })
})