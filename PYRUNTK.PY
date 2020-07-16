#!/usr/bin/python
# -*- coding: utf-8 -*-
# https://docs.python.org/3/
#
# TODO
# Fix calander to highlight current day
# Add an option to verify project file
#

import sys
import os
import datetime
import time
import platform

sys.path.append('auxfiles')
sys.path.append('..' + os.sep + 'DougModules')

from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
import tkinter.font
import tkinter.ttk
import argparse
import shutil
import pprint
import re
import __main__ as main
from inspect import currentframe as CF
from inspect import getframeinfo as GFI
from inspect import getmodulename as GMN

from ToolTip import ToolTip
import DougModules as DM

import PyCalendarTk as CAL
CalendarWindow = None
import calendar

# Debug
import pdb
# pdb.set_trace()

Main = tkinter.Tk()

from PyRunTkVars import Vars
Vars.ProgramVersionNumber.set('2.1.0')

# ------------------------------
# Parse the command line


def ParseCommandLine():
    #print(DM.MyTrace(GFI(CF()), Display='line,func,file'))
    if len(sys.argv) == 1:
        return

    del sys.argv[0]  # Don't want the script name

    x = ''
    y = []
    y = [x.upper() for x in sys.argv]

    if '-H' in y or '-HELP' in y:
        DM.Logger(DM.MyTrace(GFI(CF())), 'Help was found')
        Help()

    if '-A' in y or '-ABOUT' in y:
        DM.Logger(DM.MyTrace(GFI(CF())), 'About was found')
        About()

    if '-D' in y or '-DEBUG' in y:
        DM.Logger(DM.MyTrace(GFI(CF())), 'Debug was found')
        import pdb
        pdb.set_trace()

    if '-P' in y or '-PROJECT' in y:
        DM.Logger(DM.MyTrace(GFI(CF())), 'Project was found')
        ProjectLoad()

# ------------------------------
# Initialize the program


def StartUpStuff():

    # -- Lots of startup stuff ------------------------------------
    # The following are defaults which will be over written by a project file

    # Get the file path and name for the log file
    Vars.LogFileNameVar.set(os.path.join(os.getcwd(), 'PyRunTk.log'))
    # If the log file exits and is not removable the script is already running
    # so abort this startup
    try:
        if os.path.exists(Vars.LogFileNameVar.get()):
            os.remove(Vars.LogFileNameVar.get())
    except IOError:
        print(Vars.LogFileNameVar.get() + " is open. Script is already running")
        exit()
    DM.SetUpLogger(Vars.LogFileNameVar.get())

    Vars.AuxDirectoryVar.set(os.getcwd() + os.path.sep + 'auxfiles')

    Vars.PreferedEditorVar.set(DM.GetBestEditor())  # Not really needed

    if sys.platform.startswith('linux'):
        Vars.ProjectFileExtensionVar.set('prjl')
        Vars.ExplorerVar.set("NA")
        # Vars.ProgramFilesVar.set("NA")
        # Vars.ProgramFilesx86Var.set("NA")
    elif sys.platform.startswith('win32'):
        Vars.ProjectFileExtensionVar.set('prjw')
        Vars.ExplorerVar.set(os.environ["Windir"] + "\explorer.exe")

    Vars.AuxDirectoryVar.set(os.path.join(os.getcwd(), 'auxfiles', '.'))
    Vars.HelpFileVar.set(os.path.join(Vars.AuxDirectoryVar.get(),
                                      'PyRunTk.hlp'))

    DM.Logger(DM.MyTrace(GFI(CF())), 'OS type:' + str(os.environ.get('OS')))
    DM.Logger(DM.MyTrace(GFI(CF())), 'Uname: ' + str(platform.uname()))
    DM.Logger(DM.MyTrace(GFI(CF())),
              'Number of argument(s): ' + str(len(sys.argv)))
    DM.Logger(DM.MyTrace(GFI(CF())), 'Argument List: ' + str(sys.argv))

    Vars.DateFormatVar.set('%B  %Y/%m/%d    %A %X')

    ProjectLoad('default')

# ------------------------------
# Loads a project file
# Lines without a ~ in the line are ignored and may be used as comments
# Lines with # in position 0 are used as comments


