#!/usr/bin/env python3

import os
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP
from typing import Tuple
from openai import OpenAI


# Initialize MCP server
mcp = FastMCP("Elastic Synthetics Server")


def safe_json_response(data: Any) -> Dict[str, Any]:
    """Ensure response is JSON serializable"""
    try:
        json.dumps(data)
        return data
    except (TypeError, ValueError) as e:
        return {
            "status": "error",
            "message": f"Response serialization error: {str(e)}",
            "data_type": str(type(data).__name__)
        }

def clean_string(s: str) -> str:
    """Clean string of problematic characters"""
    if not isinstance(s, str):
        return str(s)
    return s.replace('`', "'").replace('\x00', '').strip()

def validate_elastic_locations(locations: List[str]) -> List[str]:
    """Validate and correct Elastic Synthetics location names."""
    valid_locations = [
        "japan", "india", "singapore", "australia_east", "united_kingdom",
        "germany", "canada_east", "brazil", "us_east", "us_west"
    ]
    
    location_mapping = {
        "us-east-1": "us_east",
        "us-west-1": "us_west",
        "us-east": "us_east",
        "us-west": "us_west",
        "usa-east": "us_east",
        "usa-west": "us_west",
        "uk": "united_kingdom",
        "australia": "australia_east",
        "canada": "canada_east"
    }
    
    corrected_locations = []
    for location in locations:
        if location in valid_locations:
            corrected_locations.append(location)
        elif location in location_mapping:
            corrected_locations.append(location_mapping[location])
        else:
            corrected_locations.append("us_east")  # Default fallback
    
    return corrected_locations

def clean_kibana_url(kibana_url: str) -> str:
    """Clean and normalize Kibana URL to prevent double slashes"""
    if not kibana_url:
        return kibana_url
    
    # Remove any existing /app/synthetics path to avoid duplication
    if '/app/synthetics' in kibana_url:
        kibana_url = kibana_url.split('/app/synthetics')[0]
    
    # Remove trailing slashes
    cleaned_url = kibana_url.rstrip('/')
    
    # Fix any double slashes that might exist (but preserve https://)
    cleaned_url = re.sub(r'([^:])//+', r'\1/', cleaned_url)
    
    return cleaned_url

