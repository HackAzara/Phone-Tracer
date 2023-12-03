import phonenumbers
import folium
import argparse
from phonenumbers import geocoder, timezone, carrier
from colorama import init, Fore
from termcolor import colored
from pyfiglet import Figlet
from opencage.geocoder import OpenCageGeocode
import os

init()

class PhoneNumberTracker:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.location = None
        self.latitude = None
        self.longitude = None
        self.coder = OpenCageGeocode("42c84373c47e490ba410d4132ae64fc4")

    def process_number(self):
        try:
            parsed_number = phonenumbers.parse(self.phone_number)
            print(f"{Fore.GREEN}[+] Attempting to track location of "
                  f"{phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}..")
            print(f"{Fore.GREEN}[+] Time Zone ID: {timezone.time_zones_for_number(parsed_number)}")
            self.location = geocoder.description_for_number(parsed_number, "en")
            if self.location:
                print(f"{Fore.GREEN}[+] Region: {self.location}")
            else:
                print(f"{Fore.RED}[-] Region: Unknown")

            if carrier.name_for_number(parsed_number, 'en'):
                print(f"{Fore.GREEN}[+] Service Provider: {carrier.name_for_number(parsed_number, 'en')}")
        except phonenumbers.NumberFormatException:
            raise ValueError("Please specify a valid phone number (with country code).")

    def get_approx_coordinates(self):
        try:
            results = self.coder.geocode(self.location)
            self.latitude = results[0]['geometry']['lat']
            self.longitude = results[0]['geometry']['lng']
            print(f"[+] Latitude: {self.latitude}, Longitude: {self.longitude}")
            address = self.coder.reverse_geocode(self.latitude, self.longitude)
            if address:
                address = address[0]['formatted']
                print(f"{Fore.LIGHTRED_EX}[+] Approximate Location is {address}")
            else:
                print(f"{Fore.RED}[-] No address found for the given coordinates.")
        except Exception:
            raise ValueError("Could not get the location of this number. Please specify a valid phone number or "
                             "check your internet connection.")

    @staticmethod
    def clean_phone_number(phone_number):
        cleaned = ''.join(char for part in phone_number for char in part if char.isdigit() or char == '+')
        return cleaned or "unknown"

    def draw_map(self):
        try:
            my_map = folium.Map(location=[self.latitude, self.longitude], zoom_start=9)
            folium.Marker([self.latitude, self.longitude], popup=self.location).add_to(my_map)
            cleaned_phone_number = self.clean_phone_number(self.phone_number)
            file_name = f"{cleaned_phone_number}.html"
            my_map.save(file_name)
            print(f"[+] See Aerial Coverage at: {os.path.abspath(file_name)}")
        except NameError:
            print(f"{Fore.RED}[-] Could not get Aerial coverage for this number. Please check the number again.")

def cli_argument():
    parser = argparse.ArgumentParser(description="Get approximate location of a Phone number.")
    parser.add_argument("-p", "--phone", dest="phone_number", type=str,
                        help="Phone number to track. Please include the country code when specifying the number.",
                        required=True, nargs="+")
    return parser.parse_args()

if __name__ == "__main__":
    big_figlet = Figlet(width=80, justify='center')
    big_text = big_figlet.renderText("Phone  Tracer")
    print(colored(big_text, 'blue'))
    print(colored("                                            Information : ", 'red'))
    print(colored("                                            ToolName: Phone Tracer", 'red'))
    print(colored("                                            Author: HackAzara", 'red'))
    print(colored("                                            Copyright: HackAzara (2023)", 'red'))
    print(colored("                                            Email: h4ckazara@gmail.com"))
    print(colored("                                            Github : https://github.com/HackAzara", 'red'))
    print(colored("                                            Telegram : t.me/hackAzara", 'red'))
    print(colored("                                            Description: Phone Tracer is a tool for locating phone numbers\n", 'red'))

    args = cli_argument()
    tracker = PhoneNumberTracker("".join(args.phone_number))
    try:
        tracker.process_number()
        tracker.get_approx_coordinates()
        tracker.draw_map()
    except ValueError as e:
        print(f"{Fore.RED}[-] {str(e)}")