def ProjectLoad(LoadType='none'):
    Entry1.delete(0, END)
    Entry1.insert(0, "Working")
    DM.Logger(DM.MyTrace(GFI(CF())), 'Aux Directory: '
              + Vars.AuxDirectoryVar.get())
    DM.Logger(DM.MyTrace(GFI(CF())), 'Project File Extension: '
              + Vars.ProjectFileExtensionVar.get())
    DM.Logger(DM.MyTrace(GFI(CF())), 'LoadType: ' + LoadType)

    if LoadType == 'default':  # Use the default project file
        Vars.ProjectFileNameVar.set(os.path.join(Vars.AuxDirectoryVar.get(),
                                                 'PyRunTk.'
                                                 + Vars.ProjectFileExtensionVar.get()))
    else:  # Prompt user to select a project file
        Vars.ProjectFileExtensionVar.get()
        Vars.ProjectFileNameVar.set(tkinter.filedialog.askopenfilename(
            defaultextension=Vars.ProjectFileExtensionVar.get(),
            filetypes=[('Project file', 'PyRunTk*.*'
                        + Vars.ProjectFileExtensionVar.get()),
                       ('All files', '*.*')],
            initialdir=Vars.AuxDirectoryVar.get(),
            initialfile='PyRunTk.'
            + Vars.ProjectFileExtensionVar.get(),
            title='Load a PyRunTk project file',
            parent=Main,
        ))
    Vars.ProjectFileNameVar.set(
        os.path.normpath(Vars.ProjectFileNameVar.get()))

    DM.Logger(DM.MyTrace(GFI(CF())), 'Project Load: '
              + Vars.ProjectFileNameVar.get())

    try:
        f = open(Vars.ProjectFileNameVar.get(), 'r')
    except IOError:
        tkinter.messagebox.showerror('Project file error',
                                     'Requested file does not exist.\n>>'
                                     + Vars.ProjectFileNameVar.get() + '<<')
        return

    lines = f.readlines()
    f.close()
    try:
        if not 'PyRunTk.py project file ' + sys.platform in lines[0]:
            tkinter.messagebox.showerror('Project file error',
                                         'Not a valid project file.\nproject file' + '\n'
                                         + lines[0])
            DM.Logger(DM.MyTrace(GFI(CF())), 'PyRunTk.py project file '
                      + lines[0].strip())
            return
    except:
        tkinter.messagebox.showerror('Project file error',
                                     'Unable to read project file'
                                     + Vars.ProjectFileNameVar.get())
        DM.Logger(DM.MyTrace(GFI(CF())),
                  'PyRunTk project file. Unable to read file')
        return

    # remove the first line so it won't be added to the comments list
    del lines[0]

    Vars.CommentsListVar.clear()
    Vars.KeysVar.clear()
    Vars.CommandsVar.clear()

    start = BooleanVar
    tmp = ''
    for line in lines:
        line = line.strip()

        if line.startswith('#'):  # All lines with # in the first column are comments
            Vars.CommentsListVar.append(line)
        else:
            # first we get the user defined variables from the project file
            if line.startswith('DateFormat~='):
                t = line.split('=')
                Vars.DateFormatVar.set(t[1].strip())
            elif line.startswith('PreferedEditor~='):
                t = line.split('~=')
                if sys.platform.startswith('win32'):
                    t[1] = t[1].replace('%ProgramFiles(x86)%', os.environ[
                                        "ProgramFiles(x86)"])
                    t[1] = t[1].replace(
                        '%ProgramFiles%', os.environ["ProgramFiles"])
                Vars.PreferedEditorVar.set(t[1])
            elif line.startswith('PreferedBrowser~='):
                t = line.split('~=')
                if sys.platform.startswith('win32'):
                    t[1] = t[1].replace('%ProgramFiles(x86)%', os.environ[
                                        "ProgramFiles(x86)"])
                    t[1] = t[1].replace(
                        '%ProgramFiles%', os.environ["ProgramFiles"])
                Vars.PreferedBrowserVar.set(t[1])
            elif line.count("~=") > 0:  # Now get the user command strings
                a = line.strip()
                t = a.split('~=')
                if sys.platform.startswith('win32'):
                    t[1] = t[1].replace('%ProgramFiles(x86)%', os.environ[
                                        "ProgramFiles(x86)"])
                    t[1] = t[1].replace(
                        '%ProgramFiles%', os.environ["ProgramFiles"])
                Vars.KeysVar.append(t[0])
                Vars.CommandsVar.append(t[0] + "~=" + t[1])
            elif line.count("=") == 1:  # This is a built in command
                Vars.KeysVar.append(line)

    DM.Logger(DM.MyTrace(GFI(CF())), "Keys: " + str(Vars.KeysVar))

    Vars.KeysVar.sort()
    Vars.KeysVar.sort(key=len, reverse=False)

    Vars.CommandsVar.sort()
    DM.Logger(DM.MyTrace(GFI(CF())), "Size of CommandsVar: " +
              str(len(Vars.CommandsVar)))
    DM.Logger(DM.MyTrace(GFI(CF())),
              "Size of KeysVar: " + str(len(Vars.KeysVar)))
    DM.Logger(DM.MyTrace(GFI(CF())), "Size of CommentsListVar: " +
              str(len(Vars.CommentsListVar)))

    PerformSubstitutions()
    DM.Logger(DM.MyTrace(GFI(CF())), 'Project opened: '
              + Vars.ProjectFileNameVar.get())

