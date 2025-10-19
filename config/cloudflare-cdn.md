# Cloudflare CDN Setup Guide

## Overview

Cloudflare provides free CDN, caching, and DDoS protection.
This guide shows how to integrate Cloudflare with your Glossary App.

---

## Benefits

✅ **Global CDN** - Serve assets from 200+ locations worldwide
✅ **Free SSL** - Automatic HTTPS with Let's Encrypt
✅ **DDoS Protection** - Built-in protection against attacks
✅ **Caching** - Automatic edge caching for static assets
✅ **Minification** - Auto-minify HTML, CSS, JS
✅ **Brotli Compression** - Better than gzip
✅ **Analytics** - Traffic and performance insights
✅ **Web Application Firewall (WAF)** - Security rules

---

## Setup Steps

### 1. Sign Up for Cloudflare

1. Go to https://cloudflare.com
2. Create free account
3. Add your domain (e.g., yourglossary.com)

### 2. Update Nameservers

Cloudflare will provide nameservers:
```
nameserver1.cloudflare.com
nameserver2.cloudflare.com
```

Update at your domain registrar (GoDaddy, Namecheap, etc.)

**Wait 24-48 hours for DNS propagation**

### 3. Configure DNS Records

In Cloudflare Dashboard → DNS:

```
Type    Name    Content             Proxy Status
A       @       your-server-ip      Proxied (orange cloud)
A       www     your-server-ip      Proxied (orange cloud)
CNAME   api     yourglossary.com    Proxied (orange cloud)
CNAME   cdn     yourglossary.com    Proxied (orange cloud)
```

**Note:** Orange cloud = Proxied through Cloudflare CDN

### 4. Enable SSL/TLS

Dashboard → SSL/TLS:

**Encryption Mode:** Full (strict)
- Encrypts traffic between Cloudflare and your origin server
- Requires valid SSL cert on your server

**Always Use HTTPS:** ON
- Redirects all HTTP to HTTPS

**Automatic HTTPS Rewrites:** ON
- Fixes mixed content warnings

**Minimum TLS Version:** TLS 1.2

### 5. Configure Caching

Dashboard → Caching:

**Caching Level:** Standard

**Browser Cache TTL:** Respect Existing Headers
- Uses Cache-Control headers from your server

**Always Online:** ON
- Serves cached copy if origin is down

### 6. Create Page Rules

Dashboard → Rules → Page Rules:

**Rule 1: Cache Static Assets**
```
URL: *yourglossary.com/assets/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
  - Browser Cache TTL: 1 year
```

**Rule 2: Bypass API Caching**
```
URL: *yourglossary.com/api/*
Settings:
  - Cache Level: Bypass
```

**Rule 3: Cache Search Results (Short TTL)**
```
URL: *yourglossary.com/api/search/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 5 minutes
```

**Rule 4: Force HTTPS**
```
URL: http://*yourglossary.com/*
Settings:
  - Always Use HTTPS: ON
```

### 7. Enable Speed Optimizations

Dashboard → Speed → Optimization:

**Auto Minify:**
- ✅ JavaScript
- ✅ CSS
- ✅ HTML

**Brotli:** ON
- Better compression than gzip

**Rocket Loader:** OFF
- Can break React apps, leave disabled

**Mirage:** ON (Pro plan)
- Lazy loads images

**Polish:** Lossy (Pro plan)
- Optimize images

**HTTP/2:** ON
- Faster protocol

**HTTP/3 (QUIC):** ON
- Experimental, faster

### 8. Configure Firewall Rules

Dashboard → Security → WAF:

**Security Level:** Medium
- Adjust based on attack patterns

**Challenge Passage:** 30 minutes

**Browser Integrity Check:** ON

**Create Custom Rules:**

**Block Malicious Requests:**
```
Expression: (http.request.uri.path contains "../") or (http.request.uri.path contains "etc/passwd")
Action: Block
```

**Rate Limit API:**
```
Expression: http.request.uri.path starts with "/api/"
Action: Rate Limit (100 req/min per IP)
```

### 9. Enable Analytics

Dashboard → Analytics:

**Web Analytics:** ON
- Track visitors, page views, bandwidth

**Performance:** Monitor
- Core Web Vitals
- Page load times
- Time to first byte

---

## Cloudflare Worker (Advanced)

For advanced caching logic, use Cloudflare Workers:

```javascript
// worker.js - Advanced caching for API responses

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)

  // API caching with custom logic
  if (url.pathname.startsWith('/api/glossary')) {
    const cache = caches.default
    const cacheKey = new Request(url.toString(), request)

    // Try cache first
    let response = await cache.match(cacheKey)

    if (!response) {
      // Fetch from origin
      response = await fetch(request)

      // Cache successful GET responses for 5 minutes
      if (request.method === 'GET' && response.status === 200) {
        response = new Response(response.body, response)
        response.headers.set('Cache-Control', 'max-age=300')
        event.waitUntil(cache.put(cacheKey, response.clone()))
      }
    }

    return response
  }

  // Default behavior
  return fetch(request)
}
```

