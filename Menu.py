import colorama
from typing import List, Dict
import os

class Option:
    def __init__(self,identifier:str, text:str, callback:callable):
        self.identifier:str = identifier
        self.text:str = text
        self.callback:callable = callback
        self.separator:str = ":"
        self.identifier_forecolor:str = colorama.Fore.BLACK
        self.identifier_backcolor:str = colorama.Back.WHITE
        self.text_forecolor:str = colorama.Fore.WHITE

    def setColor(self, id_fore:str = None, id_back:str = None, text_fore:str = None) -> None:
        if id_fore is not None:
            self.identifier_forecolor = id_fore
        if id_back is not None:
            self.identifier_backcolor = id_back
        if text_fore is not None:
            self.text_forecolor = text_fore

    def __str__(self):
        return (f"{self.identifier_forecolor}{self.identifier_backcolor}"
                f"{self.identifier}{self.separator}"
                f"{colorama.Fore.RESET}{colorama.Back.RESET}"
                f"{self.text_forecolor}"
                f" {self.text}{colorama.Fore.RESET}")

    
    def execute(self):
        if self.callback is not None:
            self.callback()
        else:
            input(f"No callback configured for option '{self.identifier}{self.separator} {self.text}'\nPress enter to continue...")

class Menu:
    def __init__(self, title:str):
        #get a local copy of colorama
        self.colorama = colorama
        self.colorama.init()
        #track if running for draw loop
        self.running:bool = True
        #title
        self.title:str = title
        self.title_visible:bool = True
        #info
        self.info:str = None
        self.info_visible:bool = True
        #dimensions
        self.width:int = os.get_terminal_size().columns
        self.height:int = os.get_terminal_size().lines
        #clear command windows/linux
        if os.name == 'nt': self.clear_cmd = 'cls'
        else: self.clear_cmd = 'clear'
        #options
        self.options:List[Option] = []

    def hideTitle(self) -> None:
        self.title_visible = False

    def showTitle(self) -> None:
        self.title_visible = True

    def setInfo(self, info:str) -> None:
        self.info = info

    def appendInfo(self, info:str) -> None:
        self.info += "\n" + info

    def drawInfo(self) -> None:
        if self.info is not None and self.info_visible:
            print(self.info)
            print("")

    def hideInfo(self) -> None:
        self.info_visible = False

    def showInfo(self) -> None:
        self.info_visible = True

    def updateSize(self) -> None:
        self.width = os.get_terminal_size().columns
        self.height = os.get_terminal_size().lines

    def drawTitle(self):
        #update the console size
        self.updateSize()
        #draw the title
        if self.title_visible:
            title_lines:List[str] = []
            line:str = "#" * self.width
            #center the title
            padding:int = (self.width - len(self.title)) // 2
            title_line:str = ("#" * (padding - 3)) + "   " + self.title + "   " + ("#" * (padding - 3))
            title_lines.append(line)
            title_lines.append(title_line)
            title_lines.append(line)
            title_lines.append("")
            for line in title_lines:
                print(line)
    
    def addOption(self, text:str, callback:callable, identifier:str = None) -> None:
        if identifier is None:
            identifier = str(len(self.options) + 1)
        self.options.append(Option(identifier, text, callback))

    def drawOptions(self):
        #draw the options
        for option in self.options:
            print(option)

    def clearScreen(self):
        os.system(self.clear_cmd)

    def draw(self):
        while self.running:
            #clear the screen
            self.clearScreen()
            #draw the title
            self.drawTitle()
            #draw the info
            self.drawInfo()
            #draw the options
            self.drawOptions()
            #get the input
            inp:str = input("\n>")
            #find the option
            valid:bool = False
            for option in self.options:
                if option.identifier == inp:
                    valid = True
                    option.execute()
                    break
            if not valid:
                input(f"Invalid option: {inp}\nPress enter to continue...")


class MainMenu(Menu):
    def __init__(self, title:str):
        super().__init__(title)

class ERTMenu(Menu):
    def __init__(self, title:str):
        super().__init__(title)

class MissingMenu(Menu):
    def __init__(self, title:str):
        super().__init__(title)

class AboutMenu(Menu):
    def __init__(self, title:str):
        super().__init__(title)