# ------------------------------
# This routine will subsitute enviromental variables Vars.CommandsVarles and project defined variables
# System substitutions are already done


def PerformSubstitutions():
    DM.Logger(DM.MyTrace(GFI(CF())), 'PerformSubstitutions')
    Entry1.delete(0, END)
    Entry1.insert(0, "PerformSubstitutions")
    Error = False

    # First verify project defined variables exist
    if not os.path.exists(Vars.PreferedBrowserVar.get()):
        Error = True
        tkinter.messagebox.showerror('Prefered Browser error',
                                     DM.MyTrace(GFI(CF())) +
                                     '\nPrefered Browser does not exist:\n'
                                     + Vars.PreferedBrowserVar.get())

    if not os.path.exists(Vars.PreferedEditorVar.get()):
        Error = True
        tkinter.messagebox.showerror('Prefered Editor error',
                                     DM.MyTrace(GFI(CF())) +
                                     '\nPrefered Editor does not exist:\n'
                                     + Vars.PreferedEditorVar.get())

    # These are the name that will appear in the key list
    go = False

    for w in range(len(Vars.CommandsVar)):
        x = Vars.CommandsVar[w]
        y = x  # Just for debug
        go = False  # debug stuff
        if x.lower().find("%preferedbrowser%") > -1:
            x = re.sub(r"(?i)%preferedbrowser%",
                       Vars.PreferedBrowserVar.get(), x)
            go = True
        if x.lower().find("%preferededitor%") > -1:
            x = re.sub(r"(?i)%preferededitor%",
                       Vars.PreferedEditorVar.get(), x)
            go = True
        if x.lower().find("%explorer%") > -1:
            x = re.sub(r"(?i)%explorer%", Vars.ExplorerVar.get(), x)
            go = True
        if x.lower().find("%comspec%") > -1:
            x = re.sub(r"(?i)%comspec%", os.environ["ComSpec"], x)
            go = True
        if x.lower().find("%windir%") > -1:
            x = re.sub(r"(?i)%windir%", os.environ["windir"], x)
            go = True
        if x.lower().find("%userprofile%") > -1:
            x = re.sub(r"(?i)%userprofile%", os.environ["userprofile"], x)
            go = True
        if x.lower().find("%home%") > -1:  # This is an alias for %userprofile%
            x = re.sub(r"(?i)%home%", os.environ["userprofile"], x)
            go = True

        Vars.CommandsVar[w] = x
        '''
        if go : #Just for debug
            print(DM.MyTrace(GFI(CF())), y)
            print(DM.MyTrace(GFI(CF())), Vars.CommandsVar[w])
            print(DM.MyTrace(GFI(CF())), "......................")
        '''
# ------------------------------
# Displays a list of all keys defined in the project file


def ShowKeys():
    # Prevents multiple copies from starting
    if DM.EditorToplevelName.startswith('Show keys'):
        return
    ff = 'Items: ' + str(len(Vars.KeysVar))
    x = sorted(Vars.KeysVar, key=str.lower)
    for line in x:
        ff = ff + os.linesep + line
    print(DM.MyTrace(GFI(CF())), CalulateBestPoistionForNewWindow())
    DM.Editor(
        FileToEdit=None,
        TextData=ff,
        Title='Show keys',
        Height=505,
        Width=200,
        XPos=900,
        YPos=20,
    )

