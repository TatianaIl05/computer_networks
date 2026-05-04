import subprocess
import csv
import re
import socket
from datetime import datetime


DOMAINS = [
    "google.com",
    "cloudflare.com",
    "youtube.com"
]

MAX_HOPS = 40
TIMEOUT = 5 


def dns_lookup(domain):
    ipv4_addresses = []
    try:
        ips = socket.gethostbyname_ex(domain)[2]
        for ip in ips:
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                ipv4_addresses.append(ip)
        return ipv4_addresses
    except Exception as e:
        print(f"  Ошибка: {e}")
        return []


def traceroute(target, max_hops=30, timeout=3):
    hops = []
    try:
        cmd = ["traceroute", "-n", "-m", str(max_hops), "-w", str(timeout), target]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        lines = result.stdout.split('\n')
        
        for line in lines:
            match = re.search(r'^\s*(\d+)\s+([\d\.]+|\*)\s+(.*)$', line)
            if match:
                hop_num = int(match.group(1))
                hop_ip = match.group(2) if match.group(2) != '*' else None
                
                times = re.findall(r'([\d\.]+)\s+ms', line)
                times_ms = [float(t) for t in times]
                
                hops.append({
                    'hop': hop_num,
                    'ip': hop_ip,
                    'times': times_ms,
                    'status': 'success' if hop_ip else 'timeout'
                })
        
        return hops
    except Exception as e:
        print(f"  Ошибка при traceroute: {e}")
        return []


def format_times(times):
    if not times:
        return "timeout"
    return ", ".join([f"{t:.1f}ms" for t in times[:3]])


def main():
    results = []
    
    for _, domain in enumerate(DOMAINS, 1):
        ipv4_addresses = dns_lookup(domain)
        
        if not ipv4_addresses:
            results.append({
                'domain': domain,
                'ipv4_addresses': 'N/A',
                'selected_ip': 'N/A',
                'traceroute_hops': 'N/A',
                'traceroute_summary': 'DNS lookup failed',
                'total_hops': 0,
                'last_hop_ip': 'N/A',
                'last_hop_time': 'N/A',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            continue
        
        all_ips = ", ".join(ipv4_addresses[:5])
        if len(ipv4_addresses) > 5:
            all_ips += f" и ещё {len(ipv4_addresses) - 5}"
        
        target_ip = ipv4_addresses[0]
        
        hops = traceroute(target_ip, MAX_HOPS, TIMEOUT)
        
        if not hops:
            results.append({
                'domain': domain,
                'ipv4_addresses': all_ips,
                'selected_ip': target_ip,
                'traceroute_hops': 'N/A',
                'traceroute_summary': 'Traceroute failed',
                'total_hops': 0,
                'last_hop_ip': 'N/A',
                'last_hop_time': 'N/A',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            print()
            continue
        
        last_success = None
        for hop in reversed(hops):
            if hop['ip']:
                last_success = hop
                break
        
        route_str = ""
        route_details = []
        for hop in hops:
            if hop['ip']:
                times_str = format_times(hop['times'])
                route_details.append(f"{hop['hop']}:{hop['ip']}[{times_str}]")
                route_str = " -> ".join(route_details)
        
        results.append({
            'domain': domain,
            'ipv4_addresses': all_ips,
            'selected_ip': target_ip,
            'traceroute_hops': "; ".join([f"{h['hop']}:{h['ip'] or '*'}" for h in hops]),
            'traceroute_summary': route_str,
            'total_hops': len(hops),
            'last_hop_ip': last_success['ip'] if last_success else 'N/A',
            'last_hop_time': format_times(last_success['times']) if last_success else 'N/A',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        print()
    
    csv_filename = "dns_traceroute_results.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['domain', 'ipv4_addresses', 'selected_ip', 'traceroute_hops', 
                      'traceroute_summary', 'total_hops', 'last_hop_ip', 
                      'last_hop_time', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    main()
    
