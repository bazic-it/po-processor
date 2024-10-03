import os
import tkinter as tk
from tkinter import messagebox
from script import *

# INSTRUCTION = """
# """

INSTRUCTION = "No instruction."

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.iconbitmap("./assets/icon/icon.ico")
        self.root.title("AVC PO - {}".format(APP_VERSION))
        self.root.geometry("450x200")

        self.frame1 = tk.Frame(self.root)
        self.frame1.pack()

        self.howToButton = tk.Button(self.frame1, text="?", width=2, height=1, command=self.showInstruction)
        self.howToButton.pack(side=tk.TOP, anchor=tk.NE, padx=(0,20), pady=(4,0))

        self.labelFrame1 = tk.LabelFrame(self.frame1, text="PO Filename")
        self.labelFrame1.pack(padx=20, pady=20)

        self.inputField = tk.Entry(self.labelFrame1, font=("Arial", 10), width=50)
        self.inputField.bind("<KeyPress>", self.onEnter)
        self.inputField.pack(padx=10, pady=(5,10))

        self.submitButton = tk.Button(self.frame1, text="Process", font=("Arial", 9), command=self.processCommand, width=20)
        self.submitButton.pack(padx=10, pady=0)

        self.statusMessage = tk.Label(self.frame1, text='', font=("Arial", 9))
        self.statusMessage.pack(padx=10, pady=10)
        
        self.root.mainloop()

    def showInstruction(self):
        messagebox.showinfo(title='Instruction', message=INSTRUCTION)

    def onEnter(self, event):
        if event.keysym == "Return":
            self.processCommand()

    def clearMessages(self):
        self.statusMessage.config(text="")

    def processCommand(self):
        self.statusMessage.config(text="Processing...")
        self.clearMessages()

        inputFilename = self.inputField.get()

        if len(inputFilename) != 0:
            response = processResult(inputFilename)

            if response["success"]:
                self.statusMessage.config(text="Your output filename is: " + response["outputFilename"])
                os.system("start EXCEL.EXE " + response["outputFilename"])

            if response["success"] is not None and not response["success"]:
                self.showStatusMessage("Error", response["errorMessage"])

            self.inputField.delete(0, "end")

    def showStatusMessage(self, title, message):
        messagebox.showinfo(title=title, message=message)

def main():
    App()

if __name__ == "__main__":
    main()