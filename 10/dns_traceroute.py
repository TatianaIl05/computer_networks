import subprocess
import csv
import re
import socket


DOMAINS = ["google.com", "cloudflare.com", "youtube.com"]
MAX_HOPS = 50
TIMEOUT = 5


def dns_lookup(domain):
    ipv4_addresses = []
    try:
        ips = socket.gethostbyname_ex(domain)[2]
        for ip in ips:
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                ipv4_addresses.append(ip)
        return ipv4_addresses
    except Exception:
        return []


def traceroute(target, max_hops=30, timeout=3):
    hops = []
    try:
        cmd = ["traceroute", "-n", "-m", str(max_hops), "-w", str(timeout), target]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        for line in result.stdout.split('\n'):
            match = re.search(r'^\s*(\d+)\s+([\d\.]+|\*)\s+(.*)$', line)
            if match:
                hop_ip = match.group(2) if match.group(2) != '*' else None
                hops.append({
                    'hop': int(match.group(1)),
                    'ip': hop_ip,
                    'status': 'success' if hop_ip else 'timeout'
                })
        
        return hops
    except Exception:
        return []


def save_results(results, csv_filename="dns_traceroute_results.csv"):
    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['domain', 'ipv4_addresses', 'selected_ip', 'traceroute_summary', 
                                                     'total_hops', 'last_hop_ip'], delimiter=',')
        
        writer.writeheader()
        writer.writerows(results)


def main():
    results = []
    for domain in DOMAINS:
        ipv4_addresses = dns_lookup(domain)
        if not ipv4_addresses:
            results.append({'domain': domain, 'ipv4_addresses': 'N/A', 'selected_ip': 'N/A', 'traceroute_summary': 'DNS lookup failed', 
                            'total_hops': 0, 'last_hop_ip': 'N/A'})
            continue
        
        all_ips = ", ".join(ipv4_addresses[:5])
        if len(ipv4_addresses) > 5:
            all_ips += f" и ещё {len(ipv4_addresses) - 5}"
        
        target_ip = ipv4_addresses[0]
        hops = traceroute(target_ip, MAX_HOPS, TIMEOUT)
        
        if not hops:
            results.append({'domain': domain, 'ipv4_addresses': all_ips, 'selected_ip': target_ip, 'traceroute_summary': 'Traceroute failed', 
                            'total_hops': 0, 'last_hop_ip': 'N/A'})
            continue
        
        last_success = None
        for hop in reversed(hops):
            if hop['ip']:
                last_success = hop
                break
        
        route_details = [f"{hop['hop']}:{hop['ip']}" for hop in hops if hop['ip']]
        results.append({
            'domain': domain,
            'ipv4_addresses': all_ips,
            'selected_ip': target_ip,
            'traceroute_summary': " -> ".join(route_details),
            'total_hops': len(hops),
            'last_hop_ip': last_success['ip'] if last_success else 'N/A'
        })
    
    save_results(results)


if __name__ == "__main__":
    main()
