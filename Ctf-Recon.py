import os
import subprocess
import sys
import time

print("#####################################################################################")
print("#                                                                                   #")
print("#                                   CTF-RECON                                       #")
print("#                                                                                   #")
print("#####################################################################################")
print("#                                                                                   #")
print("#  Author: Eyal Zabarsky                                                            #")
print("#  Date:   04/2023                                                                  #")
print("#  Description: ALL RIGHTS RESERVED                                                 #")
print("#                                                                                   #")
print("#####################################################################################")


def print_yellow(text):
    print("\033[33m{}\033[0m".format(text))

def print_green(text):
    print("\033[32m{}\033[0m".format(text))


def print_red(text):
    print("\033[31m{}\033[0m".format(text))


def get_ip_address(url):
    if url.startswith("http://") or url.startswith("https://"):
        print_red("Please enter the IP address instead of the URL or remove http:// or https:// from the beginning of the URL.")
        url = input("Enter the IP address or Url without the http:// : ")
    return url


def check_root():
    if os.geteuid() != 0:
        print_red("This script must be run as root.")
        sys.exit(1)


def create_nmap_directory():
    if not os.path.exists("nmap"):
        os.mkdir("nmap")


def initial_nmap_scan(ip):
    print_red("START INITAL NMAP SCAN -- PLEASE BE PATIENT")
    result = subprocess.run(["nmap", "-sV", "-sC", "-vv", "-T4", ip, "-oN", "nmap/inital"])
    if result.returncode != 0:
        print_red("There was an error running the initial Nmap scan.")
        sys.exit(1)
    print_green("INITAL NMAP SCAN DONE, SAVED UNDER NMAP DIRECTORY")


def full_nmap_scan(ip):
    response = input("Do you want to perform a full Nmap scan? [y/n]: ")
    if response.lower() == "y":
        print("STARTING FULL NMAP SCAN")
        result = subprocess.run(["nmap", "-sV", "-sC", "-vv", "-p-", "T4",  ip, "-oN", "nmap/allports"])
        if result.returncode != 0:
            print_red("There was an error running the full Nmap scan.")
        else:
            print_green("FULL NMAP SCAN DONE, SAVED UNDER NMAP DIRECTORY")


def fuzz_website(url):
    response = input("Do you want to use the default wordlist? [y/n]: ")
    if response.lower() == "y":
        directorylist = "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
    else:
        directorylist = input("Enter the directory path for the wordlist: ")
    if not os.path.exists("gobuster"):
        os.mkdir("gobuster")
    else:
        response = input("The gobuster directory already exists. Do you want to replace its contents? [y/n]: ")
        if response.lower() == "y":
            os.system("rm -rf gobuster")
            os.mkdir("gobuster")
    print("Starting Fuzzing the website with gobuster")
    try:
        result = subprocess.run(["gobuster", "dir", "-u", url, "-w", directorylist, "-x", "php,html,zip,tar,bak,txt,asp,aspx,py", "-t", "50", "-o", "gobuster/gobuster-site"])
    except subprocess.CalledProcessError as error:
        if "invalid argument" in str(error) and "for \"-sC, --script\"" in str(error):
            print_yellow("Skipping status code and length checks")
            result = subprocess.run(["gobuster", "dir", "-u", url, "-w", directorylist, "-x", "php,html,zip,tar,bak,txt,asp,aspx,py", "-t", "50", "-o", "gobuster/gobuster-site", "--wildcard"])
        else:
            print_red("There was an error running the gobuster command.")
            sys.exit(1)
    print_green("GOBUSTER IS DONE - PLEASE CHECK GOBUSTER DIRECTORY")


def main():
    check_root()
    url = input("\033[32mEnter the IP address: \033[0m")
    ip = get_ip_address(url)
    create_nmap_directory()
    initial_nmap_scan(ip)
    full_nmap_scan(ip)
    time.sleep(2)
    fuzz_website(url)
    print_green("DONE, PLEASE CHECK THE RESULTS")


if __name__ == "__main__":
    main()