#-------------------------------
# Some help stuff

def Help():
    print(DM.MyTrace(GFI(CF())), CalulateBestPoistionForNewWindow())
    DM.Editor(
        FileToEdit=Vars.HelpFileVar.get(),
        Title='Help',
        Height=370,
        Width=500,
        XPos=900,
        YPos=20,
    )

# ------------------------------
#todo
def CalulateBestPoistionForNewWindow(Width=None, Height=None):
    print(DM.MyTrace(GFI(CF())),Main.geometry() + "  Width:" + str(Width), " Height:" + str(Height))
    xx = Main.geometry().split("+")
    yy = xx[0].split("x")
    main_loc = []
    main_loc.extend(yy)
    main_loc.append(xx[1])
    main_loc.append(xx[2])
    return(main_loc)
#-------------------------------
# Some debug stuff

def About():
    AboutData = 'Aplication path: ' + os.path.dirname(os.path.abspath(__file__)) \
        + '\nApplication geometry: ' + Main.geometry() \
        + '\nScreen size:      ' + str(Main.winfo_screenwidth()) + 'x' + str(Main.winfo_screenheight()) \
        + '\nPython version:   ' + platform.python_version() \
        + '\nPlatform version: ' + platform.platform() \
        + '\nPyRunTk version:  ' + Vars.ProgramVersionNumber.get() \
        + '\nMachine:          ' + platform.machine() \
        + '\nArchitecture:     ' + str(platform.architecture())
    print(DM.MyTrace(GFI(CF())), CalulateBestPoistionForNewWindow())
    DM.Editor(
        FileToEdit=None,
        TextData=AboutData,
        Title='About',
        Height=180,
        Width=450,
        XPos=900,
        YPos=20,
    )

# ------------------------------
# Update the clock string in entry1 every 500ms


def UpDateClock():
    WorkWeek = int(time.strftime('%U')) + 1
    Entry1.delete(0, END)
    Entry1.insert(0, time.strftime(Vars.DateFormatVar.get() + ' Week: '
                                   + str(WorkWeek)))
    if len(DM.EditorResults) > 0:
        Entry2Enter(3)
        # ReturnCallback(5)
    Main.after(500, UpDateClock)

# ------------------------------

    def ShutDown():
        exit()

    Main.protocol('WM_DELETE_WINDOW', ShutDown)
# ------------------------------
# This is called whenever the user presses the return key
# It processes the commands from the keys list


def ReturnCallback(event):
    command = Entry3.get().lower()

    DM.Logger(DM.MyTrace(GFI(CF())), "command: " + command)
    print(DM.MyTrace(GFI(CF())), "command: " + command)

    # The following are built in commands
    if command == '=about':
        Entry2.delete(0, END)
        Entry3.delete(0, END)
        About()
        return
    elif command == '=exit':
        ShutDown()
        return
    elif command == '=help':
        Entry2.delete(0, END)
        Entry3.delete(0, END)
        Help()
        return
    elif command == '=cal':
        Entry2.delete(0, END)
        Entry3.delete(0, END)
        ShowCalender()
        return
    elif command == '=keyedit':
        DM.StartFile(Vars.PreferedEditorVar.get(), [
                     Vars.ProjectFileNameVar.get()])
        return
    elif command == '=load':
        Entry2.delete(0, END)
        Entry3.delete(0, END)
        ProjectLoad()
        return
    elif command == '=reload':
        Entry2.delete(0, END)
        Entry3.delete(0, END)
        ProjectLoad('default')
        ShowKeys()
        return
    elif command == '=keyshow':
        Entry2.delete(0, END)
        Entry3.delete(0, END)
        ShowKeys()
        return
    elif command == '=logshow':
        Entry2.delete(0, END)
        Entry3.delete(0, END)
        print(DM.MyTrace(GFI(CF())), CalulateBestPoistionForNewWindow())
        DM.Editor(
            FileToEdit=Vars.LogFileNameVar.get(),
            Title='Log',
            Height=750,
            Width=750,
            XPos=500,
            YPos=10,
        )
        return

    # The following are for user added commands

    for line in Vars.CommandsVar:
        if line.lower().find(command.lower() + '~=') == 0:
            MyList = line.split('~=')  # separate the key from the command
            pp = pprint.PrettyPrinter()
            pp.pprint(MyList)

            # del MyList[0]  # don't want the first item

            # separate the command and parameter
            CmdList = MyList[1].split('??')
            Arg1 = str(CmdList[0].strip())
            Arg2 = str(CmdList[1].strip())
            if not os.path.exists(Arg1):
                tkinter.messagebox.showerror('Error: ' + DM.MyTrace(GFI(CF())),
                                             'Command does not exist:\n' + Arg1)
                return

            print(DM.MyTrace(GFI(CF())), Arg1 + "  " + Arg2)
            CList = [Arg2]  # Convert command parameters to list

            print(DM.MyTrace(GFI(CF())), CList)

            Entry1.delete(0, END)
            Entry1.insert(0, "Working")

            # pdb.set_trace() #todo

            DM.StartFile(Arg1, CList)
            DM.EditorResults = ""
            Entry2.delete(0, END)
            Entry3.delete(0, END)