def ensure_playwright_available() -> bool:
    """Check if Playwright is available for enhanced test generation"""
    try:
        # Simple check - if playwright is installed, we can use enhanced features
        result = subprocess.run(['npx', 'playwright', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✨ Playwright available for enhanced test generation")
            return True
        else:
            print("ℹ️  Playwright not available - using standard test generation")
            return False
    except Exception as e:
        print(f"ℹ️  Playwright check failed ({e}) - using standard test generation")
        return False

def analyze_website_with_enhanced_logic(website_url: str) -> Dict[str, Any]:
    """Enhanced website analysis using improved domain and URL pattern matching"""
    try:
        from urllib.parse import urlparse
        import re
        
        parsed_url = urlparse(website_url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()
        
        # Enhanced analysis based on domain patterns and URL structure
        analysis = {
            "available": True,
            "domain": domain,
            "path": path,
            "page_type": "enhanced_analysis"
        }
        
        # Detect website type with more sophisticated patterns
        website_types = []
        
        # Repository detection
        if any(repo_host in domain for repo_host in ['github.com', 'gitlab.com', 'bitbucket.org']):
            website_types.append('repository')
            analysis['hasRepo'] = True
            
        # E-commerce detection
        ecommerce_patterns = ['shop', 'store', 'cart', 'buy', 'product', 'checkout', 'amazon', 'ebay', 'etsy']
        if any(pattern in domain or pattern in path for pattern in ecommerce_patterns):
            website_types.append('ecommerce')
            analysis['hasEcommerce'] = True
            
        # Blog/News detection
        blog_patterns = ['blog', 'news', 'article', 'post', 'medium.com', 'wordpress', 'substack']
        if any(pattern in domain or pattern in path for pattern in blog_patterns):
            website_types.append('blog')
            analysis['hasBlog'] = True
            
        # Documentation detection
        docs_patterns = ['docs', 'documentation', 'wiki', 'guide', 'api', 'readme']
        if any(pattern in domain or pattern in path for pattern in docs_patterns):
            website_types.append('documentation')
            analysis['hasDocs'] = True
            
        # Social media detection
        social_patterns = ['twitter.com', 'facebook.com', 'linkedin.com', 'instagram.com', 'tiktok.com']
        if any(pattern in domain for pattern in social_patterns):
            website_types.append('social')
            analysis['hasSocial'] = True
            
        analysis['website_types'] = website_types
        analysis['primary_type'] = website_types[0] if website_types else 'general'
        
        print(f"🔍 Enhanced analysis for {domain}: {', '.join(website_types) if website_types else 'general website'}")
        
        return analysis
        
    except Exception as e:
        print(f"Enhanced website analysis failed: {e}")
        return {"available": False, "page_type": "unknown"}

def generate_intelligent_test_steps(website_url: str, analysis: Dict[str, Any]) -> str:
    """Generate test steps based on actual website analysis from Playwright MCP"""
    if not analysis.get("available") or not analysis.get("analysis"):
        return ""  # Fall back to domain-based generation
    
    data = analysis["analysis"]
    steps = []
    
    # Repository-specific tests
    if data.get("hasRepo"):
        steps.append('''
  
  step('Verify repository page elements', async () => {
    try {
      // Check for repository-specific elements based on actual page analysis
      const repoElements = page.locator('[data-testid*="repo"], .repository, .repo-name');
      if (await repoElements.count() > 0) {
        console.log('Repository elements found');
      }
      
      const codeElements = page.locator('pre, code, .highlight, .blob-code');
      if (await codeElements.count() > 0) {
        console.log(`Found ${await codeElements.count()} code elements`);
      }
    } catch (error) {
      console.log(`Repository analysis failed: ${error.message}`);
    }
  });''')
    
    # E-commerce specific tests
    if data.get("hasEcommerce") or data.get("products", 0) > 0:
        steps.append(f'''
  
  step('Verify e-commerce functionality', async () => {{
    try {{
      const products = page.locator('.product, [data-testid*="product"], .item-card');
      console.log(`Expected ~{data.get("products", 0)} products based on analysis`);
      
      const cartElements = page.locator('.cart, .add-to-cart, .shopping-cart');
      if (await cartElements.count() > 0) {{
        console.log('Shopping cart functionality detected');
      }}
    }} catch (error) {{
      console.log(`E-commerce analysis failed: ${{error.message}}`);
    }}
  }});''')
    
    # Blog/Article specific tests
    if data.get("hasBlog") or data.get("articles", 0) > 0:
        steps.append(f'''
  
  step('Verify blog/article content', async () => {{
    try {{
      const articles = page.locator('article, .post, .entry, [role="article"]');
      console.log(`Expected ~{data.get("articles", 0)} articles based on analysis`);
      
      const metadata = page.locator('time, .date, .author, .published');
      if (await metadata.count() > 0) {{
        console.log('Article metadata found');
      }}
    }} catch (error) {{
      console.log(`Blog analysis failed: ${{error.message}}`);
    }}
  }});''')
    
    # Documentation specific tests
    if data.get("hasDocs"):
        steps.append('''
  
  step('Verify documentation structure', async () => {
    try {
      const navigation = page.locator('.sidebar, .nav, .toc, .documentation-nav');
      if (await navigation.count() > 0) {
        await expect(navigation.first()).toBeVisible();
        console.log('Documentation navigation verified');
      }
      
      const codeExamples = page.locator('pre code, .code-block, .highlight');
      if (await codeExamples.count() > 0) {
        console.log(`Found ${await codeExamples.count()} code examples`);
      }
    } catch (error) {
      console.log(`Documentation analysis failed: ${error.message}`);
    }
  });''')
    
    # Interactive elements test based on actual counts
    if data.get("buttons", 0) > 0 or data.get("forms", 0) > 0:
        steps.append(f'''
  
  step('Verify interactive elements', async () => {{
    try {{
      const buttons = page.locator('button, input[type="submit"], .btn');
      console.log(`Expected ~{data.get("buttons", 0)} buttons based on analysis`);
      
      const forms = page.locator('form');
      console.log(`Expected ~{data.get("forms", 0)} forms based on analysis`);
      
      const links = page.locator('a[href]');
      console.log(`Expected ~{data.get("links", 0)} links based on analysis`);
    }} catch (error) {{
      console.log(`Interactive elements analysis failed: ${{error.message}}`);
    }}
  }});''')
    
    # Search functionality test
    if data.get("searchBoxes", 0) > 0:
        steps.append('''
  
  step('Verify search functionality', async () => {
    try {
      const searchBoxes = page.locator('input[type="search"], [placeholder*="search" i]');
      if (await searchBoxes.count() > 0) {
        console.log('Search functionality detected');
        // Could add actual search testing here
      }
    } catch (error) {
      console.log(`Search analysis failed: ${error.message}`);
    }
  });''')
    
    return ''.join(steps)

def generate_dynamic_test_steps(website_url: str) -> str:
    """Generate dynamic test steps based on website characteristics"""
    import random
    from urllib.parse import urlparse
    
    try:
        # Use enhanced analysis for intelligent test generation
        analysis = analyze_website_with_enhanced_logic(website_url)
        if analysis.get("available"):
            print(f"🎯 Using enhanced analysis for {website_url}")
            intelligent_steps = generate_intelligent_test_steps(website_url, analysis)
            
            # Add some randomized generic tests for variety
            generic_tests = [
                '''
  
  step('Check interactive elements', async () => {
    try {
      const buttons = page.locator('button, input[type="submit"], .btn');
      const buttonCount = await buttons.count();
      console.log(`Found ${buttonCount} interactive buttons`);
      
      if (buttonCount > 0) {
        const firstButton = buttons.first();
        await expect(firstButton).toBeVisible();
      }
    } catch (error) {
      console.log(`Interactive elements check failed: ${error.message}`);
    }
  });''',
                '''
  
  step('Verify accessibility features', async () => {
    try {
      const headings = page.locator('h1, h2, h3, h4, h5, h6');
      const headingCount = await headings.count();
      console.log(`Found ${headingCount} heading elements`);
      
      const images = page.locator('img');
      const imageCount = await images.count();
      console.log(`Found ${imageCount} images`);
      
      // Check for alt attributes on images
      const imagesWithAlt = page.locator('img[alt]');
      const altCount = await imagesWithAlt.count();
      console.log(`${altCount} of ${imageCount} images have alt text`);
    } catch (error) {
      console.log(`Accessibility check failed: ${error.message}`);
    }
  });''',
                '''
  
  step('Test responsive design elements', async () => {
    try {
      const viewport = page.viewportSize();
      console.log(`Current viewport: ${viewport?.width}x${viewport?.height}`);
      
      const mobileElements = page.locator('.mobile, .responsive, [class*="mobile"], [class*="responsive"]');
      if (await mobileElements.count() > 0) {
        console.log('Responsive design elements detected');
      }
    } catch (error) {
      console.log(`Responsive design check failed: ${error.message}`);
    }
  });'''
            ]
            selected_generic = random.choice(generic_tests)
            return intelligent_steps + selected_generic
    
    except Exception as e:
        print(f"Enhanced analysis failed: {e}")
    
    # Fall back to domain-based analysis if Playwright MCP is not available
    print(f"🎲 Using domain-based analysis for {website_url} (fallback mode)")
    parsed_url = urlparse(website_url)
    domain = parsed_url.netloc.lower()
    path = parsed_url.path.lower()
    
    # Website-specific test steps
    website_specific_steps = ""
    
    # GitHub/GitLab repository tests
    if 'github.com' in domain or 'gitlab.com' in domain:
        website_specific_steps = '''
  
  step('Check repository elements', async () => {
    try {
      // Look for repository-specific elements
      const repoName = page.locator('[data-testid="AppHeader-context-item-label"], .js-repo-nav-item, h1 strong a');
      if (await repoName.count() > 0) {
        await expect(repoName.first()).toBeVisible();
        console.log('Repository name element found');
      }
      
      // Check for code highlighting or file browser
      const codeElements = page.locator('.highlight, .blob-code, .file-navigation');
      if (await codeElements.count() > 0) {
        console.log('Code elements detected');
      }
    } catch (error) {
      console.log(`Repository check failed: ${error.message}`);
    }
  });
  
  step('Check for README or documentation', async () => {
    try {
      const readme = page.locator('#readme, [data-testid="readme"], .markdown-body');
      if (await readme.count() > 0) {
        await expect(readme.first()).toBeVisible();
        console.log('README or documentation found');
      }
    } catch (error) {
      console.log(`Documentation check failed: ${error.message}`);
    }
  });'''
    
    # E-commerce site tests
    elif any(keyword in domain for keyword in ['shop', 'store', 'cart', 'buy', 'commerce', 'market']):
        website_specific_steps = '''
  
  step('Check for product listings', async () => {
    try {
      const products = page.locator('.product, [data-testid*="product"], .item, .card');
      if (await products.count() > 0) {
        await expect(products.first()).toBeVisible();
        console.log(`Found ${await products.count()} product elements`);
      }
    } catch (error) {
      console.log(`Product listing check failed: ${error.message}`);
    }
  });
  
  step('Check for cart or shopping functionality', async () => {
    try {
      const cartElements = page.locator('[data-testid*="cart"], .cart, .shopping-cart, .basket');
      if (await cartElements.count() > 0) {
        console.log('Shopping cart elements found');
      }
      
      const addToCartButtons = page.locator('button:has-text("Add to Cart"), button:has-text("Buy"), .add-to-cart');
      if (await addToCartButtons.count() > 0) {
        console.log('Add to cart buttons found');
      }
    } catch (error) {
      console.log(`Cart functionality check failed: ${error.message}`);
    }
  });'''
    
    # Blog/News site tests
    elif any(keyword in domain for keyword in ['blog', 'news', 'article', 'post', 'medium', 'wordpress']):
        website_specific_steps = '''
  
  step('Check for article content', async () => {
    try {
      const articles = page.locator('article, .post, .entry, [data-testid*="article"]');
      if (await articles.count() > 0) {
        await expect(articles.first()).toBeVisible();
        console.log(`Found ${await articles.count()} article elements`);
      }
      
      const headings = page.locator('h1, h2, .title, .headline');
      if (await headings.count() > 0) {
        console.log('Article headings found');
      }
    } catch (error) {
      console.log(`Article content check failed: ${error.message}`);
    }
  });
  
  step('Check for metadata and publishing info', async () => {
    try {
      const metadata = page.locator('.date, .author, .published, time, .byline');
      if (await metadata.count() > 0) {
        console.log('Article metadata found');
      }
    } catch (error) {
      console.log(`Metadata check failed: ${error.message}`);
    }
  });'''
    
    # Documentation site tests
    elif any(keyword in domain for keyword in ['docs', 'documentation', 'wiki', 'guide', 'manual']):
        website_specific_steps = '''
  
  step('Check navigation and table of contents', async () => {
    try {
      const navigation = page.locator('.sidebar, .nav, .toc, .menu, [data-testid*="nav"]');
      if (await navigation.count() > 0) {
        await expect(navigation.first()).toBeVisible();
        console.log('Documentation navigation found');
      }
    } catch (error) {
      console.log(`Navigation check failed: ${error.message}`);
    }
  });
  
  step('Check for code examples', async () => {
    try {
      const codeBlocks = page.locator('pre, code, .highlight, .code-block');
      if (await codeBlocks.count() > 0) {
        console.log(`Found ${await codeBlocks.count()} code examples`);
      }
    } catch (error) {
      console.log(`Code examples check failed: ${error.message}`);
    }
  });'''
    
    # Add random generic tests for variety
    generic_tests = [
        '''
  
  step('Check for interactive elements', async () => {
    try {
      const buttons = page.locator('button, input[type="submit"], .btn');
      const links = page.locator('a[href]');
      const forms = page.locator('form');
      
      console.log(`Found ${await buttons.count()} buttons, ${await links.count()} links, ${await forms.count()} forms`);
    } catch (error) {
      console.log(`Interactive elements check failed: ${error.message}`);
    }
  });''',
        '''
  
  step('Check accessibility features', async () => {
    try {
      const altTexts = page.locator('img[alt]');
      const headings = page.locator('h1, h2, h3, h4, h5, h6');
      const landmarks = page.locator('[role="main"], [role="navigation"], [role="banner"]');
      
      console.log(`Accessibility check: ${await altTexts.count()} images with alt text, ${await headings.count()} headings, ${await landmarks.count()} landmarks`);
    } catch (error) {
      console.log(`Accessibility check failed: ${error.message}`);
    }
  });''',
        '''
  
  step('Check responsive design elements', async () => {
    try {
      // Check for mobile-friendly elements
      const viewport = page.viewportSize();
      console.log(`Current viewport: ${viewport?.width}x${viewport?.height}`);
      
      const mobileElements = page.locator('.mobile, .responsive, [class*="mobile"], [class*="responsive"]');
      if (await mobileElements.count() > 0) {
        console.log('Responsive design elements detected');
      }
    } catch (error) {
      console.log(`Responsive design check failed: ${error.message}`);
    }
  });'''
    ]
    
    # Randomly select 1-2 generic tests for variety
    selected_generic = random.sample(generic_tests, random.randint(1, 2))
    
    return website_specific_steps + ''.join(selected_generic)

def generate_enhanced_dynamic_test_steps(website_url: str, prompt: str = "", test_name: str = "") -> str:
    """Generate more varied dynamic test steps with randomization"""
    import random
    from urllib.parse import urlparse
    
    # Create a seed based on URL and test name for consistent but varied results
    seed = hash(f"{website_url}_{test_name}_{prompt}") % 10000
    random.seed(seed)
    
    try:
        # Use enhanced analysis for intelligent test generation
        analysis = analyze_website_with_enhanced_logic(website_url)
        if analysis.get("available"):
            print(f"🎯 Using enhanced analysis for {website_url}")
            intelligent_steps = generate_intelligent_test_steps(website_url, analysis)
            
            # Add randomized generic tests with more variety
            generic_test_pool = [
                # Performance tests
                '''
  step('Check page load performance', async () => {
    try {
      const loadTime = await page.evaluate(() => {
        return performance.getEntriesByType('navigation')[0].loadEventEnd - 
               performance.getEntriesByType('navigation')[0].startTime;
      });
      console.log(`Page load time: ${loadTime}ms`);
      expect(loadTime).toBeLessThan(5000);
    } catch (error) {
      console.log(`Performance check failed: ${error.message}`);
    }
  });''',
                
                # Interactive elements tests
                '''
  step('Check interactive elements', async () => {
    try {
      const buttons = page.locator('button, input[type="submit"], .btn');
      const buttonCount = await buttons.count();
      console.log(`Found ${buttonCount} interactive buttons`);
      
      if (buttonCount > 0) {
        const firstButton = buttons.first();
        await expect(firstButton).toBeVisible();
      }
    } catch (error) {
      console.log(`Interactive elements check failed: ${error.message}`);
    }
  });''',
                
                # Accessibility tests
                '''
  step('Verify accessibility features', async () => {
    try {
      const headings = page.locator('h1, h2, h3, h4, h5, h6');
      const headingCount = await headings.count();
      console.log(`Found ${headingCount} heading elements`);
      
      const images = page.locator('img');
      const imageCount = await images.count();
      console.log(`Found ${imageCount} images`);
      
      const imagesWithAlt = page.locator('img[alt]');
      const altCount = await imagesWithAlt.count();
      console.log(`${altCount} of ${imageCount} images have alt text`);
    } catch (error) {
      console.log(`Accessibility check failed: ${error.message}`);
    }
  });''',
                
                # Responsive design tests
                '''
  step('Test responsive design elements', async () => {
    try {
      const viewport = page.viewportSize();
      console.log(`Current viewport: ${viewport?.width}x${viewport?.height}`);
      
      const mobileElements = page.locator('.mobile, .responsive, [class*="mobile"], [class*="responsive"]');
      if (await mobileElements.count() > 0) {
        console.log('Responsive design elements detected');
      }
    } catch (error) {
      console.log(`Responsive design check failed: ${error.message}`);
    }
  });''',
                
                # Content validation tests
                '''
  step('Validate page content structure', async () => {
    try {
      const mainContent = page.locator('main, .main, .content, #content');
      if (await mainContent.count() > 0) {
        await expect(mainContent.first()).toBeVisible();
        console.log('Main content area found');
      }
      
      const navigation = page.locator('nav, .nav, .navigation, [role="navigation"]');
      if (await navigation.count() > 0) {
        console.log('Navigation elements found');
      }
    } catch (error) {
      console.log(`Content structure check failed: ${error.message}`);
    }
  });''',
                
                # Form validation tests
                '''
  step('Check for form elements', async () => {
    try {
      const forms = page.locator('form');
      const formCount = await forms.count();
      console.log(`Found ${formCount} form elements`);
      
      if (formCount > 0) {
        const inputs = page.locator('input, textarea, select');
        const inputCount = await inputs.count();
        console.log(`Found ${inputCount} input elements`);
      }
    } catch (error) {
      console.log(`Form check failed: ${error.message}`);
    }
  });'''
            ]
            
            # Select 2-3 random tests for variety
            num_tests = random.randint(2, 3)
            selected_tests = random.sample(generic_test_pool, num_tests)
            return intelligent_steps + ''.join(selected_tests)
    
    except Exception as e:
        print(f"Enhanced analysis failed: {e}")
    
    # Enhanced fallback with more variety
    print(f"🎲 Using enhanced domain-based analysis for {website_url}")
    parsed_url = urlparse(website_url)
    domain = parsed_url.netloc.lower()
    
    # Website-specific test steps
    website_specific_steps = ""
    
    # GitHub/GitLab repository tests
    if 'github.com' in domain or 'gitlab.com' in domain:
        website_specific_steps = '''
  
  step('Check repository elements', async () => {
    try {
      // Look for repository-specific elements
      const repoName = page.locator('[data-testid="AppHeader-context-item-label"], .js-repo-nav-item, h1 strong a');
      if (await repoName.count() > 0) {
        await expect(repoName.first()).toBeVisible();
        console.log('Repository name element found');
      }
      
      // Check for code highlighting or file browser
      const codeElements = page.locator('.highlight, .blob-code, .file-navigation');
      if (await codeElements.count() > 0) {
        console.log('Code elements detected');
      }
    } catch (error) {
      console.log(`Repository check failed: ${error.message}`);
    }
  });
  
  step('Check for README or documentation', async () => {
    try {
      const readme = page.locator('#readme, [data-testid="readme"], .markdown-body');
      if (await readme.count() > 0) {
        await expect(readme.first()).toBeVisible();
        console.log('README or documentation found');
      }
    } catch (error) {
      console.log(`Documentation check failed: ${error.message}`);
    }
  });'''
    
    # E-commerce site tests
    elif any(keyword in domain for keyword in ['shop', 'store', 'cart', 'buy', 'commerce', 'market']):
        website_specific_steps = '''
  
  step('Check for product listings', async () => {
    try {
      const products = page.locator('.product, [data-testid*="product"], .item, .card');
      if (await products.count() > 0) {
        await expect(products.first()).toBeVisible();
        console.log(`Found ${await products.count()} product elements`);
      }
    } catch (error) {
      console.log(`Product listing check failed: ${error.message}`);
    }
  });
  
  step('Check for cart or shopping functionality', async () => {
    try {
      const cartElements = page.locator('[data-testid*="cart"], .cart, .shopping-cart, .basket');
      if (await cartElements.count() > 0) {
        console.log('Shopping cart elements found');
      }
      
      const addToCartButtons = page.locator('button:has-text("Add to Cart"), button:has-text("Buy"), .add-to-cart');
      if (await addToCartButtons.count() > 0) {
        console.log('Add to cart buttons found');
      }
    } catch (error) {
      console.log(`Cart functionality check failed: ${error.message}`);
    }
  });'''
    
    # Blog/News site tests
    elif any(keyword in domain for keyword in ['blog', 'news', 'article', 'post', 'medium', 'wordpress']):
        website_specific_steps = '''
  
  step('Check for article content', async () => {
    try {
      const articles = page.locator('article, .post, .entry, [data-testid*="article"]');
      if (await articles.count() > 0) {
        await expect(articles.first()).toBeVisible();
        console.log(`Found ${await articles.count()} article elements`);
      }
      
      const headings = page.locator('h1, h2, .title, .headline');
      if (await headings.count() > 0) {
        console.log('Article headings found');
      }
    } catch (error) {
      console.log(`Article content check failed: ${error.message}`);
    }
  });
  
  step('Check for metadata and publishing info', async () => {
    try {
      const metadata = page.locator('.date, .author, .published, time, .byline');
      if (await metadata.count() > 0) {
        console.log('Article metadata found');
      }
    } catch (error) {
      console.log(`Metadata check failed: ${error.message}`);
    }
  });'''
    
    # Documentation site tests
    elif any(keyword in domain for keyword in ['docs', 'documentation', 'wiki', 'guide', 'manual']):
        website_specific_steps = '''
  
  step('Check navigation and table of contents', async () => {
    try {
      const navigation = page.locator('.sidebar, .nav, .toc, .menu, [data-testid*="nav"]');
      if (await navigation.count() > 0) {
        await expect(navigation.first()).toBeVisible();
        console.log('Documentation navigation found');
      }
    } catch (error) {
      console.log(`Navigation check failed: ${error.message}`);
    }
  });
  
  step('Check for code examples', async () => {
    try {
      const codeBlocks = page.locator('pre, code, .highlight, .code-block');
      if (await codeBlocks.count() > 0) {
        console.log(`Found ${await codeBlocks.count()} code examples`);
      }
    } catch (error) {
      console.log(`Code examples check failed: ${error.message}`);
    }
  });'''
    
    # Add random generic tests for variety
    generic_tests = [
        '''
  
  step('Check for interactive elements', async () => {
    try {
      const buttons = page.locator('button, input[type="submit"], .btn');
      const links = page.locator('a[href]');
      const forms = page.locator('form');
      
      console.log(`Found ${await buttons.count()} buttons, ${await links.count()} links, ${await forms.count()} forms`);
    } catch (error) {
      console.log(`Interactive elements check failed: ${error.message}`);
    }
  });''',
        '''
  
  step('Check accessibility features', async () => {
    try {
      const altTexts = page.locator('img[alt]');
      const headings = page.locator('h1, h2, h3, h4, h5, h6');
      const landmarks = page.locator('[role="main"], [role="navigation"], [role="banner"]');
      
      console.log(`Accessibility check: ${await altTexts.count()} images with alt text, ${await headings.count()} headings, ${await landmarks.count()} landmarks`);
    } catch (error) {
      console.log(`Accessibility check failed: ${error.message}`);
    }
  });''',
        '''
  
  step('Check responsive design elements', async () => {
    try {
      // Check for mobile-friendly elements
      const viewport = page.viewportSize();
      console.log(`Current viewport: ${viewport?.width}x${viewport?.height}`);
      
      const mobileElements = page.locator('.mobile, .responsive, [class*="mobile"], [class*="responsive"]');
      if (await mobileElements.count() > 0) {
        console.log('Responsive design elements detected');
      }
    } catch (error) {
      console.log(`Responsive design check failed: ${error.message}`);
    }
  });'''
    ]
    
    # Randomly select 1-2 generic tests for variety
    selected_generic = random.sample(generic_tests, random.randint(1, 2))
    
    return website_specific_steps + ''.join(selected_generic)

def load_env_from_warp_mcp() -> Dict[str, str]:
    """Load Elastic Synthetics environment variables from Warp MCP."""
    elastic_env_vars = {}
    
    # Primary environment variable patterns
    primary_patterns = [
        'ELASTIC_KIBANA_URL', 'KIBANA_URL',
        'ELASTIC_API_KEY', 'API_KEY', 'SYNTHETICS_API_KEY',
        'ELASTIC_PROJECT_ID', 'PROJECT_ID', 'SYNTHETICS_PROJECT_ID',
        'ELASTIC_SPACE', 'SPACE', 'SYNTHETICS_SPACE',
        'OPENAI_API_KEY', 'LLM_MODEL'  # Add OpenAI API key
    ]
    
    # Check environment variables first
    for var in primary_patterns:
        if var in os.environ:
            elastic_env_vars[var] = os.environ[var]
    
    # If we don't have the OpenAI API key, try to load from mcp.json
    if 'OPENAI_API_KEY' not in elastic_env_vars:
        try:
            mcp_config_path = Path('mcp.json')
            if mcp_config_path.exists():
                with open(mcp_config_path, 'r') as f:
                    mcp_config = json.load(f)
                
                # Extract environment variables from mcp.json
                env_section = mcp_config.get('elastic-synthetics', {}).get('env', {})
                for var in primary_patterns:
                    if var in env_section and var not in elastic_env_vars:
                        elastic_env_vars[var] = env_section[var]
                        print(f"📁 Loaded {var} from mcp.json")
        except Exception as e:
            print(f"⚠️  Could not load mcp.json: {e}")
    
    return elastic_env_vars

@mcp.tool()
def initialize_intelligent_testing() -> Dict[str, Any]:
    """🎭 Initialize intelligent test generation with automatic Playwright MCP setup"""
    try:
        print("🚀 Initializing Elastic Synthetics with Enhanced Intelligence...")
        
        # Check if Playwright MCP is installed
        try:
            result = subprocess.run(['npx', '@playwright/mcp@latest', '--help'], 
                                  capture_output=True, timeout=5)
            playwright_installed = result.returncode == 0
        except:
            playwright_installed = False
        
        if not playwright_installed:
            print("📦 Installing Playwright MCP for enhanced intelligence...")
            try:
                subprocess.run(['npm', 'install', '-g', '@playwright/mcp@latest'], 
                             check=True, timeout=60)
                print("✅ Playwright MCP installed successfully!")
                playwright_installed = True
            except Exception as e:
                print(f"⚠️  Could not install Playwright MCP: {e}")
        
        # Test the intelligent system
        if playwright_installed:
            # Try to start and test Playwright MCP
            mcp_available = ensure_playwright_mcp_running()
            
            if mcp_available:
                # Test with a quick analysis
                test_analysis = analyze_website_with_playwright_mcp("https://github.com")
                intelligent_mode = test_analysis.get("available", False)
            else:
                intelligent_mode = False
        else:
            intelligent_mode = False
        
        # Check Elastic configuration
        env_vars = load_env_from_warp_mcp()
        elastic_configured = bool(
            env_vars.get('ELASTIC_KIBANA_URL') and 
            env_vars.get('ELASTIC_API_KEY')
        )
        
        return safe_json_response({
            "status": "success",
            "message": "🎭 Elastic Synthetics Enhanced Intelligence Initialized!",
            "capabilities": {
                "elastic_synthetics": True,
                "intelligent_analysis": intelligent_mode,
                "playwright_mcp": playwright_installed,
                "environment_configured": elastic_configured
            },
            "features": [
                "✅ Dynamic test generation based on website characteristics",
                "🎯 Intelligent website analysis" if intelligent_mode else "🔄 Domain-based test generation (fallback)",
                "⚡ Automatic Playwright MCP management" if intelligent_mode else "💡 Install Playwright MCP for enhanced intelligence",
                "🚀 Clean test deployment (no monitor.use issues)",
                "🛡️ Graceful fallbacks ensure reliability",
                "🔧 Comprehensive URL cleanup and validation"
            ],
            "intelligence_level": "🧠 Enhanced" if intelligent_mode else "🎲 Standard",
            "next_steps": [
                "Your test generation is now ready!",
                "Tests will automatically use the best available intelligence",
                "Enhanced mode provides real-time website analysis" if intelligent_mode else "Consider setting up Playwright MCP for enhanced intelligence",
                "All existing workflows continue to work seamlessly"
            ],
            "magical_features": {
                "auto_playwright_management": intelligent_mode,
                "intelligent_fallback": True,
                "zero_configuration": True,
                "seamless_enhancement": True
            }
        })
        
    except Exception as e:
        return safe_json_response({
            "status": "error",
            "message": f"Initialization failed: {str(e)}",
            "fallback": "Standard test generation still available"
        })

@mcp.tool()
def diagnose_warp_mcp_config() -> Dict[str, Any]:
    """Diagnose Warp MCP environment configuration for Elastic Synthetics"""
    try:
        env_vars = load_env_from_warp_mcp()
        
        # Check for required variables
        kibana_url = env_vars.get('ELASTIC_KIBANA_URL') or env_vars.get('KIBANA_URL')
        api_key = env_vars.get('ELASTIC_API_KEY') or env_vars.get('API_KEY')
        project_id = env_vars.get('ELASTIC_PROJECT_ID') or env_vars.get('PROJECT_ID')
        space = env_vars.get('ELASTIC_SPACE') or env_vars.get('SPACE', 'default')
        
        # Mask sensitive values for display
        masked_vars = {}
        for key, value in env_vars.items():
            if 'API_KEY' in key or 'TOKEN' in key:
                masked_vars[key] = f"{value[:8]}..." if value and len(value) > 8 else "***"
            else:
                masked_vars[key] = value
        
        deployment_ready = bool(kibana_url and api_key)
        
        return safe_json_response({
            "status": "success",
            "environment_variables": masked_vars,
            "required_check": {
                "kibana_url": bool(kibana_url),
                "api_key": bool(api_key),
                "project_id": bool(project_id),
                "space": bool(space)
            },
            "deployment_ready": deployment_ready,
            "recommendations": [
                "Environment variables detected" if env_vars else "No environment variables found",
                "Kibana URL configured" if kibana_url else "Missing ELASTIC_KIBANA_URL or KIBANA_URL",
                "API Key configured" if api_key else "Missing ELASTIC_API_KEY or API_KEY",
                "Ready for deployment" if deployment_ready else "Missing required credentials"
            ]
        })
        
    except Exception as e:
        return safe_json_response({
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        })

@mcp.tool()
def create_test_and_manual_deploy_command(
    website_url: str,
    test_name: str,
    schedule_minutes: int = 10,
    locations: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    working_directory: Optional[str] = None
) -> Dict[str, Any]:
    """Create a clean browser test and provide manual deployment command"""
    try:
        if working_directory is None:
            working_directory = os.getcwd()
        
        if locations is None:
            locations = ["us_east"]
        
        locations = validate_elastic_locations(locations)
        
        if tags is None:
            tags = []
        
        # Validate schedule
        allowed_schedules = [1, 2, 3, 5, 10, 15, 20, 30, 60, 120, 240]
        if schedule_minutes not in allowed_schedules:
            schedule_minutes = min(allowed_schedules, key=lambda x: abs(x - schedule_minutes))
        
        # Get environment variables
        elastic_vars = load_env_from_warp_mcp()
        kibana_url = (
            elastic_vars.get('ELASTIC_KIBANA_URL') or 
            elastic_vars.get('KIBANA_URL') or
            os.environ.get('ELASTIC_KIBANA_URL') or
            os.environ.get('KIBANA_URL')
        )
        api_key = (
            elastic_vars.get('ELASTIC_API_KEY') or 
            elastic_vars.get('API_KEY') or
            os.environ.get('ELASTIC_API_KEY') or
            os.environ.get('API_KEY')
        )
        project_id = (
            elastic_vars.get('ELASTIC_PROJECT_ID') or 
            elastic_vars.get('PROJECT_ID') or
            os.environ.get('ELASTIC_PROJECT_ID') or
            os.environ.get('PROJECT_ID', 'mcp-synthetics-demo')
        )
        space = (
            elastic_vars.get('ELASTIC_SPACE') or 
            elastic_vars.get('SPACE') or
            os.environ.get('ELASTIC_SPACE') or
            os.environ.get('SPACE', 'default')
        )
        
        # Clean the Kibana URL to prevent double slashes
        if kibana_url:
            kibana_url = clean_kibana_url(kibana_url)
        
        if not kibana_url or not api_key:
            return safe_json_response({
                "status": "error",
                "message": "Missing ELASTIC_KIBANA_URL or ELASTIC_API_KEY in environment",
                "suggestion": "Run diagnose_warp_mcp_config() to check your environment variables"
            })
        
        # Create test file
        test_name_clean = clean_string(test_name)
        website_url_clean = clean_string(website_url)
        
        test_dir = Path(working_directory) / "synthetic_tests"
        test_dir.mkdir(exist_ok=True)
        
        test_file_name = f"{test_name_clean.lower().replace(' ', '_')}.journey.ts"
        test_file_path = test_dir / test_file_name
        
        # Generate dynamic test steps based on website characteristics
        dynamic_steps = generate_dynamic_test_steps(website_url_clean)
        
        test_content = f'''import {{ journey, step, expect, monitor }} from '@elastic/synthetics';

journey({{
  name: '{test_name}',
  tags: {json.dumps(tags)},
}}, ({{ page, params }}) => {{
  
  // Monitor settings are configured via CLI parameters
  // Individual tests should not override global schedule settings
  
  step('Navigate to {website_url_clean}', async () => {{
    await page.goto('{website_url_clean}');
    await page.waitForLoadState('networkidle');
  }});
  
  step('Verify page title', async () => {{
    try {{
      // Wait for title to be present, but don't fail if it's empty
      await page.waitForFunction(() => document.title !== undefined, {{ timeout: 3000 }});
      const title = await page.title();
      console.log(`Page title: "${{title}}"`);
      
      // Check if title exists and is not empty
      if (title && title.trim().length > 0) {{
        await expect(page).toHaveTitle(/.+/);
      }} else {{
        console.log('Page has no title or empty title - skipping title assertion');
      }}
    }} catch (error) {{
      console.log(`Title check failed: ${{error.message}} - continuing with other tests`);
    }}
  }});
  
  step('Check page load performance', async () => {{
    const loadTime = await page.evaluate(() => {{
      return performance.getEntriesByType('navigation')[0].loadEventEnd - 
             performance.getEntriesByType('navigation')[0].startTime;
    }});
    console.log(`Page load time: ${{loadTime}}ms`);
    expect(loadTime).toBeLessThan(5000); // Should load within 5 seconds
  }});{dynamic_steps}
  
  step('Take screenshot', async () => {{
    await page.screenshot({{ path: '{test_name_clean}_screenshot.png' }});
  }});
  
  step('Verify page is visible', async () => {{
    await expect(page.locator('body')).toBeVisible();
  }});
}});
'''
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Create manual deployment commands
        manual_commands = [
            f"# Navigate to your project directory",
            f"cd {working_directory}",
            f"",
            f"# Deploy the test file",
            f"npx @elastic/synthetics push {test_file_path} \\",
            f"  --auth {api_key} \\",
            f"  --url {kibana_url} \\",
            f"  --schedule {schedule_minutes} \\",
            f"  --locations {','.join(locations)} \\",
            f"  --id {project_id} \\",
            f"  --space {space} \\",
            f"  --yes"
        ]
        
        return safe_json_response({
            "status": "success",
            "message": "Test created successfully. Use manual commands to deploy.",
            "test_file": str(test_file_path),
            "test_name": test_name,
            "website_url": website_url,
            "schedule_minutes": schedule_minutes,
            "locations": locations,
            "manual_commands": manual_commands,
            "manual_commands_text": "\n".join(manual_commands),
            "environment_check": {
                "kibana_url_set": bool(kibana_url),
                "api_key_set": bool(api_key),
                "kibana_url_preview": kibana_url[:50] + "..." if kibana_url and len(kibana_url) > 50 else kibana_url,
                "api_key_preview": api_key[:10] + "..." if api_key and len(api_key) > 10 else "Not found",
                "project_id": project_id,
                "space": space
            },
            "instructions": [
                "1. The commands above have your actual credentials filled in from Warp MCP",
                "2. Copy and paste the manual command into your terminal",
                "3. This test file has NO monitor.use() calls to cause @every format issues",
                "4. The test uses dynamic steps tailored to the specific website type",
                "5. Tests are automatically customized based on website characteristics (e.g., GitHub repos, e-commerce, blogs)",
                "6. Dynamic tests include website-specific checks and random generic tests for comprehensive coverage"
            ]
        })
        
    except Exception as e:
        return safe_json_response({
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        })

@mcp.tool()
def create_and_deploy_browser_test(
    website_url: str,
    test_name: str,
    test_description: Optional[str] = None,
    locations: Optional[List[str]] = None,
    schedule_minutes: int = 10,
    tags: Optional[List[str]] = None,
    working_directory: Optional[str] = None
) -> Dict[str, Any]:
    """Complete automated workflow: 1) Test connection 2) Create clean browser test 3) Deploy to Elastic"""
    try:
        if working_directory is None:
            working_directory = os.getcwd()
        
        if locations is None:
            locations = ["us_east"]
        
        locations = validate_elastic_locations(locations)
        
        if tags is None:
            tags = []
        
        if test_description is None:
            test_description = f"Browser test for {website_url}"
        
        # Validate schedule
        allowed_schedules = [1, 2, 3, 5, 10, 15, 20, 30, 60, 120, 240]
        if schedule_minutes not in allowed_schedules:
            schedule_minutes = min(allowed_schedules, key=lambda x: abs(x - schedule_minutes))
        
        workflow_results = {
            "workflow_status": "in_progress",
            "steps": {},
            "test_file": None,
            "monitor_url": None
        }
        
        # Step 1: Test connection (environment variables)
        elastic_vars = load_env_from_warp_mcp()
        kibana_url = (
            elastic_vars.get('ELASTIC_KIBANA_URL') or 
            elastic_vars.get('KIBANA_URL') or
            os.environ.get('ELASTIC_KIBANA_URL') or
            os.environ.get('KIBANA_URL')
        )
        api_key = (
            elastic_vars.get('ELASTIC_API_KEY') or 
            elastic_vars.get('API_KEY') or
            os.environ.get('ELASTIC_API_KEY') or
            os.environ.get('API_KEY')
        )
        project_id = (
            elastic_vars.get('ELASTIC_PROJECT_ID') or 
            elastic_vars.get('PROJECT_ID') or
            os.environ.get('ELASTIC_PROJECT_ID') or
            os.environ.get('PROJECT_ID', 'mcp-synthetics-demo')
        )
        space = (
            elastic_vars.get('ELASTIC_SPACE') or 
            elastic_vars.get('SPACE') or
            os.environ.get('ELASTIC_SPACE') or
            os.environ.get('SPACE', 'default')
        )
        
        # Clean the Kibana URL to prevent double slashes
        if kibana_url:
            kibana_url = clean_kibana_url(kibana_url)
        
        if not kibana_url or not api_key:
            workflow_results["steps"]["1_connection"] = {
                "status": "failed",
                "result": {
                    "error": "Missing required environment variables",
                    "missing": {
                        "kibana_url": not bool(kibana_url),
                        "api_key": not bool(api_key)
                    }
                }
            }
            workflow_results["workflow_status"] = "failed"
            return safe_json_response(workflow_results)
        
        workflow_results["steps"]["1_connection"] = {
            "status": "success",
            "result": {"message": "Environment variables detected"}
        }
        
        # Step 2: Create clean test file
        test_name_clean = clean_string(test_name)
        website_url_clean = clean_string(website_url)
        
        test_dir = Path(working_directory) / "synthetic_tests"
        test_dir.mkdir(exist_ok=True)
        
        test_file_name = f"{test_name_clean.lower().replace(' ', '_')}.journey.ts"
        test_file_path = test_dir / test_file_name
        
        # Generate dynamic test steps based on website characteristics
        dynamic_steps = generate_dynamic_test_steps(website_url_clean)
        
        # Generate clean test content
        test_content = f'''import {{ journey, step, expect, monitor }} from '@elastic/synthetics';

journey({{
  name: '{test_name}',
  tags: {json.dumps(tags)},
}}, ({{ page, params }}) => {{
  
  // Monitor settings are configured via CLI parameters
  // Individual tests should not override global schedule settings
  
  step('Navigate to {website_url_clean}', async () => {{
    await page.goto('{website_url_clean}');
    await page.waitForLoadState('networkidle');
  }});
  
  step('Verify page title', async () => {{
    try {{
      // Wait for title to be present, but don't fail if it's empty
      await page.waitForFunction(() => document.title !== undefined, {{ timeout: 3000 }});
      const title = await page.title();
      console.log(`Page title: "${{title}}"`);
      
      // Check if title exists and is not empty
      if (title && title.trim().length > 0) {{
        await expect(page).toHaveTitle(/.+/);
      }} else {{
        console.log('Page has no title or empty title - skipping title assertion');
      }}
    }} catch (error) {{
      console.log(`Title check failed: ${{error.message}} - continuing with other tests`);
    }}
  }});
  
  step('Check page load performance', async () => {{
    const loadTime = await page.evaluate(() => {{
      return performance.getEntriesByType('navigation')[0].loadEventEnd - 
             performance.getEntriesByType('navigation')[0].startTime;
    }});
    console.log(`Page load time: ${{loadTime}}ms`);
    expect(loadTime).toBeLessThan(5000); // Should load within 5 seconds
  }});{dynamic_steps}
  
  step('Take screenshot', async () => {{
    await page.screenshot({{ path: '{test_name_clean}_screenshot.png' }});
  }});
  
  step('Verify page is visible', async () => {{
    await expect(page.locator('body')).toBeVisible();
  }});
}});
'''
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        workflow_results["steps"]["2_test_creation"] = {
            "status": "success",
            "result": {
                "message": "Clean test file created successfully",
                "test_file": str(test_file_path),
                "test_name": test_name
            }
        }
        workflow_results["test_file"] = str(test_file_path)
        
        # Step 3: Deploy to Elastic
        env = os.environ.copy()
        env.update(elastic_vars)
        
        push_cmd = [
            "npx", "@elastic/synthetics", "push", str(test_file_path),
            "--auth", api_key,
            "--url", kibana_url,
            "--locations", ",".join(locations),
            "--schedule", str(schedule_minutes),
            "--yes"
        ]
        
        if project_id and project_id != 'mcp-synthetics-demo':
            push_cmd.extend(["--id", project_id])
        if space and space != 'default':
            push_cmd.extend(["--space", space])
        
        try:
            result = subprocess.run(
                push_cmd, 
                cwd=working_directory, 
                env=env, 
                capture_output=True, 
                text=True,
                timeout=120,
                input="y\n"
            )
        except subprocess.TimeoutExpired as e:
            workflow_results["steps"]["3_deployment"] = {
                "status": "failed",
                "result": {
                    "error": f"Command timed out after 120 seconds",
                    "suggestion": "Try the manual deployment command instead"
                }
            }
            workflow_results["workflow_status"] = "partial_success"
            return safe_json_response(workflow_results)
        
        if result.returncode == 0:
            # Parse output for monitor URL
            monitor_url = None
            monitor_id = None
            
            for line in result.stdout.split('\n'):
                if 'app/synthetics/monitor/' in line:
                    url_match = re.search(r'https://[^\s]+/app/synthetics/monitor[^\s]+', line)
                    if url_match:
                        # Fix double slashes in URL from CLI output
                        monitor_url = url_match.group(0).replace('//app/synthetics', '/app/synthetics')
                elif any(phrase in line.lower() for phrase in ['monitor id', 'created monitor']):
                    id_match = re.search(r'[a-f0-9-]{36}', line)
                    if id_match:
                        monitor_id = id_match.group(0)
            
            if not monitor_url:
                monitor_url = f"{kibana_url}/app/synthetics"
            
            workflow_results["steps"]["3_deployment"] = {
                "status": "success",
                "result": {
                    "message": "Test deployed successfully",
                    "monitor_url": monitor_url,
                    "monitor_id": monitor_id,
                    "stdout": result.stdout
                }
            }
            workflow_results["workflow_status"] = "completed"
            workflow_results["monitor_url"] = monitor_url
            workflow_results["message"] = f"Successfully created and deployed browser test for {website_url}"
        else:
            workflow_results["steps"]["3_deployment"] = {
                "status": "failed",
                "result": {
                    "error": result.stderr,
                    "stdout": result.stdout,
                    "push_command": " ".join(push_cmd)
                }
            }
            workflow_results["workflow_status"] = "partial_success"
            workflow_results["message"] = "Test created but deployment failed"
        
        return safe_json_response(workflow_results)
        
    except Exception as e:
        return safe_json_response({
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        })
    

def _get_llm():
    # First check environment variables
    env_api_key = os.environ.get("OPENAI_API_KEY")
    
    if OpenAI and env_api_key:
        model = os.environ.get("LLM_MODEL", "gpt-4o")
        return OpenAI(), model
    
    # If no env var, check MCP configuration
    try:
        elastic_vars = load_env_from_warp_mcp()
        api_key = elastic_vars.get('OPENAI_API_KEY')
        if api_key:
            model = elastic_vars.get('LLM_MODEL', 'gpt-4o-mini')
            # Set the API key in environment for OpenAI client
            os.environ["OPENAI_API_KEY"] = api_key
            
            if OpenAI:
                return OpenAI(), model
        else:
            pass
    except Exception as e:
        pass
    
    return None, None  # no-LLM fallback

JOURNEY_TEMPLATE = """import {{ journey, step, expect }} from '@elastic/synthetics';

journey({{
  name: '{TEST_NAME}',
  tags: {TAGS_JSON}
}}, ({{ page, params }}) => {{
  // ── Guarded nav: always load target URL first
  step('Navigate to {WEBSITE_URL}', async () => {{
    await page.goto('{WEBSITE_URL}');
    await page.waitForLoadState('networkidle');
  }});

  // ==== BEGIN LLM STEPS (safe region) ====
{LLM_STEPS}
  // ==== END LLM STEPS ====

  // Baseline checks still included
  step('Screenshot', async () => {{
    await page.screenshot({{ path: '{SAFE_FILE}_screenshot.png' }});
  }});
  step('Body visible', async () => {{
    await expect(page.locator('body')).toBeVisible();
  }});
}});
"""

# Very conservative sanitizer to keep generated content safe and compatible
BLOCKED_PATTERNS = [
    r"monitor\.use",               # prevent schedule overrides (@every issues)
    r"import\s+",                  # no extra imports
    r"require\s*\(",               # no require
    r"exec\(|spawn\(|fork\(",      # no process control
    r"fs\.", r"child_process",     # no FS/child proc
    r"await\s+page\.goto\(",       # we manage navigation
]

def _sanitize_llm_steps(text: str) -> str:
    """Sanitize LLM-generated steps while preserving variety and functionality"""
    if not text or not text.strip():
        return """  step('Verify title', async () => {
    const t = await page.title();
    if (t && t.trim()) { await expect(page).toHaveTitle(/.+/); }
  });"""
    
    # Remove code fencing if present
    cleaned = text.strip()
    for fence in ["```ts", "```typescript", "```javascript", "```"]:
        cleaned = cleaned.replace(fence, "")
    
    # Split into lines and filter dangerous patterns
    lines = []
    import re as _re
    
    for line in cleaned.splitlines():
        line_stripped = line.strip()
        
        # Skip completely empty lines at the start, but preserve indentation structure
        if not line_stripped and not lines:
            continue
            
        # Block truly dangerous patterns
        dangerous = False
        for pattern in BLOCKED_PATTERNS:
            if _re.search(pattern, line, _re.IGNORECASE):
                print(f"🚫 Blocked dangerous line: {line.strip()}")
                dangerous = True
                break
        
        if not dangerous:
            lines.append(line.rstrip())
    
    safe = "\n".join(lines).strip()
    
    # Only fall back to default if there are literally no step() calls
    step_count = safe.count("step(")
    if step_count == 0 or len(safe.strip()) < 20:
        print(f"⚠️  Insufficient content (steps: {step_count}, length: {len(safe)}), using fallback")
        safe = """  step('Verify page loads', async () => {
    const t = await page.title();
    if (t && t.trim()) { 
      await expect(page).toHaveTitle(/.+/); 
    }
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });"""
    else:
        print(f"✅ Sanitized content preserved: {step_count} steps, {len(safe)} chars")
    
    return safe

def _seed_context_for_llm(website_url: str) -> str:
    # Small deterministic hints to help the model (no external calls)
    hints = analyze_website_with_enhanced_logic(website_url) or {}
    types = ", ".join(hints.get("website_types", [])) or "general"
    return f"Target appears to be: {types}. Primary type: {hints.get('primary_type','general')}."

LLM_SYSTEM = """You write ONLY the body steps for an Elastic Synthetics Playwright journey.

CRITICAL INSTRUCTIONS:
- You MUST create specific test steps based on the user's request
- Do NOT generate generic tests
- If the user asks to verify specific text or elements, create steps that actually check for those specific things
- Use page.locator() with specific selectors for the elements mentioned
- Use expect() assertions to verify the expected behavior

Constraints:
- Do NOT import anything (imports are provided)
- Do NOT call monitor.use or set schedules/tags/ids
- Do NOT navigate to other URLs; the harness already called page.goto(target)
- Write 2–6 clear step(...) blocks using Playwright
- Prefer robust selectors (roles, labels, text with expect(...) guards)
- Be resilient: wrap risky assertions in try/catch and log rather than fail hard

Output: RAW TypeScript code consisting solely of step(...) blocks."""

def _deploy_test_file_only(
    test_file_path: str,
    website_url: str,
    test_name: str,
    locations: List[str],
    schedule_minutes: int,
    working_directory: str
) -> Dict[str, Any]:
    """Deploy an existing test file without creating a new one"""
    try:
        print(f"🚀 Starting deployment of {test_file_path}")
        
        # Validate schedule
        allowed_schedules = [1, 2, 3, 5, 10, 15, 20, 30, 60, 120, 240]
        if schedule_minutes not in allowed_schedules:
            schedule_minutes = min(allowed_schedules, key=lambda x: abs(x - schedule_minutes))
        
        # Get environment variables
        elastic_vars = load_env_from_warp_mcp()
        kibana_url = (
            elastic_vars.get('ELASTIC_KIBANA_URL') or 
            elastic_vars.get('KIBANA_URL') or
            os.environ.get('ELASTIC_KIBANA_URL') or
            os.environ.get('KIBANA_URL')
        )
        api_key = (
            elastic_vars.get('ELASTIC_API_KEY') or 
            elastic_vars.get('API_KEY') or
            os.environ.get('ELASTIC_API_KEY') or
            os.environ.get('API_KEY')
        )
        project_id = (
            elastic_vars.get('ELASTIC_PROJECT_ID') or 
            elastic_vars.get('PROJECT_ID') or
            os.environ.get('ELASTIC_PROJECT_ID') or
            os.environ.get('PROJECT_ID', 'mcp-synthetics-demo')
        )
        space = (
            elastic_vars.get('ELASTIC_SPACE') or 
            elastic_vars.get('SPACE') or
            os.environ.get('ELASTIC_SPACE') or
            os.environ.get('SPACE', 'default')
        )
        
        # Clean the Kibana URL
        if kibana_url:
            kibana_url = clean_kibana_url(kibana_url)
        
        print(f"🔑 Using Kibana URL: {kibana_url}")
        print(f"🔑 API Key present: {bool(api_key)}")
        print(f"📍 Project ID: {project_id}")
        print(f"🏠 Space: {space}")
        
        if not kibana_url or not api_key:
            return {
                "workflow_status": "failed",
                "steps": {
                    "1_connection": {
                        "status": "failed",
                        "result": {
                            "error": "Missing required environment variables",
                            "missing": {
                                "kibana_url": not bool(kibana_url),
                                "api_key": not bool(api_key)
                            }
                        }
                    }
                },
                "message": "Missing ELASTIC_KIBANA_URL or ELASTIC_API_KEY"
            }
        
        # Build deployment command
        env = os.environ.copy()
        env.update(elastic_vars)
        
        push_cmd = [
            "npx", "@elastic/synthetics", "push", test_file_path,
            "--auth", api_key,
            "--url", kibana_url,
            "--locations", ",".join(locations),
            "--schedule", str(schedule_minutes),
            "--yes"
        ]
        
        if project_id and project_id != 'mcp-synthetics-demo':
            push_cmd.extend(["--id", project_id])
        if space and space != 'default':
            push_cmd.extend(["--space", space])
        
        print(f"🚀 Deployment command: {' '.join(push_cmd[:3])} [file] [auth] [url] --locations {','.join(locations)} --schedule {schedule_minutes}")
        
        try:
            result = subprocess.run(
                push_cmd, 
                cwd=working_directory, 
                env=env, 
                capture_output=True, 
                text=True,
                timeout=120,
                input="y\n"
            )
            print(f"📤 Command completed with return code: {result.returncode}")
            print(f"📝 Stdout: {result.stdout}")
            if result.stderr:
                print(f"⚠️ Stderr: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            return {
                "workflow_status": "failed",
                "steps": {
                    "3_deployment": {
                        "status": "failed",
                        "result": {
                            "error": "Command timed out after 120 seconds",
                            "suggestion": "Try manual deployment"
                        }
                    }
                },
                "message": "Deployment timed out"
            }
        
        if result.returncode == 0:
            # Parse output for monitor URL
            monitor_url = None
            monitor_id = None
            
            for line in result.stdout.split('\n'):
                if 'app/synthetics/monitor/' in line:
                    url_match = re.search(r'https://[^\s]+/app/synthetics/monitor[^\s]+', line)
                    if url_match:
                        monitor_url = url_match.group(0).replace('//app/synthetics', '/app/synthetics')
                elif any(phrase in line.lower() for phrase in ['monitor id', 'created monitor']):
                    id_match = re.search(r'[a-f0-9-]{36}', line)
                    if id_match:
                        monitor_id = id_match.group(0)
            
            if not monitor_url:
                monitor_url = f"{kibana_url}/app/synthetics"
            
            print(f"✅ Deployment successful! Monitor URL: {monitor_url}")
            
            return {
                "workflow_status": "completed",
                "steps": {
                    "1_connection": {
                        "status": "success",
                        "result": {"message": "Environment variables detected"}
                    },
                    "2_test_creation": {
                        "status": "success", 
                        "result": {
                            "message": "LLM test file created successfully",
                            "test_file": test_file_path,
                            "test_name": test_name
                        }
                    },
                    "3_deployment": {
                        "status": "success",
                        "result": {
                            "message": "Test deployed successfully",
                            "monitor_url": monitor_url,
                            "monitor_id": monitor_id,
                            "stdout": result.stdout
                        }
                    }
                },
                "test_file": test_file_path,
                "monitor_url": monitor_url,
                "message": f"Successfully deployed LLM test for {website_url}"
            }
        else:
            print(f"❌ Deployment failed with return code {result.returncode}")
            return {
                "workflow_status": "partial_success", 
                "steps": {
                    "1_connection": {
                        "status": "success",
                        "result": {"message": "Environment variables detected"}
                    },
                    "2_test_creation": {
                        "status": "success",
                        "result": {
                            "message": "LLM test file created successfully", 
                            "test_file": test_file_path,
                            "test_name": test_name
                        }
                    },
                    "3_deployment": {
                        "status": "failed",
                        "result": {
                            "error": result.stderr,
                            "stdout": result.stdout,
                            "push_command": " ".join(push_cmd)
                        }
                    }
                },
                "test_file": test_file_path,
                "message": "LLM test created but deployment failed"
            }
            
    except Exception as e:
        print(f"💥 Deployment exception: {e}")
        return {
            "workflow_status": "failed",
            "steps": {
                "3_deployment": {
                    "status": "failed",
                    "result": {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                }
            },
            "message": f"Deployment failed: {str(e)}"
        }

@mcp.tool()
def llm_create_and_deploy_test_from_prompt(
    prompt: str,
    website_url: str,
    test_name: str,
    test_description: Optional[str] = None,
    locations: Optional[List[str]] = None,
    schedule_minutes: int = 10,
    tags: Optional[List[str]] = None,
    working_directory: Optional[str] = None
) -> Dict[str, Any]:
    """
    Let an LLM WRITE the journey steps based on user prompt, wrap in a guarded template, save,
    then deploy WITHOUT calling create_and_deploy_browser_test (which would overwrite our LLM content).
    """
    try:
        print(f"🚀 Starting LLM test creation for: {test_name}")
        
        # Defaults / normalization
        if working_directory is None:
            working_directory = os.getcwd()
        if tags is None:
            tags = []
        if locations is None:
            locations = ["us_east"]
        locations = validate_elastic_locations(locations)
        
        print(f"✅ Basic setup completed")

        client, model = _get_llm()
        print(f"🔍 LLM client: {bool(client)}, model: {model}")
        
        context = _seed_context_for_llm(website_url)
        print(f"💡 Context: {context}")

        # Ask the LLM for step(...) blocks
        llm_raw = ""
        
        if client:
            print(f"🤖 Using LLM to generate test steps from user prompt: '{prompt}'")
            try:
                import random
                import time
                
                # Create more varied prompts by incorporating randomization
                random_seed = int(time.time() * 1000) % 10000
                random.seed(random_seed)
                
                # Vary the approach based on randomization
                approaches = [
                    "Focus on user interactions and form elements",
                    "Emphasize visual elements and layout verification", 
                    "Prioritize navigation and link testing",
                    "Check accessibility and semantic structure",
                    "Verify content and data display"
                ]
                random_approach = random.choice(approaches)
                
                # Build dynamic prompt using user's actual request
                enhanced_prompt = f"""You are writing Playwright test steps for: {website_url}

Website context: {context}
Testing approach: {random_approach}

User's specific request: {prompt}

Please generate 2-5 Playwright test steps that fulfill the user's request. Each step should:
- Use descriptive step names that explain what you're testing
- Use appropriate Playwright selectors (page.locator, getByRole, getByText, etc.)
- Include expect() assertions where appropriate
- Handle potential failures gracefully with try/catch where needed
- Be specific to the user's requirements

Example format:
step('Check for specific element', async () => {{
  const element = page.locator('selector');
  await expect(element).toBeVisible();
}});

Write ONLY the step() blocks, no imports or other content. Be creative and varied in your approach.
Randomization seed: {random_seed}"""
                
                msg = [
                    {"role": "system", "content": LLM_SYSTEM},
                    {"role": "user", "content": enhanced_prompt}
                ]
                
                # Use randomization to vary parameters
                temperature = random.uniform(0.7, 0.9)
                top_p = random.uniform(0.85, 0.95)
                
                resp = client.chat.completions.create(
                    model=model,
                    messages=msg,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=1200,
                    presence_penalty=random.uniform(0.1, 0.4),
                    frequency_penalty=random.uniform(0.1, 0.4)
                )
                llm_raw = resp.choices[0].message.content or ""
                print(f"✅ LLM generated {len(llm_raw)} chars (temp={temperature:.2f}, top_p={top_p:.2f})")
                print(f"🔍 LLM content: {llm_raw}")  # Show full content for debugging
                
            except Exception as e:
                print(f"❌ LLM call failed: {e}")
                llm_raw = ""
        else:
            print(f"⚠️  No LLM available, using enhanced fallback generator")
            llm_raw = generate_enhanced_dynamic_test_steps(website_url, prompt, test_name)

        print(f"🔍 Raw generated content length: {len(llm_raw)}")
        safe_steps = _sanitize_llm_steps(llm_raw)
        print(f"✅ Sanitized steps: {safe_steps}")

        # Compose full test file with LLM-generated steps
        test_name_clean = clean_string(test_name)
        website_url_clean = clean_string(website_url)
        tags_json = json.dumps(tags)
        file_safe = test_name_clean.lower().replace(" ", "_")
        
        full_ts = JOURNEY_TEMPLATE.format(
            TEST_NAME=test_name_clean,
            WEBSITE_URL=website_url_clean,
            TAGS_JSON=tags_json,
            SAFE_FILE=file_safe,
            LLM_STEPS=safe_steps
        )

        # Write LLM-generated test file
        test_dir = Path(working_directory) / "synthetic_tests"
        test_dir.mkdir(exist_ok=True)
        test_file_path = test_dir / f"{file_safe}.journey.ts"
        
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(full_ts)
        
        print(f"📝 Wrote LLM test file: {test_file_path}")
        print(f"📄 File contents:\n{full_ts}")

        # Deploy using our separate deployment function (won't overwrite the file)
        deploy_result = _deploy_test_file_only(
            test_file_path=str(test_file_path),
            website_url=website_url_clean,
            test_name=test_name_clean,
            locations=locations,
            schedule_minutes=schedule_minutes,
            working_directory=working_directory
        )

        return safe_json_response({
            "status": "success",
            "message": f"LLM test created from prompt: '{prompt}'",
            "llm_available": bool(client),
            "llm_model": model if client else None,
            "test_file": str(test_file_path),
            "user_prompt": prompt,
            "llm_steps_generated": safe_steps,
            "randomization_used": bool(client),
            "deploy_result": deploy_result,
            "full_test_content": full_ts  # Include for debugging
        })
        
    except Exception as e:
        return safe_json_response({
            "status": "error",
            "message": f"LLM create+deploy failed: {str(e)}",
            "error_type": type(e).__name__
        })
    
if __name__ == "__main__":
    mcp.run()