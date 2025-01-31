import requests
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
from queue import Queue

init(autoreset=True)

thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

def format_url(url):
    if not url.startswith(("http://", "https://")):
        return "http://" + url
    return url

def check_subdomain(url, result_queue):
    session = get_session()
    url = format_url(url)
    status_code = "Error"
    color = Fore.CYAN
    
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = session.get(url, timeout=5)
            status_code = response.status_code
            break
        except requests.RequestException:
            if attempt < 2:
                time.sleep(1)
                continue
            else:
                status_code = "Error"
    
    if status_code == 200:
        color = Fore.GREEN
    elif status_code == 404:
        color = Fore.RED
    elif status_code == 403:
        color = Fore.YELLOW
    
    result_queue.put((status_code, url, color))

def writer_thread(output_file, result_queue):
    while True:
        item = result_queue.get()
        if item is None:  # Stop signal
            break
        status_code, url, color = item
        print(f"{color}{status_code}{Style.RESET_ALL} - {url}")
        output_file.write(f"{status_code} - {url}\n")
        result_queue.task_done()

def main():
    while True:
        try:
            num_threads = int(input("Enter the number of threads (default 50) - (MAX 100): "))
            if num_threads > 100:
                print(f"{Fore.RED}!Maximum Threads 100{Style.RESET_ALL}")
                continue
            else:
                break
        except ValueError:
            num_threads = 50
            break

    print(f"\nUsing {num_threads} threads for parallel processing...")
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
    print(f"{Fore.RED}!notice You should put the subdomains list in: subdomains.txt{Style.RESET_ALL}")
    print("Tool started....\n")

    try:
        with open("subdomains.txt", "r") as f:
            subdomains = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.RED}Error: subdomains.txt file not found!{Style.RESET_ALL}")
        return

    with open("output_results.txt", "w") as output_file:
        result_queue = Queue()
        writer = threading.Thread(target=writer_thread, args=(output_file, result_queue))
        writer.start()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(check_subdomain, url, result_queue) for url in subdomains]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"{Fore.RED}Error processing task: {e}{Style.RESET_ALL}")

        # Signal writer thread to exit
        result_queue.put(None)
        writer.join()

    end_time = time.time()
    print(f"\n{Fore.GREEN}Scan finished. Results saved to 'output_results.txt'{Style.RESET_ALL}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
