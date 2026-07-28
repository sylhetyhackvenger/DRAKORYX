#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════
#  DRAKORYX - CDN REVELATOR
#  ⚡ Cybernetic Network Analysis Tool ⚡
#  Author: SYLHETYHACKVENGER (THE-ERROR808)
#  ═══════════════════════════════════════════════════════════════════════════

import ipaddress
import sys
import socket
import click
import re
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple, Dict, Any
from colorama import init, Fore, Back, Style
from datetime import datetime

# Initialize colorama for cross-platform color support
init(autoreset=True)

# ═══════════════════════════════════════════════════════════════════════════
#  CONFIGURATION MATRIX
# ═══════════════════════════════════════════════════════════════════════════

class Config:
    """Quantum configuration parameters for the Drakoryx engine"""
    BUILD = "NEXUS-808"
    API_TIMEOUT = 5
    MAX_RETRIES = 3
    CACHE_DURATION = 300
    MAX_THREADS = 100
    DEFAULT_THREADS = 20

    # Cyberpunk color palette
    COLORS = {
        'primary': Fore.CYAN,
        'success': Fore.GREEN,
        'warning': Fore.YELLOW,
        'danger': Fore.RED,
        'info': Fore.BLUE,
        'purple': Fore.MAGENTA,
        'white': Fore.WHITE,
        'reset': Style.RESET_ALL,
        'dim': Style.DIM,
        'bright': Style.BRIGHT
    }

    # CDN Provider Endpoints
    CDN_SOURCES = {
        'cloudflare': "https://www.cloudflare.com/ips-v4",
        'cloudfront': "https://d7uri8nf7uskq.cloudfront.net/tools/list-cloudfront-ips",
        'fastly': "https://api.fastly.com/public-ip-list",
        'akamai': "https://api.akamai.com/ips/v1/ips.json"
    }

    # CDN Provider Headers for detection
    CDN_PROVIDERS = {
        'cloudflare': ['cf-', 'cloudflare', 'cf-ray'],
        'cloudfront': ['x-amz-cf', 'cloudfront', 'x-cache'],
        'fastly': ['fastly', 'x-served-by', 'x-cache-hits'],
        'akamai': ['akamai', 'x-akamai', 'x-edge']
    }

# ═══════════════════════════════════════════════════════════════════════════
#  NEURAL PATTERN RECOGNITION
# ═══════════════════════════════════════════════════════════════════════════

class PatternMatrix:
    """Advanced pattern recognition for network entities"""

    IP_PATTERN = re.compile(
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}"
        r"(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\b"
    )

    DOMAIN_PATTERN = re.compile(
        r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]"
    )

    CDN_HEADERS = re.compile(
        r"(?:cf-|cloudflare|x-amz-cf|x-cache|akamai|fastly|x-served-by|x-akamai)",
        re.IGNORECASE
    )

# ═══════════════════════════════════════════════════════════════════════════
#  DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class NetworkEntity:
    """Quantum data container for network entities"""
    identifier: str
    entity_type: str
    cdn_status: bool
    provider: Optional[str] = None
    reverse_dns: Optional[str] = None
    resolved_ips: Optional[List[str]] = None
    response_time: Optional[float] = None
    confidence_score: float = 1.0
    timestamp: str = datetime.now().isoformat()

