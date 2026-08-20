from urllib.parse import urlparse

def generate_csp(sources):
    """Generate safe CSP from discovered sources"""
    domains = set()
    
    # Extract domains from all sources
    for source_type in ['script', 'style']:
        for url in sources[source_type]:
            domain = urlparse(url).netloc
            if domain and not domain.startswith('localhost'):
                domains.add(domain)
    
    # Build CSP
    script_src = "'self'" + (f" {' '.join(domains)}" if domains else "")
    style_src = "'self'" + (f" {' '.join(domains)}" if domains else "")
    
    csp = (
        f"default-src 'self'; "
        f"script-src {script_src}; "
        f"style-src {style_src}; "
        f"img-src 'self' data: https:; "
        f"object-src 'none'; "
        f"frame-ancestors 'none'"
    )
    
    return csp

def csp_quality_score(csp_string):
    """Score CSP safety (0-100)"""
    if not csp_string:
        return 0
    
    score = 50
    bad_patterns = ['unsafe-inline', '*', 'unsafe-eval']
    
    for pattern in bad_patterns:
        if pattern in csp_string.lower():
            score -= 25
    
    if any(good in csp_string.lower() for good in ['nonce-', "'strict-dynamic'"]):
        score += 20
    
    return min(100, max(0, score))
