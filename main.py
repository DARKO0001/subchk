import requests
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor
import time

init(autoreset=True)


def format_url(url):
    if not url.startswith(("http://", "https://")):
        return "http://" + url
    return url


def check_subdomain(url, output_file):
    url = format_url(url)
    try:
        response = requests.get(url, timeout=5)
        status_code = response.status_code
    except requests.RequestException:
        status_code = "Error"

    
    if status_code == 200:
        color = Fore.GREEN
    elif status_code == 404:
        color = Fore.RED
    elif status_code == 403:
        color = Fore.YELLOW
    else:
        color = Fore.CYAN

    
    print(f"{color}{status_code}{Style.RESET_ALL} - {url}")

   
    output_file.write(f"{status_code} - {url}\n")


def main():
     
    try:
        num_threads = int(input("Enter the number of threads (default 10): "))
    except ValueError:
        num_threads = 10 

    print(f"Using {num_threads} threads for parallel processing...\n")
    start_time = time.time()
    print(f"""
{Fore.GREEN}    .▄▄ · ▄• ▄▌▄▄▄▄·  ▄▄·  ▄ .▄▄ •▄ {Style.RESET_ALL}
{Fore.GREEN}    ▐█ ▀. █▪██▌▐█ ▀█▪▐█ ▌▪██▪▐██▌▄▌▪{Style.RESET_ALL}
{Fore.GREEN}    ▄▀▀▀█▄█▌▐█▌▐█▀▀█▄██ ▄▄██▀▐█▐▀▀▄·{Style.RESET_ALL}
{Fore.RED}    ▐█▄▪▐█▐█▄█▌██▄▪▐█▐███▌██▌▐▀▐█.█▌{Style.RESET_ALL}
{Fore.RED}     ▀▀▀▀  ▀▀▀ ·▀▀▀▀ ·▀▀▀ ▀▀▀ ··▀  ▀{Style.RESET_ALL}
{Fore.RED}                                                                                
{Style.RESET_ALL}
                                               subchk ~ 𝙀𝙂𝘿𝙖𝙧𝙠𝙤  """)
    print(f"{Fore.RED}!notice You should put the subdomains list in : subdomains.txt{Style.RESET_ALL}")
    print("Tool started.... ")

     
    with open("output_results.txt", "w") as output_file:
        with open("subdomains.txt", "r") as subs:
           
            subdomains = [line.strip() for line in subs]
            
            with ThreadPoolExecutor(max_workers=num_threads) as executor: 
                
                executor.map(lambda url: check_subdomain(url, output_file), subdomains)
    end_time = time.time()
    elapsed_time = end_time - start_time  
    print("Scan Finished. Results saved to 'output_results.txt'")
    print(f"Execution Time: {elapsed_time:.2f} seconds")

main()