class CyberNetwork:
    """Advanced network analysis engine"""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.networks = self._build_quantum_networks()
        self.cache = {}
        self.stats = {
            'total_scanned': 0,
            'proxied': 0,
            'unproxied': 0,
            'errors': 0,
            'start_time': datetime.now().isoformat()
        }
        self.provider_cache = {}

    def _log(self, message: str, level: str = "info"):
        if not self.verbose:
            return

        icons = {
            'info': 'ℹ',
            'success': '✓',
            'warning': '⚠',
            'error': '✗',
            'debug': '🔍'
        }

        colors = {
            'info': Config.COLORS['info'],
            'success': Config.COLORS['success'],
            'warning': Config.COLORS['warning'],
            'error': Config.COLORS['danger'],
            'debug': Config.COLORS['dim']
        }

        print(f"{colors.get(level, Config.COLORS['white'])}{icons.get(level, '•')} {message}{Config.COLORS['reset']}")

    def _build_quantum_networks(self) -> List[ipaddress.ip_network]:
        networks = []

        self._log("Initializing quantum network matrix...", "info")

        for provider, url in Config.CDN_SOURCES.items():
            try:
                self._log(f"Fetching {provider.upper()} network ranges...", "debug")
                response = requests.get(url, timeout=Config.API_TIMEOUT)

                if response.status_code != 200:
                    self._log(f"Failed to fetch {provider}: HTTP {response.status_code}", "warning")
                    continue

                if provider == 'cloudfront':
                    cidrs = self._parse_cloudfront_response(response)
                elif provider == 'cloudflare':
                    cidrs = self._parse_cloudflare_response(response)
                elif provider == 'fastly':
                    cidrs = self._parse_fastly_response(response)
                elif provider == 'akamai':
                    cidrs = self._parse_akamai_response(response)
                else:
                    continue

                count = 0
                for cidr in cidrs:
                    try:
                        networks.append(ipaddress.ip_network(cidr, strict=False))
                        count += 1
                    except ValueError:
                        continue

                self._log(f"Loaded {count} networks from {provider.upper()}", "success")

            except requests.exceptions.Timeout:
                self._log(f"Timeout loading {provider}", "error")
            except Exception as e:
                self._log(f"Error loading {provider}: {str(e)}", "error")

        self._log(f"Total quantum networks loaded: {len(networks)}", "success")
        return networks

    def _parse_cloudfront_response(self, response) -> List[str]:
        try:
            data = response.json()
            return data.get("CLOUDFRONT_GLOBAL_IP_LIST", []) + \
                   data.get("CLOUDFRONT_REGIONAL_EDGE_IP_LIST", [])
        except:
            return []

    def _parse_cloudflare_response(self, response) -> List[str]:
        return response.text.strip().split("\n")

    def _parse_fastly_response(self, response) -> List[str]:
        try:
            data = response.json()
            return data.get("addresses", [])
        except:
            return []

    def _parse_akamai_response(self, response) -> List[str]:
        try:
            data = response.json()
            return data.get("ipv4", [])
        except:
            return []

    def analyze_entity(self, entity: str) -> NetworkEntity:
        self.stats['total_scanned'] += 1

        clean_entity = entity.strip().replace("https://", "").replace("http://", "").replace("www.", "")

        if PatternMatrix.IP_PATTERN.fullmatch(clean_entity):
            if self.verbose:
                self._log(f"Analyzing IP: {clean_entity}", "debug")
            return self._analyze_ip(clean_entity)
        elif PatternMatrix.DOMAIN_PATTERN.fullmatch(clean_entity):
            if self.verbose:
                self._log(f"Analyzing Domain: {clean_entity}", "debug")
            return self._analyze_domain(clean_entity)
        else:
            self._log(f"Invalid entity format: {clean_entity}", "error")
            return NetworkEntity(
                identifier=clean_entity,
                entity_type='unknown',
                cdn_status=False,
                confidence_score=0.0
            )

    def _analyze_ip(self, ip: str) -> NetworkEntity:
        start_time = time.time()

        try:
            is_proxied = self._check_ip_in_cdn(ip)

            reverse_dns = None
            try:
                reverse_dns, _, _ = socket.gethostbyaddr(ip)
                if self.verbose:
                    self._log(f"Reverse DNS found: {reverse_dns}", "debug")
            except socket.error:
                if self.verbose:
                    self._log(f"No reverse DNS for {ip}", "debug")

            provider = self._identify_provider_enhanced(ip, reverse_dns)

            response_time = (time.time() - start_time) * 1000

            entity = NetworkEntity(
                identifier=ip,
                entity_type='ip',
                cdn_status=is_proxied,
                provider=provider,
                reverse_dns=reverse_dns,
                response_time=response_time
            )

            if is_proxied:
                self.stats['proxied'] += 1
                if self.verbose:
                    self._log(f"IP {ip} is CDN proxied via {provider or 'Unknown'}", "info")
            else:
                self.stats['unproxied'] += 1
                if self.verbose:
                    self._log(f"IP {ip} is direct (not proxied)", "info")

            return entity

        except Exception as e:
            self.stats['errors'] += 1
            self._log(f"Error analyzing IP {ip}: {str(e)}", "error")
            return NetworkEntity(
                identifier=ip,
                entity_type='ip',
                cdn_status=False,
                confidence_score=0.0
            )

    def _analyze_domain(self, domain: str) -> NetworkEntity:
        start_time = time.time()

        try:
            ips = socket.gethostbyname_ex(domain)[2]
            if self.verbose:
                self._log(f"Domain {domain} resolved to {len(ips)} IPs", "debug")

            proxied_ips = []
            direct_ips = []
            providers = []

            for ip in ips:
                if self._check_ip_in_cdn(ip):
                    proxied_ips.append(ip)
                    provider = self._identify_provider_enhanced(ip, None)
                    if provider and provider not in providers:
                        providers.append(provider)
                else:
                    direct_ips.append(ip)

            is_proxied = len(proxied_ips) > 0
            provider = providers[0] if providers else None

            if is_proxied:
                self._log(f"Domain {domain} is CDN protected via {provider or 'Unknown CDN'}", "info")
                if direct_ips:
                    self._log(f"  But {len(direct_ips)} IPs are direct: {', '.join(direct_ips[:3])}", "warning")
            else:
                self._log(f"Domain {domain} is not CDN protected", "info")

            response_time = (time.time() - start_time) * 1000

            entity = NetworkEntity(
                identifier=domain,
                entity_type='domain',
                cdn_status=is_proxied,
                provider=provider,
                reverse_dns=None,
                resolved_ips=ips,
                response_time=response_time
            )

            if is_proxied:
                self.stats['proxied'] += 1
            else:
                self.stats['unproxied'] += 1

            return entity

        except socket.gaierror as e:
            self.stats['errors'] += 1
            self._log(f"Domain resolution failed for {domain}: {str(e)}", "error")
            return NetworkEntity(
                identifier=domain,
                entity_type='domain',
                cdn_status=False,
                confidence_score=0.0
            )
        except Exception as e:
            self.stats['errors'] += 1
            self._log(f"Error analyzing domain {domain}: {str(e)}", "error")
            return NetworkEntity(
                identifier=domain,
                entity_type='domain',
                cdn_status=False,
                confidence_score=0.0
            )

    def _check_ip_in_cdn(self, ip: str) -> bool:
        try:
            ip_addr = ipaddress.ip_address(ip)
            for network in self.networks:
                if ip_addr in network:
                    return True
            return False
        except ValueError:
            return False

    def _identify_provider_enhanced(self, ip: str, reverse_dns: Optional[str] = None) -> Optional[str]:
        if ip in self.provider_cache:
            return self.provider_cache[ip]

        provider = None

        if reverse_dns:
            reverse_dns_lower = reverse_dns.lower()
            for cdn_name, patterns in Config.CDN_PROVIDERS.items():
                for pattern in patterns:
                    if pattern in reverse_dns_lower:
                        provider = cdn_name.capitalize()
                        break
                if provider:
                    break

        if not provider:
            try:
                ip_addr = ipaddress.ip_address(ip)
                provider_names = list(Config.CDN_SOURCES.keys())
                for i, network in enumerate(self.networks):
                    if ip_addr in network:
                        provider = provider_names[i % len(provider_names)].capitalize()
                        break
            except:
                pass

        self.provider_cache[ip] = provider
        return provider