# ------------------------------
# When user pressed return (enter) attempt to start the action

Main.bind('<Return>', ReturnCallback)

# Clear inputs on delete or backspace key


def ClearInputs(Junk=""):
    Entry2.delete(0, END)
    Entry3.delete(0, END)
    DM.EditorResults = ""

Main.bind('<Delete>', ClearInputs)
Main.bind('<BackSpace>', ClearInputs)

# ------------------------------
# Check for a match between user entry and the key list
# This fills in entry3 with the mtch if found


def CheckForMatchInKeyList():
    inputStr = StringVar()
    inputStr = Entry2Var.get().lower().strip()

    if len(inputStr) == 0:
        Entry3.delete(0, END)
    else:
        for y in Vars.KeysVar:
            y = y.lower()
            if y.find(inputStr) == 0:
                Entry3.delete(0, END)
                Entry3.insert(0, y)
                break
            else:
                Entry3.delete(0, END)

# ------------------------------

Entry2Var = StringVar()
Entry2Var.trace('w', lambda name, index, mode,
                Entry2Var=Entry2Var: Entry2callback(Entry2Var))


def Entry2callback(Entry2Var):
    CheckForMatchInKeyList()

# ------------------------------
# Build the gui and start the program

# This entry box displays the time and date
Entry1 = Entry(Main)
Entry1.pack(side=TOP, fill=X, expand=TRUE)
ToolTip(Entry1, 'Time and date display')

# Enter the search values


def ShowCalender():
    global CalendarWindow
    if CalendarWindow:
        try:
            CalendarWindow.destroy()
        except:
            CalendarWindow = None
    CalendarWindow = tkinter.Tk()
    CalendarWindow.title('Tk Calendar')
    ttkcal = CAL.Calendar(CalendarWindow, firstweekday=calendar.SUNDAY)
    ttkcal.pack(expand=1, fill='both')


Entry2 = Entry(Main, textvariable=Entry2Var)
Entry2.pack(side=TOP, fill=X, expand=TRUE)
Entry2.focus_force()
ToolTip(Entry2, 'space for a key list')
Entry2.bind('<space>', lambda e: ShowKeys())
Entry2.bind('<F1>', lambda e: Help())
Entry2.bind('<F2>', lambda e: About())
Entry2.bind('<F3>', lambda e: ShowCalender())
Entry2.bind('<F5>', lambda e: ProjectLoad('default'))

# ------------------------------
# This handles the entry2 binding of <Enter>


def Entry2Enter(Junk):
    Entry2.delete(0, END)
    Entry2.insert(0, DM.EditorResults)
    CheckForMatchInKeyList()
    Entry2.focus_force()

Entry2.bind('<Enter>', Entry2Enter)

# ------------------------------
# This prints out the window geometry on configure event
# Main.bind('<Configure>', lambda e:DM.ShowResize("Main window", Main))

# Display search results

Entry3 = Entry(Main)
Entry3.pack(side=TOP, fill=X, expand=TRUE)
ToolTip(Entry3, 'Press enter to start command')

# ------------------------------

StartUpStuff()
ParseCommandLine()

# ------------------------------

Main.minsize(400, 75)
Main.Geometry = '400x75+10+10'
Main.resizable(True, False)
Main.option_add('*Font', 'courier 10')
Main.title('PyRunTk')
Main.wm_iconname('PyRunTk')

UpDateClock()

Main.mainloop()
