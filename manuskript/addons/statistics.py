#!/usr/bin/env python
# --!-- coding: utf8 --!--
import os
import time

from datetime import datetime
from PyQt5.QtWidgets import QPushButton, qApp, QStyle

from manuskript.enums import Outline
from manuskript.functions import mainWindow

# Statistics addon that tracks wordcounts for writing sessions in fullscreen mode.
# ---------------------------------------------------------------------------------------------------
# Integration into manuskript.ui.editors.fullScreenEditor:
#   __init__			create instance of Statistics class
#   leaveFullscreen		call Statistics.stopTimer()
#   keyPressEvent       if leaving fullscreen: call Statistics.stopTimer()
#   switchPreviousItem	if previousItem: call Statistics.stopTimer(), then Statistics.toggleTimer()
#   switchNextItem		if previousItem: call Statistics.stopTimer(), then Statistics.toggleTimer()
#   switchToItem		if item: call Statistics.stopTimer(), then Statistics.toggleTimer()
#   dataChanged         call Statistics.onInputUpdate()
class Statistics(object):
    
    def __init__(self, ui, index, wPath):
        self.writingStats = []
        self.__previousWC = 0
        self.timerRunning = False

        self._index = index
        self.wPath = wPath

        self.btnToggleTimer = QPushButton(ui)
        self.btnToggleTimer.setIcon(qApp.style().standardIcon(QStyle.SP_MediaPause))
        self.btnToggleTimer.clicked.connect(self.toggleTimer)
        self.btnToggleTimer.setFlat(True)

        self.timerRunning = False
        self.toggleTimer()

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
                "end" : "",
                "startWC" : str(item.data(Outline.wordCount)),
                "endWC" : "",
                "wordsAdded" : 0,
                "wordsRemoved": 0,
                "endTrigger" : "",
                "pathToFile" : "",
                "file" : ""
            })
            self.__previousWC = item.data(Outline.wordCount)
            print("Stats Addon > Started timer.")     

    def stopTimer(self, endTrigger="stop"):
        if self.timerRunning:
            self.__pauseTimer(endTrigger)
        self.timerRunning = False
        self.__writeToOutput()

    def onInputUpdate(self, newWC):
        if newWC == self.__previousWC or len(self.writingStats) == 0:
            return
        diff = newWC - self.__previousWC
        if diff < 0:
            self.writingStats[len(self.writingStats) - 1]["wordsRemoved"] += abs(diff)
        else:
            self.writingStats[len(self.writingStats) - 1]["wordsAdded"] += abs(diff)
        self.__previousWC = newWC

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

    def __createFile(self, outputFile):
        try:
            with open(outputFile, "w") as output:
                output.write("id;start_time;end_time;start_count;end_count;words_added;words_removed;end_trigger;path;fileName\n")
        except Exception as e:
            print("Stats Addon > ERROR > Could not create output file: " + str(e))

    def __appendWritingStatsToFile(self, outputFile):
        try:
            with open(outputFile, "a") as output:
                for d in self.writingStats:
                    output.write(
                        d["id"] + ";" +
                        d["start"] + ";" + 
                        d["end"] + ";" +
                        d["startWC"] + ";" + 
                        d["endWC"] + ";" +
                        str(d["wordsAdded"]) + ";" +
                        str(d["wordsRemoved"]) + ";" +
                        d["endTrigger"] + ";" +
                        d["pathToFile"] + ";" +
                        d["file"] + "\n"
                    )
                print("Stats Addon > Successfully wrote to output file.")
        except Exception as e:
            print("Stats Addon > ERROR > Could not write to output file: " + str(e))

    def __writeToOutput(self):
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
            self.__createFile(outputFile)

        self.__appendWritingStatsToFile(outputFile)
    
    def __getPathAsString(self, path):
        res = path[1].title()
        if len(path) < 3:
            return res
        
        for i in path[2:]:
            if i.isFolder():
                res += " > " + i.title()
        return res