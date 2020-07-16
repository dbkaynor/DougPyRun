#!/usr/bin/python
# -*- coding: utf-8 -*-
import tkinter as tk


# ------------------------------


class Vars:
    ProgramVersionNumber = tk.StringVar()
    ProjectFileNameVar = tk.StringVar()
    ProjectFileExtensionVar = tk.StringVar()
    ProjectFileLinesVar = []
    LogFileNameVar = tk.StringVar()
    ListFileNameVar = tk.StringVar()
    AuxDirectoryVar = tk.StringVar()
    HelpFileVar = tk.StringVar()
    CommentsListVar = []
    KeysVar = []
    CommandsVar = []
    HelpTopLevelVar = None
    FileRenameTopLevelVar = None
    GeometryVar = tk.StringVar()
    EntryVar = tk.StringVar()
    DateFormatVar = tk.StringVar()
    EditorResultsSave = ''
    ExplorerVar = tk.StringVar()
    PreferedEditorVar = tk.StringVar()
    PreferedBrowserVar = tk.StringVar()
    EnterNotNeeded = tk.IntVar()
    ListShowStartup = tk.IntVar()
    KeysShowStartup = tk.IntVar()
    NextListItem = tk.StringVar()