# ═══════════════════════════════════════════════════════════════════════════
#  VISUAL DISPLAY ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class HolographicDisplay:
    """Advanced holographic UI renderer"""

    @staticmethod
    def render_entity(entity: NetworkEntity):
        if entity.cdn_status:
            status = f"{Fore.YELLOW}⚡ PROXIED {Style.BRIGHT}{Fore.YELLOW}◈{Style.RESET_ALL}"
        else:
            status = f"{Fore.GREEN}✦ DIRECT {Style.BRIGHT}{Fore.GREEN}◈{Style.RESET_ALL}"

        type_icon = "🌐" if entity.entity_type == 'domain' else "📡"

        display_parts = [
            f"{Fore.CYAN}┃{Style.RESET_ALL}",
            status,
            f"{Fore.CYAN}┃{Style.RESET_ALL}",
            f"{Fore.MAGENTA}{type_icon}{Style.RESET_ALL}",
            f"{Fore.WHITE}{entity.identifier}{Style.RESET_ALL}"
        ]

        if entity.provider:
            display_parts.extend([
                f"{Fore.CYAN}┃{Style.RESET_ALL}",
                f"{Fore.BLUE}⧫ {entity.provider}{Style.RESET_ALL}"
            ])

        if entity.reverse_dns:
            display_parts.extend([
                f"{Fore.CYAN}┃{Style.RESET_ALL}",
                f"{Style.DIM}↳ {entity.reverse_dns}{Style.RESET_ALL}"
            ])

        if entity.resolved_ips:
            ip_display = ', '.join(entity.resolved_ips[:3])
            if len(entity.resolved_ips) > 3:
                ip_display += f" ... (+{len(entity.resolved_ips)-3} more)"
            display_parts.extend([
                f"{Fore.CYAN}┃{Style.RESET_ALL}",
                f"{Style.DIM}⇢ {ip_display}{Style.RESET_ALL}"
            ])

        if entity.response_time:
            time_color = Fore.GREEN if entity.response_time < 100 else Fore.YELLOW
            display_parts.extend([
                f"{Fore.CYAN}┃{Style.RESET_ALL}",
                f"{time_color}⏱ {entity.response_time:.2f}ms{Style.RESET_ALL}"
            ])

        if entity.confidence_score < 1.0:
            confidence_icon = "⚠" if entity.confidence_score < 0.5 else "◈"
            confidence_color = Fore.RED if entity.confidence_score < 0.5 else Fore.YELLOW
            display_parts.extend([
                f"{Fore.CYAN}┃{Style.RESET_ALL}",
                f"{confidence_color}{confidence_icon} {entity.confidence_score:.1%}{Style.RESET_ALL}"
            ])

        print(" ".join(display_parts))

    @staticmethod
    def render_header():
        """Clean header without ASCII banner"""
        print(f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.BRIGHT}{Fore.WHITE}  🚀 DRAKORYX - CDN Revelator v{Config.BUILD}{Fore.CYAN}                          ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.DIM}  ⚡ Cybernetic Network Analysis Tool{Fore.CYAN}                                    ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.DIM}  👾 Author: SYLHETYHACKVENGER (THE-ERROR808){Fore.CYAN}                        ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")

        print(f"\n{Style.DIM}  ⚙ Mode: {Fore.GREEN}VERBOSE{Style.DIM} | Detection: {Fore.GREEN}ACTIVE{Style.RESET_ALL}")
        print(f"{Style.DIM}  📡 CDN Providers: {', '.join([p.capitalize() for p in Config.CDN_SOURCES.keys()])}{Style.RESET_ALL}\n")

    @staticmethod
    def render_footer(stats: dict = None):
        """Clean footer"""
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.BRIGHT}{Fore.WHITE}  🔌 DRAKORYX - Scan Complete{Fore.CYAN}                                     ║{Style.RESET_ALL}")
        if stats:
            duration = (datetime.now() - datetime.fromisoformat(stats['start_time'])).total_seconds()
            print(f"{Fore.CYAN}║{Style.DIM}  ⏱ Duration: {duration:.2f}s | Scanned: {stats['total_scanned']} | Proxied: {stats['proxied']}{Fore.CYAN}   ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.DIM}  🛡️  Stay secure, netrunner!{Fore.CYAN}                                            ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")

    @staticmethod
    def render_stats(stats: dict):
        duration = (datetime.now() - datetime.fromisoformat(stats['start_time'])).total_seconds()

        print(f"\n{Fore.CYAN}┌─────────────────────────────────────────────────────────────┐{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.BRIGHT}{Fore.WHITE}  📊 SCAN STATISTICS {Style.RESET_ALL}")
        print(f"{Fore.CYAN}├─────────────────────────────────────────────────────────────┤{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│  {Fore.WHITE}⏱ Duration: {Fore.CYAN}{duration:.2f}s")
        print(f"{Fore.CYAN}│  {Fore.WHITE}📌 Total Scanned: {Fore.CYAN}{stats['total_scanned']}")
        if stats['total_scanned'] > 0:
            print(f"{Fore.CYAN}│  {Fore.YELLOW}🟠 Proxied: {Fore.YELLOW}{stats['proxied']} ({stats['proxied']/stats['total_scanned']*100:.1f}%)")
            print(f"{Fore.CYAN}│  {Fore.GREEN}🟢 Unproxied: {Fore.GREEN}{stats['unproxied']} ({stats['unproxied']/stats['total_scanned']*100:.1f}%)")
        print(f"{Fore.CYAN}│  {Fore.RED}⚠ Errors: {Fore.RED}{stats['errors']}")

        if stats['total_scanned'] > 0:
            success_rate = (stats['total_scanned'] - stats['errors']) / stats['total_scanned'] * 100
            rate_color = Fore.GREEN if success_rate > 90 else Fore.YELLOW if success_rate > 70 else Fore.RED
            print(f"{Fore.CYAN}│  {Fore.WHITE}💯 Success Rate: {rate_color}{success_rate:.1f}%")
        print(f"{Fore.CYAN}└─────────────────────────────────────────────────────────────┘{Style.RESET_ALL}")

    @staticmethod
    def render_loading_animation():
        frames = ["◈", "◇", "◆", "◈", "◇", "◆"]
        print(f"\r{Fore.CYAN}Initializing neural network {Fore.YELLOW}{frames[0]}{Style.RESET_ALL}", end="")
        for i in range(6):
            time.sleep(0.1)
            print(f"\r{Fore.CYAN}Initializing neural network {Fore.YELLOW}{frames[i % len(frames)]}{Style.RESET_ALL}", end="")
        print("\r" + " " * 50 + "\r", end="")