**Deploy:**
```bash
npm install -g wrangler
wrangler login
wrangler init
wrangler publish
```

---

## Testing CDN

### 1. Check Cloudflare Headers

```bash
curl -I https://yourglossary.com

# Look for:
# cf-cache-status: HIT (cached) or MISS (not cached)
# cf-ray: unique request ID
# server: cloudflare
```

### 2. Test Asset Caching

```bash
# First request (MISS)
curl -I https://yourglossary.com/assets/js/main-abc123.js

# Second request (HIT)
curl -I https://yourglossary.com/assets/js/main-abc123.js
```

### 3. Check Global Distribution

Use https://www.cdn77.com/tester
- Tests asset loading from multiple locations worldwide
- Shows CDN edge server used

### 4. Performance Testing

**GTmetrix:** https://gtmetrix.com
- Enter your URL
- Check CDN status
- Review performance scores

**WebPageTest:** https://www.webpagetest.org
- Test from multiple locations
- Waterfall analysis
- CDN effectiveness

---

## Cloudflare vs. Self-Hosted CDN

| Feature | Cloudflare (Free) | Self-Hosted (Nginx) |
|---------|-------------------|---------------------|
| **Cost** | Free | Server costs |
| **Setup** | 10 minutes | 1-2 hours |
| **Global POPs** | 200+ locations | 1 location |
| **DDoS Protection** | Included | Manual setup |
| **SSL** | Auto (Let's Encrypt) | Manual cert |
| **Caching** | Edge caching | Server caching |
| **Bandwidth** | Unlimited | Limited by server |
| **Analytics** | Built-in | DIY (Google Analytics) |

**Recommendation:** Use Cloudflare for production!

---

## Alternative CDNs

### AWS CloudFront

**Pros:**
- Deep AWS integration
- Lambda@Edge for custom logic
- Very reliable

**Cons:**
- Pay per usage
- More complex setup

**Cost:** ~$0.085/GB + $0.0075/10,000 requests

### Google Cloud CDN

**Pros:**
- GCP integration
- Good performance
- HTTP/3 support

**Cons:**
- Pay per usage
- GCP only

**Cost:** ~$0.08/GB + $0.0075/10,000 requests

### Fastly

**Pros:**
- Real-time purging
- Very fast
- VCL for customization

**Cons:**
- Expensive
- Complex

**Cost:** Starting at $50/month

### Bunny CDN

**Pros:**
- Cheap ($1/TB)
- Fast setup
- Good performance

**Cons:**
- Smaller network
- Less features

**Cost:** $1/TB + $0.005/10,000 requests

---

## Troubleshooting

### Issue: Too Much Caching

**Symptom:** API changes not reflected immediately

**Solution:**
```
Dashboard → Caching → Purge Cache → Purge Everything
```

Or use API:
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

### Issue: Mixed Content Warnings

**Symptom:** HTTPS page loading HTTP resources

**Solution:**
- Enable "Automatic HTTPS Rewrites"
- Check for hardcoded HTTP URLs in code

### Issue: Slow API Responses

**Symptom:** API slower through Cloudflare

**Solution:**
- Set Page Rule to bypass API caching
- Or cache with short TTL (5 minutes)
- Check origin server performance

---

## Best Practices

1. **Use Versioned Asset Names**
   - `main-abc123.js` instead of `main.js`
   - Enables long cache times

2. **Set Appropriate Cache Headers**
   ```nginx
   # Long cache for versioned assets
   expires 1y;
   add_header Cache-Control "public, immutable";

   # No cache for index.html
   expires -1;
   add_header Cache-Control "no-store";
   ```

3. **Purge Cache on Deployment**
   ```bash
   # In CI/CD pipeline
   curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
     -H "Authorization: Bearer {api_token}" \
     -H "Content-Type: application/json" \
     --data '{"files":["https://yourglossary.com/index.html"]}'
   ```

4. **Monitor Cache Hit Rate**
   - Target: > 80% for static assets
   - Dashboard → Analytics → Caching

5. **Use CDN for All Static Assets**
   - Images, CSS, JavaScript, fonts
   - Not for API responses (or short TTL)

---

## Summary

Cloudflare provides:

✅ **Free Global CDN** - 200+ locations
✅ **Easy Setup** - 10 minutes
✅ **Built-in Security** - DDoS, WAF, SSL
✅ **Performance Boost** - 2-5x faster load times
✅ **Cost Savings** - Reduce bandwidth costs
✅ **Analytics** - Traffic and performance insights

**Recommended for all production deployments!**

---

**Last Updated:** 2025-10-19
**Version:** 1.0.0
