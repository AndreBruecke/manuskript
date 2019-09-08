#!/usr/bin/env python
# --!-- coding: utf8 --!--
import os
import time

from datetime import datetime
from PyQt5.QtWidgets import QPushButton, qApp, QStyle

from manuskript.enums import Outline
from manuskript.functions import mainWindow

class Statistics(object):

    def __init__(self, ui, index, wPath):
        print("Stats Addon > Initializing statistics addon...")
        self.writingStats = []
        self.writingDetails = []
        self.timerRunning = False

        self._index = index
        self.wPath = wPath

        self.btnToggleTimer = QPushButton(ui)
        self.btnToggleTimer.setIcon(qApp.style().standardIcon(QStyle.SP_MediaPause))
        self.btnToggleTimer.clicked.connect(self.toggleTimer)
        self.btnToggleTimer.setFlat(True)

        self.timerRunning = False
        self.toggleTimer()

    def __getPathAsString(self, path):
        res = path[1].title()
        if len(path) < 3:
            return res
        
        for i in path[2:]:
            if i.isFolder():
                res += " > " + i.title()
        return res

    def __pauseTimer(self, endTrigger="pause"):
        if self._index:
            item = self._index.internalPointer()
        length = len(self.writingStats)
        if length > 0:
            self.writingStats[length - 1]["end"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.writingStats[length - 1]["endWC"] = str(item.data(Outline.wordCount))
            self.writingStats[length - 1]["endTrigger"] = endTrigger
            self.writingStats[length - 1]["pathToFile"] = self.__getPathAsString(self.wPath.getItemPath(item))
            self.writingStats[length - 1]["file"] = item.data(Outline.title)

    def toggleTimer(self):
        if self._index:
            item = self._index.internalPointer()
                    
        if self.timerRunning:
            self.timerRunning = False
            self.btnToggleTimer.setIcon(qApp.style().standardIcon(QStyle.SP_MediaPlay))
            self.__pauseTimer("pause")
        else:
            self.timerRunning = True
            self.btnToggleTimer.setIcon(qApp.style().standardIcon(QStyle.SP_MediaPause))
            self.writingStats.append({
                "id" : str(int(time.mktime(datetime.now().timetuple()))),
                "start" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "startWC" : str(item.data(Outline.wordCount)),
                "end" : "",
                "endWC" : "",
                "endTrigger" : "",
                "pathToFile" : "",
                "file" : ""
            })     

    def stopTimer(self, endTrigger="stop"):
        if self.timerRunning:
            self.__pauseTimer(endTrigger)
        self.timerRunning = False
        self.writeToOutput()

    def createFile(self, ouputFile):
        try:
            with open(outputFile, "w") as output:
                output.write("id;start_time;start_count;end_time;end_count;end_trigger;path;fileName\n")
        except Exception as e:
            print("Stats Addon > ERROR > Could not create output file: " + str(e))

    def appendWritingStatsToFile(self, outputFile):
        try:
            with open(outputFile, "a") as output:
                for d in self.writingStats:
                    output.write(
                        d["id"] + ";" +
                        d["start"] + ";" + 
                        d["startWC"] + ";" + 
                        d["end"] + ";" +
                        d["endWC"] + ";" +
                        d["endTrigger"] + ";" +
                        d["pathToFile"] + ";" +
                        d["file"] + "\n"
                    )
        except Exception as e:
            print("Stats Addon > ERROR > Could not write to output file: " + str(e))

    def writeToOutput(self):
        mw = mainWindow()
        project = mw.currentProject
        projectFolder = os.path.dirname(project)
        outputFile = projectFolder + "/" + "stats.csv"

        if len(self.writingStats) == 0:
            return
        if not os.path.exists(projectFolder):
            print("Stats Addon > ERROR > Project directory could not be found.")
            return
        if not os.path.isfile(outputFile):
            self.createFile(outputFile)

        self.appendWritingStatsToFile(outputFile)