# ═══════════════════════════════════════════════════════════════════════════
#  TARGET INPUT HANDLER
# ═══════════════════════════════════════════════════════════════════════════

def get_targets():
    """Get targets from stdin or interactive input"""
    targets = []

    # Check if there's piped input
    if not sys.stdin.isatty():
        for line in sys.stdin:
            clean_line = line.strip()
            if clean_line:
                targets.append(clean_line)
        return targets

    # Interactive mode
    print(f"{Fore.CYAN}┌─────────────────────────────────────────────────────────────┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.BRIGHT}{Fore.WHITE}  🎯 TARGET INPUT {Style.RESET_ALL}")
    print(f"{Fore.CYAN}├─────────────────────────────────────────────────────────────┤{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.DIM}  Enter targets (IPs or domains), one per line{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.DIM}  Press ENTER on empty line to start scanning{Style.RESET_ALL}")
    print(f"{Fore.CYAN}└─────────────────────────────────────────────────────────────┘{Style.RESET_ALL}\n")

    print(f"{Fore.GREEN}›{Style.RESET_ALL} Enter target (or empty to scan): ", end="")

    while True:
        try:
            target = input().strip()
            if not target:
                if targets:
                    break
                else:
                    print(f"{Fore.YELLOW}⚠ No targets entered. Please enter at least one target.{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}›{Style.RESET_ALL} Enter target: ", end="")
                    continue
            targets.append(target)
            print(f"{Fore.GREEN}›{Style.RESET_ALL} Enter target (or empty to scan): ", end="")
        except KeyboardInterrupt:
            print()
            return targets if targets else []
        except EOFError:
            break

    return targets

