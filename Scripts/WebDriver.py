import plistlib
import sys
import os
import time
import Downloader
import tempfile
import shutil
import subprocess
# Python-aware urllib stuff
if sys.version_info >= (3, 0):
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

class WebDriver:

    def __init__(self):
        self.dl = Downloader.Downloader()
        self.web_drivers = None
        self.os_build_number = None
        self.os_number = None
        self.wd_loc = None
        self.installed_version = "Not Installed!"

        self.get_manifest()
        self.get_system_info()

    def _check_info(self):
        if os.path.exists("/System/Library/Extensions/NVDAStartupWeb.kext"):
            self.wd_loc = "/System/Library/Extensions/NVDAStartupWeb.kext"
        elif os.path.exists("/Library/Extensions/NVDAStartupWeb.kext"):
            self.wd_loc = "/Library/Extensions/NVDAStartupWeb.kext"
        else:
            self.wd_loc = None

    def _get_output(self, comm, shell = False):
        try:
            if shell:
                if type(comm) is list:
                    comm = " ".join(comm)
                p = subprocess.Popen(comm, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                if type(comm) is str():
                    comm = comm.split()
                p = subprocess.Popen(comm, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            c = p.communicate()
            if not p.returncode == 0:
                return c[1].decode("utf-8")
            return c[0].decode("utf-8")
        except:
            return c[1].decode("utf-8")

    def _stream_output(self, comm):
        try:
            p = subprocess.Popen(comm, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                stdoutdata = p.stdout.readline()
                if stdoutdata:
                    sys.stdout.write(stdoutdata.decode("utf-8"))
                else:
                    break
        except:
            return

    def check_path(self, path):
        # Add os checks for path escaping/quote stripping
        path = path.replace("\\", "").replace('"', "")
        # Remove trailing space if drag and dropped
        if path[len(path)-1:] == " ":
            path = path[:-1]
        # Expand tilde
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            print("That file doesn't exist!")
            return None
        return path

    # Helper methods
    def grab(self, prompt):
        if sys.version_info >= (3, 0):
            return input(prompt)
        else:
            return str(raw_input(prompt))

    # Header drawing method
    def head(self, text = "Web Driver Updater", width = 50):
        os.system("clear")
        print("  {}".format("#"*width))
        mid_len = int(round(width/2-len(text)/2)-2)
        middle = " #{}{}{}#".format(" "*mid_len, text, " "*((width - mid_len - len(text))-2))
        print(middle)
        print("#"*width)

    def custom_quit(self):
        self.head("Web Driver Updater")
        print("by CorpNewt\n")
        print("Thanks for testing it out, for bugs/comments/complaints")
        print("send me a message on Reddit, or check out my GitHub:\n")
        print("www.reddit.com/u/corpnewt")
        print("www.github.com/corpnewt\n")
        print("Have a nice day/night!\n\n")
        exit(0)

    def get_manifest(self):
        self.head("Retrieving Manifest...")
        print(" ")
        print("Retrieving manifest from \"https://gfe.nvidia.com/mac-update\"...\n")
        try:
            plist_data = self.dl.get_bytes("https://gfe.nvidia.com/mac-update")
            if not plist_data or not len(str(plist_data)):
                print("Looks like that site isn't responding!\n\nPlease check your intenet connection and try again.")
                time.sleep(3)
                self.web_drivers = {}
                return
            if sys.version_info >= (3, 0):
                self.web_drivers = plistlib.loads(plist_data)
            else:
                self.web_drivers = plistlib.readPlistFromString(plist_data)
        except:
            print("Something went wrong while getting the manifest!\n\nPlease check your intenet connection and try again.")
            time.sleep(3)
            self.web_drivers = {}

    def get_system_info(self):
        self.installed_version = "Not Installed!"
        self.os_build_number = self._get_output(["sw_vers", "-buildVersion"]).strip()
        self.os_number       = self._get_output(["sw_vers", "-productVersion"]).strip()
        if self.wd_loc:
            info_plist = plistlib.readPlist(self.wd_loc + "/Contents/Info.plist")            
            self.installed_version = info_plist["CFBundleGetInfoString"].split(" ")[-1].replace("(", "").replace(")", "")

    def check_dir(self, build):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir("../")
        if not os.path.exists("Web Drivers"):
            os.mkdir("Web Drivers")
        os.chdir("Web Drivers")
        if not os.path.exists(build):
            os.mkdir(build)
        os.chdir(build)
        return os.getcwd()

    def download_for_build(self, build):
        self.head("Downloading for " + build)
        print(" ")
        dl_update = None
        if not "updates" in self.web_drivers:
            print("The manifest was unreachable!\n\nPlease check your internet connection and update the manifest.")
            time.sleep(5)
            return
        for update in self.web_drivers.get("updates", []):
            if update["OS"].lower() == build.lower():
                dl_update = update
                break 
        if not dl_update:
            print("There isn't a version available for that build number!")
            time.sleep(5)
            return
        print("Downloading " + dl_update["version"])
        print(" ")
        self.check_dir(build)
        dl_file = self.dl.stream_to_file(dl_update["downloadURL"], dl_update["downloadURL"].split("/")[-1])
        if dl_file:
            print(dl_file + " downloaded successfully!")
            self._get_output(["open", os.getcwd()])
            time.sleep(5)

    def format_table(self, items, columns):
        max_length = 0
        current_row = 0
        row_list = [[]]
        cur_list = []
        msg = ""
        sorted_list = sorted(items)
        for key in sorted_list:
            entry = key
            if len(entry) > max_length:
                max_length = len(entry)
            row_list[len(row_list)-1].append(entry)
            if len(row_list[len(row_list)-1]) >= columns:
                row_list.append([])
                current_row += 1
        for row in row_list:
            for entry in row:
                entry = entry.ljust(max_length)
                msg += entry + "  "
            msg += "\n"
        return msg

    def build_list(self):
        # Print 8 columns
        self.head("Web Drivers By Build Number")
        print(" ")
        build_list = []
        if not "updates" in self.web_drivers:
            # No manifest
            print("The manifest was unreachable!\n\nPlease check your internet connection and update the manifest.")
            time.sleep(5)
            return
        for update in self.web_drivers.get("updates", []):
            build_list.append(update["OS"])

        print("OS Build Number:  {}".format(self.os_build_number))
        print(" ")
        
        print("Available Build Numbers:\n")
        builds = self.format_table(build_list, 8)
        print(builds)
        print("M. Main Menu")
        print("Q. Quit")
        print(" ")
        menu = self.grab("Please type a build number to download the web driver:  ")

        if not len(menu):
            self.build_list()

        if menu[:1].lower() == "m":
            return
        elif menu[:1].lower() == "q":
            self.custom_quit()

        for build in build_list:
            if build.lower() == menu.lower():
                self.download_for_build(build)
                return
        self.build_list()

    def patch_menu(self):
        self.head("Web Driver Patch")
        print(" ")
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

        if not self.wd_loc:
            print("NVDAStartupWeb.kext was not found in either /L/E or /S/L/E!\n")
            print("Please make sure you have the Web Drivers installed.")
            time.sleep(5)
            return
        info_plist = plistlib.readPlist(self.wd_loc + "/Contents/Info.plist")
        current_build = info_plist.get("IOKitPersonalities", {}).get("NVDAStartup", {}).get("NVDARequiredOS", None)

        print("OS Build Number:  {}".format(self.os_build_number))
        print("WD Target Build:  {}".format(current_build))

        print(" ")
        print("C. Set to Current Build Number")
        print("I. Input New Build Number")
        can_restore = False
        if os.path.exists(self.wd_loc + "/Contents/Info.plist.bak"):
            print("R. Restore Backup")
            print("D. Delete Backup")
            can_restore = True
        print(" ")
        print("M. Main Menu")
        print("Q. Quit")
        print(" ")

        menu = self.grab("Please make a selection:  ")

        if not len(menu):
            self.patch_menu()
            return

        if menu[:1].lower() == "q":
            self.custom_quit()
        elif menu[:1].lower() == "c":
            self.set_build(self.os_build_number)
        elif menu[:1].lower() == "i":
            self.custom_build()
        elif menu[:1].lower() == "r" and can_restore:
            self.restore_backup()
        elif menu[:1].lower() == "d" and can_restore:
            self.delete_backup()
        elif menu[:1].lower() == "m":
            return
        
        self.patch_menu()
        return

    def restore_backup(self):
        self.head("Restoring Backup Info.plist")
        print(" ")
        if not os.path.exists(self.wd_loc + "/Contents/Info.plist.bak"):
            # Create a backup
            print("Backup doesn't exist...")
            time.sleep(5)
            return
        # Removing
        print("Removing " + self.wd_loc + "/Contents/Info.plist...\n")
        self._get_output(["sudo", "rm", self.wd_loc + "/Contents/Info.plist"])
        print("Renaming Info.plist.bak to Info.plist...\n")
        self._get_output(["sudo", "mv", "-f", self.wd_loc + "/Contents/Info.plist.bak", self.wd_loc + "/Contents/Info.plist"])
        print("Updating ownership and permissions...\n")
        self._get_output(["sudo", "chown", "0:0", self.wd_loc + "/Contents/Info.plist"])
        self._get_output(["sudo", "chmod", "755", self.wd_loc + "/Contents/Info.plist"])
        # Rebuild kextcache
        print("Rebuilding kext cache...\n")
        self._stream_output(["sudo", "kextcache", "-i", "/"])
        print(" ")
        print("Done.")
        time.sleep(5)
        return

    def delete_backup(self):
        self.head("Deleting Backup Info.plist")
        print(" ")
        if not os.path.exists(self.wd_loc + "/Contents/Info.plist.bak"):
            # Create a backup
            print("Backup doesn't exist...")
            time.sleep(5)
            return
        # Removing
        print("Removing " + self.wd_loc + "/Contents/Info.plist.bak...\n")
        self._get_output(["sudo", "rm", self.wd_loc + "/Contents/Info.plist.bak"])
        print("Done.")
        time.sleep(5)
        return

    def set_build(self, build_number):
        self.head("Setting NVDARequiredOS to {}".format(build_number))
        print(" ")
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

        info_plist = plistlib.readPlist(self.wd_loc + "/Contents/Info.plist")
        if not os.path.exists(self.wd_loc + "/Contents/Info.plist.bak"):
            # Create a backup
            print("Creating backup...\n")
            self._get_output(["sudo", "cp", self.wd_loc + "/Contents/Info.plist", self.wd_loc + "/Contents/Info.plist.bak"])
            # plistlib.writePlist(info_plist, self.wd_loc + "/Contents/Info.plist.bak")
        # Change the build number and write to the main plist
        print("Patching plist for build \"{}\"...\n".format(build_number))
        info_plist["IOKitPersonalities"]["NVDAStartup"]["NVDARequiredOS"] = build_number
        # Make a temp folder for our plist
        temp_folder = tempfile.mkdtemp()
        # Write the changes
        plistlib.writePlist(info_plist, temp_folder + "/Info.plist")
        # Copy over
        self._get_output(["sudo", "mv", "-f", temp_folder + "/Info.plist", self.wd_loc + "/Contents/Info.plist"])
        # Remove temp
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
        # Ensure perms and ownership are set right
        print("Updating ownership and permissions...\n")
        self._get_output(["sudo", "chown", "0:0", self.wd_loc + "/Contents/Info.plist"])
        self._get_output(["sudo", "chmod", "755", self.wd_loc + "/Contents/Info.plist"])
        # Rebuild kextcache
        print("Rebuilding kext cache...\n")
        self._stream_output(["sudo", "kextcache", "-i", "/"])
        print(" ")
        print("Done.")
        time.sleep(5)
        return

    def custom_build(self):
        self.head("Custom Build")
        print(" ")
        print("")

        if not self.wd_loc:
            print("NVDAStartupWeb.kext was not found in either /L/E or /S/L/E!\n")
            print("Please make sure you have the Web Drivers installed.")
            time.sleep(5)
            return
        info_plist = plistlib.readPlist(self.wd_loc + "/Contents/Info.plist")
        current_build = info_plist.get("IOKitPersonalities", {}).get("NVDAStartup", {}).get("NVDARequiredOS", None)

        print("OS Build Number:  {}".format(self.os_build_number))
        print("WD Target Build:  {}".format(current_build))

        print(" ")
        print("P. Patch Menu")
        print(" ")
        print("M. Main Menu")
        print("Q. Quit")
        print(" ")

        menu = self.grab("Please enter a new build number:  ")

        if not len(menu):
            self.custom_build()
            return

        if menu.lower() == "q":
            self.custom_quit()
        elif menu.lower() == "m":
            self.main()
        elif menu.lower() == "p":
            return
        
        # We have a build number
        self.set_build(menu)
        self.main()
        return

    def patch_installer(self):
        self.head("Patch Install Package")
        print(" ")
        print("M. Main Menu")
        print("Q. Quit")
        print(" ")
        menu = self.grab("Please drag and drop the install package to patch:  ")

        if not len(menu):
            self.patch_installer()
            return

        if menu.lower() == "q":
            self.custom_quit()
        elif menu.lower() == "m":
            return

        # Check path
        menu_path = self.check_path(menu)
        if not menu_path:
            print("That path doesn't exist...")
            time.sleep(3)
            self.patch_installer()
            return
        # Path exists
        temp_dir = tempfile.mkdtemp()
        try:
            self.patch_pkg(menu_path, temp_dir)
        except:
            print("Something went wrong!")
            time.sleep(3)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return

    def patch_pkg(self, package, temp):
        self.head("Patching Install Package")
        print(" ")
        script_path = os.path.dirname(os.path.realpath(__file__))
        print(script_path)
        print("Expanding package...\n")
        self._get_output(["pkgutil", "--expand", package, temp + "/package"])
        new_dist = ""
        print("Patching Distribution...\n")
        with open(temp + "/package/Distribution") as f:
            for line in f:
                if "if (!validatesoftware())" in line.lower():
                    continue
                if "if (!validatehardware())" in line.lower():
                    continue
                if "return false;" in line:
                    line = line.replace("return false;", "return true;")
                new_dist += line
        with open(temp + "/package/Distribution", "w") as f:
            f.write(new_dist)
        self.check_dir("Patched")
        print("Repacking...\n")
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir("../Web Drivers/Patched/")
        self._get_output(["pkgutil", "--flatten", temp + "/package", os.getcwd() + "/" + os.path.basename(package)[:-4] + " (Patched).pkg"])
        print("Done.")
        self._get_output(["open", os.getcwd()])
        time.sleep(5)

    def remove_drivers(self):
        self.head("Removing Web Drivers")
        print(" ")
        print("Clearing web drivers from /S/L/E...\n")
        self._get_output(["sudo", "rm", "-rf", "/System/Library/Extensions/GeForce*Web.*", "/System/Library/Extensions/NVDA*Web.kext"], True)
        print("Clearing web drivers from /L/E...\n")
        self._get_output(["sudo", "rm", "-rf", "/Library/Extensions/GeForce*Web.kext", "/Library/Extensions/NVDA*Web.kext"], True)
        # Rebuild kextcache
        print("Rebuilding kext cache...\n")
        self._stream_output(["sudo", "kextcache", "-i", "/"])
        print(" ")
        print("Done.")
        time.sleep(5)

    def main(self):
        self._check_info()
        self.get_system_info()
        self.head("Web Driver Updater")
        print(" ")
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

        print("OS Version:       {} - {}".format(self.os_number, self.os_build_number))
        print("WD Version:       " + self.installed_version)

        if self.wd_loc:
            info_plist = plistlib.readPlist(self.wd_loc + "/Contents/Info.plist")
            current_build = info_plist.get("IOKitPersonalities", {}).get("NVDAStartup", {}).get("NVDARequiredOS", None)
            print("WD Target Build:  {}".format(current_build))
        
        if not "updates" in self.web_drivers:
            newest_version = "Manifest not available!"
        else:
            newest_version = "None for this build number!"
        for update in self.web_drivers.get("updates", []):
            if update["OS"].lower() == self.os_build_number.lower():
                newest_version = update["version"]
                break 

        if self.installed_version.lower() == newest_version.lower():
            print("Newest:           " + newest_version + " (Current)")
        else:
            print("Newest:           " + newest_version)
        
        print(" ")
        patch = False
        if self.wd_loc:
            print("P. Patch Menu")
            patch = True
        print("I. Patch Install Package")
        print("D. Download For Current")
        print("B. Download By Build Number")
        print("R. Remove Web Drivers")
        print("U. Update Manifest")
        print("")
        print("Q. Quit")
        print(" ")

        menu = self.grab("Please make a selection (just press enter to reload):  ")

        if not len(menu):
            return

        if menu[:1].lower() == "q":
            self.custom_quit()
        elif menu[:1].lower() == "p" and patch:
            self.patch_menu()
        elif menu[:1].lower() == "d":
            self.download_for_build(self.os_build_number)
        elif menu[:1].lower() == "b":
            self.build_list()
        elif menu[:1].lower() == "i":
            self.patch_installer()
        elif menu[:1].lower() == "u":
            self.get_manifest()
        elif menu[:1].lower() == "r":
            self.remove_drivers()
        
        return

wd = WebDriver()

while True:
    try:
        wd.main()
    except Exception as e:
        print(e)
        time.sleep(5)
