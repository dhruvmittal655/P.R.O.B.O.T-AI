# How to Deploy ProBot AI & Index on Google Search Console

Follow this step-by-step guide to get your website live on the internet and indexed by Google for your digital marketing project.

---

## Part 1: Preview the Website Locally on Your Computer

You can test the site right now on your machine:

1. Open your terminal in this workspace.
2. Run this command:
   ```powershell
   python -m http.server 8000 --directory website
   ```
3. Open your browser and go to: **[http://localhost:8000](http://localhost:8000)**
4. You will see the complete working site with the live Wikipedia research extractor, note generator, text export, and technical documentation.

---

## Part 2: Deploy Free to Get a Live HTTPS URL (2 Simple Methods)

### Method A: Netlify Drop (Easiest — No Git required, 60 seconds)
1. Go to **[app.netlify.com/drop](https://app.netlify.com/drop)** (create a free account if you haven't).
2. Open your File Explorer on Windows to:
   `c:\Users\dhruv\.vscode\SmartSearch\`
3. Drag and drop the **`website`** folder directly into the Netlify Drop box in your browser.
4. Netlify will deploy it instantly and give you a free live URL like `https://probot-ai-demo.netlify.app`.
5. Under **Site Configuration > Change site name**, you can customize the subdomain to whatever name you want (e.g., `probot-ai.netlify.app`).

### Method B: Vercel (Fast & Professional)
1. Sign in to **[vercel.com](https://vercel.com)** with your GitHub or email.
2. Click **Add New... > Project**.
3. Import your GitHub repository, set the **Root Directory** to `website`, and click **Deploy**.
4. You will receive an instant live URL like `https://probot-ai.vercel.app`.

---

## Part 3: Verify & Index with Google Search Console (GSC)

Once your website is live on Netlify or Vercel:

1. Go to **[Google Search Console](https://search.google.com/search-console)** and sign in with your Google account.
2. In the top-left dropdown, click **Add Property**.
3. Choose **URL prefix** (on the right) and paste your live URL (e.g. `https://your-site-name.netlify.app/`).
4. Click **Continue**.
5. Google will show multiple verification methods:
   - Select **HTML tag** (under *Other verification methods*).
   - Google will show a code snippet:
     `<meta name="google-site-verification" content="XYZ_YOUR_CODE_123" />`
   - Copy the string inside `content="..."`.
6. Open `website/index.html` on line 17 and replace `PASTE_YOUR_GSC_VERIFICATION_CODE_HERE` with your actual code.
7. Save and re-deploy (or drag the updated folder into Netlify / push to GitHub).
8. Go back to Google Search Console and click **Verify**.
9. **You will see a green checkmark: "Ownership Verified"!**

---

## Part 4: Submit Sitemap & Request Fast Crawling

1. In the Google Search Console sidebar, click **Sitemaps**.
2. Under "Add a new sitemap", type:
   `sitemap.xml`
3. Click **Submit**. Google will read all pages and mark status as **Success**.
4. To accelerate indexing for your project grading:
   - Paste your homepage URL `https://your-site-name.netlify.app/` into the top search bar ("Inspect any URL in...").
   - Click **Request Indexing**.
   - Do the same for your docs page.
   - Googlebot will prioritize crawling and indexing your site within 24–48 hours.

---

## Part 5: Google Analytics 4 (For Digital Marketing Grading)

1. Go to **[analytics.google.com](https://analytics.google.com)** and create a free Property named "ProBot AI".
2. Select **Web** data stream and enter your URL.
3. Copy your Measurement ID (e.g. `G-XXXXXXXXXX`).
4. Paste the standard Google Tag script into the `<head>` of your HTML files.
5. You can now take real screenshots of live visitor traffic, click events, and user demographics for your project presentation.