# ═══════════════════════════════════════════════════════════════════════════
#  MAIN ENGINE
# ═══════════════════════════════════════════════════════════════════════════

@click.command()
@click.option("-t", "--threads", default=Config.DEFAULT_THREADS, help="Number of parallel scanning threads")
@click.option("-o", "--output", help="Output file for results (JSON format)")
@click.option("--no-animation", is_flag=True, help="Disable loading animation")
@click.option("--quiet", is_flag=True, help="Reduce output verbosity")
@click.argument("targets", nargs=-1)
def main(threads: int, output: str, no_animation: bool, quiet: bool, targets: tuple):
    """
    DRAKORYX - Advanced CDN Detection Engine
    Scan IPs and domains to detect CDN protection (Cloudflare, CloudFront, Fastly, Akamai)

    Usage:
      # Interactive mode (will prompt for targets)
      python drakoryx.py

      # With arguments
      python drakoryx.py google.com cloudflare.com

      # Pipe input
      cat targets.txt | python drakoryx.py -t 50 -o results.json
    """

    verbose = not quiet

    HolographicDisplay.render_header()

    if not no_animation:
        HolographicDisplay.render_loading_animation()

    print(f"{Fore.CYAN}⧫ Connecting to CDN networks...{Style.RESET_ALL}")
    analyzer = CyberNetwork(verbose=verbose)

    # Collect targets from various sources
    all_targets = []

    # 1. From command line arguments
    if targets:
        all_targets.extend(targets)

    # 2. From pipe input
    if not sys.stdin.isatty():
        for line in sys.stdin:
            clean_line = line.strip()
            if clean_line:
                all_targets.append(clean_line)

    # 3. If no targets found, ask interactively
    if not all_targets:
        all_targets = get_targets()

    if not all_targets:
        print(f"{Fore.RED}⚠ No targets provided. Exiting...{Style.RESET_ALL}")
        return

    # Process and validate targets
    entities = []
    invalid_entities = []

    for target in all_targets:
        clean_target = target.strip().replace("https://", "").replace("http://", "").replace("www.", "")
        if clean_target:
            if PatternMatrix.IP_PATTERN.fullmatch(clean_target) or \
               PatternMatrix.DOMAIN_PATTERN.fullmatch(clean_target):
                entities.append(clean_target)
            else:
                invalid_entities.append(clean_target)

    if not entities:
        print(f"{Fore.RED}⚠ No valid entities found in input.{Style.RESET_ALL}")
        if invalid_entities:
            print(f"{Fore.YELLOW}⚠ Invalid entities: {', '.join(invalid_entities[:5])}{Style.RESET_ALL}")
        return

    if invalid_entities and verbose:
        print(f"\n{Fore.YELLOW}⚠ {len(invalid_entities)} invalid entities skipped:{Style.RESET_ALL}")
        for inv in invalid_entities[:3]:
            print(f"  {Fore.RED}✗ {inv}{Style.RESET_ALL}")
        if len(invalid_entities) > 3:
            print(f"  {Fore.RED}... and {len(invalid_entities) - 3} more{Style.RESET_ALL}")

    # Show what we're scanning
    print(f"\n{Fore.CYAN}┌─────────────────────────────────────────────────────────────┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.BRIGHT}{Fore.WHITE}  🔍 SCAN INITIATED {Style.RESET_ALL}")
    print(f"{Fore.CYAN}├─────────────────────────────────────────────────────────────┤{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.DIM}  Targets: {len(entities)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.DIM}  Threads: {min(threads, Config.MAX_THREADS)}{Style.RESET_ALL}")
    if output:
        print(f"{Fore.CYAN}│{Style.DIM}  Output: {output}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}└─────────────────────────────────────────────────────────────┘{Style.RESET_ALL}\n")

    results = []
    with ThreadPoolExecutor(max_workers=min(threads, Config.MAX_THREADS)) as executor:
        future_to_entity = {
            executor.submit(analyzer.analyze_entity, entity): entity
            for entity in entities
        }

        completed = 0
        for future in as_completed(future_to_entity):
            try:
                entity = future.result()
                HolographicDisplay.render_entity(entity)
                results.append(entity)
                completed += 1

                if verbose and completed % 10 == 0:
                    print(f"{Style.DIM}Progress: {completed}/{len(entities)} entities processed{Style.RESET_ALL}")

            except Exception as e:
                if verbose:
                    print(f"{Fore.RED}⚠ Error processing {future_to_entity[future]}: {str(e)}{Style.RESET_ALL}")
                analyzer.stats['errors'] += 1

    HolographicDisplay.render_stats(analyzer.stats)

    if output:
        try:
            results_dict = []
            for entity in results:
                entity_dict = asdict(entity)
                results_dict.append(entity_dict)

            output_data = {
                'build': Config.BUILD,
                'timestamp': datetime.now().isoformat(),
                'stats': analyzer.stats,
                'results': results_dict
            }

            with open(output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"{Fore.GREEN}✓ Results saved to {output}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}⚠ Error saving results: {str(e)}{Style.RESET_ALL}")

    # Render footer
    HolographicDisplay.render_footer(analyzer.stats)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠ Scan interrupted by user. Shutting down...{Style.RESET_ALL}")
        HolographicDisplay.render_footer()
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}⚠ Fatal error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
