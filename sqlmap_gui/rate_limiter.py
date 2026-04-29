"""
Rate limiting and stealth mode functionality
"""

import random
import threading
import time
from typing import List


class RateLimiter:
    def __init__(self, requests_per_second: float = 1.0, random_delay: bool = True):
        self.requests_per_second = requests_per_second
        self.random_delay = random_delay
        self.min_delay = 1.0 / requests_per_second if requests_per_second > 0 else 0
        self.last_request_time = 0
        self.lock = threading.Lock()

    def wait(self):
        """Wait before next request"""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_request_time

            if self.random_delay:
                delay = self.min_delay * random.uniform(0.5, 1.5)
            else:
                delay = self.min_delay

            if elapsed < delay:
                time.sleep(delay - elapsed)

            self.last_request_time = time.time()

    def set_rate(self, requests_per_second: float):
        """Update rate limit"""
        with self.lock:
            self.requests_per_second = requests_per_second
            self.min_delay = 1.0 / requests_per_second if requests_per_second > 0 else 0


class UserAgentRotator:
    """Rotate user agents for stealth"""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0",
    ]

    def __init__(self):
        self.index = 0
        self.lock = threading.Lock()

    def get_next(self) -> str:
        """Get next user agent in rotation"""
        with self.lock:
            ua = self.USER_AGENTS[self.index]
            self.index = (self.index + 1) % len(self.USER_AGENTS)
            return ua

    def get_random(self) -> str:
        """Get random user agent"""
        return random.choice(self.USER_AGENTS)


class ProxyRotator:
    """Rotate through proxy list"""

    def __init__(self, proxies: List[str] = None):
        self.proxies = proxies or []
        self.index = 0
        self.lock = threading.Lock()

    def add_proxy(self, proxy: str):
        """Add proxy to rotation"""
        with self.lock:
            if proxy not in self.proxies:
                self.proxies.append(proxy)

    def get_next(self) -> str:
        """Get next proxy in rotation"""
        with self.lock:
            if not self.proxies:
                return None
            proxy = self.proxies[self.index]
            self.index = (self.index + 1) % len(self.proxies)
            return proxy

    def get_random(self) -> str:
        """Get random proxy"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def remove_proxy(self, proxy: str):
        """Remove proxy from rotation"""
        with self.lock:
            if proxy in self.proxies:
                self.proxies.remove(proxy)
                if self.index >= len(self.proxies):
                    self.index = 0


def build_stealth_options(
    rate_limit: float = None,
    user_agent_rotation: bool = False,
    random_delays: bool = False,
    proxy: str = None,
) -> List[str]:
    """Build sqlmap options for stealth mode"""
    options = []

    if rate_limit:
        delay = 1.0 / rate_limit
        if random_delays:
            delay *= random.uniform(0.8, 1.2)
        options.extend(["--delay", str(int(delay))])

    if user_agent_rotation:
        ua_rotator = UserAgentRotator()
        options.extend(["--user-agent", ua_rotator.get_random()])

    if random_delays:
        options.append("--randomize=user-agent,referer")

    if proxy:
        options.extend(["--proxy", proxy])

    # Additional stealth options
    options.extend(
        [
            "--threads",
            "1",  # Single thread for stealth
            "--timeout",
            "30",  # Longer timeout
            "--retries",
            "2",  # Fewer retries
        ]
    )

    return options


# Global instances
rate_limiter = RateLimiter()
ua_rotator = UserAgentRotator()
proxy_rotator = ProxyRotator()
