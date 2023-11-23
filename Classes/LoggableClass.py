import colorama
from typing import List
import time

class LoggableClass:
    def __init__(self,prefix:str = "UND",
                 prefix_error:str = "UND ERR",
                 prefix_warning:str = "UND WRN",
                 logging:bool = True,
                 log_warning:bool = True,
                 log_errors:bool = True
                 ):
        #colors
        self.colorama:colorama = colorama
        self.colorama.init()
        self.red:str = colorama.Fore.RED
        self.green:str = colorama.Fore.GREEN
        self.yellow:str = colorama.Fore.YELLOW
        self.blue:str = colorama.Fore.BLUE
        self.magenta:str = colorama.Fore.MAGENTA
        self.cyan:str = colorama.Fore.CYAN
        self.white:str = colorama.Fore.WHITE
        self.black:str = colorama.Fore.BLACK
        self.grey:str = colorama.Fore.LIGHTBLACK_EX
        self.reset:str = colorama.Style.RESET_ALL
        #colors background
        self.bg_red:str = colorama.Back.RED
        self.bg_green:str = colorama.Back.GREEN
        self.bg_yellow:str = colorama.Back.YELLOW
        self.bg_blue:str = colorama.Back.BLUE
        self.bg_magenta:str = colorama.Back.MAGENTA
        self.bg_cyan:str = colorama.Back.CYAN
        self.bg_white:str = colorama.Back.WHITE
        self.bg_black:str = colorama.Back.BLACK
        self.bg_grey:str = colorama.Back.LIGHTBLACK_EX
        #logging
            #colors
        self.prefix_color:str = self.cyan
        self.messsage_color:str = self.white
        self.timestamp_color:str = self.grey
        self.warning_color:str = self.yellow
        self.error_color:str = self.red
            #switches
        self.logging:bool = logging
        self.log_warning:bool = log_warning
        self.log_errors:bool = log_errors
            #lists
        self.log_list:List[str] = []
        self.warning_list:List[str] = []
        self.error_list:List[str] = []
        self.full_logs:List[str] = []
            #prefixes
        self.prefix:str = prefix
        self.prefix_error:str = prefix_error
        self.prefix_warning:str = prefix_warning

    def getTimestamp(self) -> str:
        """Returns the current time in HH:MM:SS format"""
        return time.strftime("%H:%M:%S", time.localtime())
    
    def getCurrentTime(self) -> str:
        """Returns the current, unformatted time"""
        return str(time.time())
    
    def getTimeSince(self,start_time:str) -> str:
        """Returns the time since the start time (start time should be unformatted)"""
        return str(time.time() - start_time)
    
    def getTimeSinceFormatted(self,start_time:str) -> str:
        """Returns the formatted time since the start time (start time should be unformatted)"""
        elapsed_time:float = time.time() - start_time
        #format the elapsed time to hh:mm:ss
        hours:int = int(elapsed_time // 3600)
        minutes:int = int((elapsed_time % 3600) // 60)
        seconds:int = int(elapsed_time % 60)
        return f"{hours}:{minutes}:{seconds}"
    
    def log(self, message:str, prefix:str = None):
        """Logs a message to the console if logging is enabled.  Message is logged to log_list and full_logs regardless of logging status"""
        if not prefix: prefix = self.prefix
        current_time:str = self.getTimestamp()
        line:str = f"[{self.prefix_color}{prefix}{self.reset}]:[{self.timestamp_color}{current_time}{self.reset}] {self.messsage_color}{message}{self.reset}"
        self.log_list.append(line)
        self.full_logs.append(line)
        if self.logging:
            print(line)

    def logError(self, message:str, prefix:str = None):
        """Logs an error message to the console if logging is enabled.  Message is logged to error_list and full_logs regardless of logging status"""
        if not prefix: prefix = self.prefix_error
        current_time:str = self.getTimestamp()
        line:str = f"[{self.error_color}{prefix}{self.reset}]:[{self.timestamp_color}{current_time}{self.reset}] {self.messsage_color}{message}{self.reset}"
        self.error_list.append(line)
        self.full_logs.append(line)
        if self.log_errors:
            print(line)

    def logWarning(self, message:str, prefix:str = None):
        """Logs a warning message to the console if logging is enabled.  Message is logged to warning_list and full_logs regardless of logging status"""
        if not prefix: prefix = self.prefix_warning
        current_time:str = self.getTimestamp()
        line:str = f"[{self.warning_color}{prefix}{self.reset}]:[{self.timestamp_color}{current_time}{self.reset}] {self.messsage_color}{message}{self.reset}"
        self.warning_list.append(line)
        self.full_logs.append(line)
        if self.log_warning:
            print(line)

    def setPrefix(self,prefix:str) -> None:
        """Sets the prefix"""
        self.prefix = prefix

    def setPrefixError(self,prefix:str) -> None:
        """Sets the error prefix"""
        self.prefix_error = prefix

    def setPrefixWarning(self,prefix:str) -> None:
        """Sets the warning prefix"""
        self.prefix_warning = prefix

    def setPrefixColor(self,color:str) -> None:
        """Sets the prefix color"""
        if color.lower() == "red":
            self.prefix_color = self.red
        elif color.lower() == "green":
            self.prefix_color = self.green
        elif color.lower() == "yellow":
            self.prefix_color = self.yellow
        elif color.lower() == "blue":
            self.prefix_color = self.blue
        elif color.lower() == "magenta":
            self.prefix_color = self.magenta
        elif color.lower() == "cyan":
            self.prefix_color = self.cyan
        elif color.lower() == "white":
            self.prefix_color = self.white
        elif color.lower() == "black":
            self.prefix_color = self.black
        elif color.lower() == "grey":
            self.prefix_color = self.grey
        else:
            self.logError(f"Invalid color '{color}'")

    def setMessageColor(self,color:str) -> None:
        """Sets the message color"""
        if color.lower() == "red":
            self.messsage_color = self.red
        elif color.lower() == "green":
            self.messsage_color = self.green
        elif color.lower() == "yellow":
            self.messsage_color = self.yellow
        elif color.lower() == "blue":
            self.messsage_color = self.blue
        elif color.lower() == "magenta":
            self.messsage_color = self.magenta
        elif color.lower() == "cyan":
            self.messsage_color = self.cyan
        elif color.lower() == "white":
            self.messsage_color = self.white
        elif color.lower() == "black":
            self.messsage_color = self.black
        elif color.lower() == "grey":
            self.messsage_color = self.grey
        else:
            self.logError(f"Invalid color '{color}'")

    def setPrefixErrorColor(self,color:str) -> None:
        """Sets the error prefix color"""
        if color.lower() == "red":
            self.prefix_error = self.red
        elif color.lower() == "green":
            self.prefix_error = self.green
        elif color.lower() == "yellow":
            self.prefix_error = self.yellow
        elif color.lower() == "blue":
            self.prefix_error = self.blue
        elif color.lower() == "magenta":
            self.prefix_error = self.magenta
        elif color.lower() == "cyan":
            self.prefix_error = self.cyan
        elif color.lower() == "white":
            self.prefix_error = self.white
        elif color.lower() == "black":
            self.prefix_error = self.black
        elif color.lower() == "grey":
            self.prefix_error = self.grey
        else:
            self.logError(f"Invalid color '{color}'")

    def setPrefixWarningColor(self,color:str) -> None:
        """Sets the warning prefix color"""
        if color.lower() == "red":
            self.prefix_warning = self.red
        elif color.lower() == "green":
            self.prefix_warning = self.green
        elif color.lower() == "yellow":
            self.prefix_warning = self.yellow
        elif color.lower() == "blue":
            self.prefix_warning = self.blue
        elif color.lower() == "magenta":
            self.prefix_warning = self.magenta
        elif color.lower() == "cyan":
            self.prefix_warning = self.cyan
        elif color.lower() == "white":
            self.prefix_warning = self.white
        elif color.lower() == "black":
            self.prefix_warning = self.black
        elif color.lower() == "grey":
            self.prefix_warning = self.grey
        else:
            self.logError(f"Invalid color '{color}'")

    def setTimestampColor(self,color:str) -> None:
        """Sets the timestamp color"""
        if color.lower() == "red":
            self.timestamp_color = self.red
        elif color.lower() == "green":
            self.timestamp_color = self.green
        elif color.lower() == "yellow":
            self.timestamp_color = self.yellow
        elif color.lower() == "blue":
            self.timestamp_color = self.blue
        elif color.lower() == "magenta":
            self.timestamp_color = self.magenta
        elif color.lower() == "cyan":
            self.timestamp_color = self.cyan
        elif color.lower() == "white":
            self.timestamp_color = self.white
        elif color.lower() == "black":
            self.timestamp_color = self.black
        elif color.lower() == "grey":
            self.timestamp_color = self.grey
        else:
            self.logError(f"Invalid color '{color}'")