import { test, expect } from '@playwright/test'

test.describe('Navigation', () => {
  test('unauthenticated user is redirected to /login', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveURL(/\/login/)
  })

  test('login page renders correctly', async ({ page }) => {
    await page.goto('/login')
    await expect(page.getByRole('heading', { name: /admin login/i })).toBeVisible()
    await expect(page.getByLabel(/email/i)).toBeVisible()
    await expect(page.getByLabel(/password/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible()
  })

  test('home page loads after authentication', async ({ page }) => {
    // Login first
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('admin@gmail.com')
    await page.getByLabel(/password/i).fill('admin123')
    await page.getByRole('button', { name: /sign in/i }).click()
    await page.waitForURL('/')

    // Check home page content
    await expect(page.getByText(/travelbase/i)).toBeVisible()
  })

  test('navigation to Flights page', async ({ page }) => {
    // Login first
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('admin@gmail.com')
    await page.getByLabel(/password/i).fill('admin123')
    await page.getByRole('button', { name: /sign in/i }).click()
    await page.waitForURL('/')

    // Use navbar link specifically
    await page.locator('nav').getByRole('link', { name: /flights/i }).click()
    await expect(page).toHaveURL(/\/flights/)
  })

  test('navigation to Hotels page', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('admin@gmail.com')
    await page.getByLabel(/password/i).fill('admin123')
    await page.getByRole('button', { name: /sign in/i }).click()
    await page.waitForURL('/')

    await page.locator('nav').getByRole('link', { name: /hotels/i }).click()
    await expect(page).toHaveURL(/\/hotels/)
  })

  test('navigation to Activities page', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('admin@gmail.com')
    await page.getByLabel(/password/i).fill('admin123')
    await page.getByRole('button', { name: /sign in/i }).click()
    await page.waitForURL('/')

    await page.locator('nav').getByRole('link', { name: /activities/i }).click()
    await expect(page).toHaveURL(/\/activities/)
  })

  test('navigation to Transport page', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('admin@gmail.com')
    await page.getByLabel(/password/i).fill('admin123')
    await page.getByRole('button', { name: /sign in/i }).click()
    await page.waitForURL('/')

    await page.locator('nav').getByRole('link', { name: /transport/i }).click()
    await expect(page).toHaveURL(/\/transport/)
  })

  test('navigation to Bookings page', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('admin@gmail.com')
    await page.getByLabel(/password/i).fill('admin123')
    await page.getByRole('button', { name: /sign in/i }).click()
    await page.waitForURL('/')

    await page.locator('nav').getByRole('link', { name: /bookings/i }).click()
    await expect(page).toHaveURL(/\/bookings/)
  })

  test('navigation to Support page', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('admin@gmail.com')
    await page.getByLabel(/password/i).fill('admin123')
    await page.getByRole('button', { name: /sign in/i }).click()
    await page.waitForURL('/')

    await page.locator('nav').getByRole('link', { name: /support/i }).click()
    await expect(page).toHaveURL(/\/support/)
  })

  test('support page displays contact information', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('admin@gmail.com')
    await page.getByLabel(/password/i).fill('admin123')
    await page.getByRole('button', { name: /sign in/i }).click()
    await page.waitForURL('/')

    await page.locator('nav').getByRole('link', { name: /support/i }).click()
    await expect(page).toHaveURL(/\/support/)
    await expect(page.getByRole('heading', { name: /support center/i })).toBeVisible()
  })
})