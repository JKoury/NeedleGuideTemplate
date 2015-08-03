import os
import unittest
import csv
import numpy
from Tkinter import *
import math
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

#
# NeedleGuideTemplate
#

class NeedleGuideTemplate(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
        https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
        """
    
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "NeedleGuideTemplate" # TODO make this more human readable by adding spaces
        self.parent.categories = ["IGT"]
        self.parent.dependencies = []
        self.parent.contributors = ["Junichi Tokuda (Brigham and Women's Hospital)"] # replace with "Firstname Lastname (Organization)"
        self.parent.helpText = """
            The NeedleGuideTemlpate module guides image-guided percutaneous interventions with needle-guide template.
            The module calculates identify the needle guide hole and needle insertion depth to reach to the target
            specified on the image.
            """
        self.parent.acknowledgementText = """
            This module is developed by Junichi Tokuda with support from NIH grants P41EB015898 (PI: Jolesz, Tempany) and R01CA111288 (PI: Tempany)
            based on ScriptedLoadableModule template developed by Jean-Christophe Fillion-Robin, Kitware Inc. and Steve Pieper, Isomics, Inc.
            and was partially funded by NIH grant 3P41RR013218-12S1.
            """

#
# NeedleGuideTemplateWidget
#

class NeedleGuideTemplateWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
        https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
        """
    
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        # Instantiate and connect widgets ...
        
        self.logic = NeedleGuideTemplateLogic(None)
        
        #--------------------------------------------------
        # For debugging
        #
        # Reload and Test area
        reloadCollapsibleButton = ctk.ctkCollapsibleButton()
        reloadCollapsibleButton.text = "Reload && Test"
        self.layout.addWidget(reloadCollapsibleButton)
        reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)
        
        reloadCollapsibleButton.collapsed = True
        
        # reload button
        # (use this during development, but remove it when delivering
        #  your module to users)
        self.reloadButton = qt.QPushButton("Reload")
        self.reloadButton.toolTip = "Reload this module."
        self.reloadButton.name = "NeedleGuideTemlpate Reload"
        reloadFormLayout.addWidget(self.reloadButton)
        self.reloadButton.connect('clicked()', self.onReload)
        #
        #--------------------------------------------------
        
        #--------------------------------------------------
        #
        # Configuration
        #
        configCollapsibleButton = ctk.ctkCollapsibleButton()
        configCollapsibleButton.text = "Configuration"
        self.layout.addWidget(configCollapsibleButton)
        
        configFormLayout = qt.QFormLayout(configCollapsibleButton)
        
        configCollapsibleButton.collapsed = True
        
        templateConfigPathLayout = qt.QHBoxLayout()
        
        self.templateConfigPathEdit = qt.QLineEdit()
        self.templateConfigPathEdit.text = ""
        self.templateConfigPathEdit.readOnly = False
        self.templateConfigPathEdit.frame = True
        self.templateConfigPathEdit.styleSheet = "QLineEdit { background:transparent; }"
        self.templateConfigPathEdit.cursor = qt.QCursor(qt.Qt.IBeamCursor)
        templateConfigPathLayout.addWidget(self.templateConfigPathEdit)
        
        self.templateConfigButton = qt.QPushButton("...")
        self.templateConfigButton.toolTip = "Choose a template configuration file"
        self.templateConfigButton.enabled = True
        self.templateConfigButton.connect('clicked(bool)', self.onTemplateConfigButton)
        templateConfigPathLayout.addWidget(self.templateConfigButton)
        
        configFormLayout.addRow("Template Config File: ", templateConfigPathLayout)
        
        fiducialConfigPathLayout = qt.QHBoxLayout()
        
        self.fiducialConfigPathEdit = qt.QLineEdit()
        self.fiducialConfigPathEdit.text = ""
        self.fiducialConfigPathEdit.readOnly = False
        self.fiducialConfigPathEdit.frame = True
        self.fiducialConfigPathEdit.styleSheet = "QLineEdit { background:transparent; }"
        self.fiducialConfigPathEdit.cursor = qt.QCursor(qt.Qt.IBeamCursor)
        fiducialConfigPathLayout.addWidget(self.fiducialConfigPathEdit)
        
        self.fiducialConfigButton = qt.QPushButton("...")
        self.fiducialConfigButton.toolTip = "Choose a fiducial configuration file"
        self.fiducialConfigButton.enabled = True
        self.fiducialConfigButton.connect('clicked(bool)', self.onFiducialConfigButton)
        fiducialConfigPathLayout.addWidget(self.fiducialConfigButton)
        
        configFormLayout.addRow("Fiducial Config File: ", fiducialConfigPathLayout)
        
        #
        # Main Area
        #
        mainCollapsibleButton = ctk.ctkCollapsibleButton()
        mainCollapsibleButton.text = "Main"
        
        self.layout.addWidget(mainCollapsibleButton)
        
        # Layout within the dummy collapsible button
        #mainFormLayout = qt.QFormLayout(mainCollapsibleButton)
        mainLayout = qt.QVBoxLayout(mainCollapsibleButton)
        
        mainFormFrame = qt.QFrame()
        mainFormLayout = qt.QFormLayout(mainFormFrame)
        mainLayout.addWidget(mainFormFrame)
        
        self.showTemplateCheckBox = qt.QCheckBox()
        self.showTemplateCheckBox.checked = 0
        self.showTemplateCheckBox.setToolTip("Show 3D model of the template")
        mainFormLayout.addRow("Show Template:", self.showTemplateCheckBox)
        self.showTemplateCheckBox.connect('toggled(bool)', self.onShowTemplate)
        
        self.showFiducialCheckBox = qt.QCheckBox()
        self.showFiducialCheckBox.checked = 0
        self.showFiducialCheckBox.setToolTip("Show 3D model of the fiducial")
        mainFormLayout.addRow("Show Fiducial:", self.showFiducialCheckBox)
        self.showFiducialCheckBox.connect('toggled(bool)', self.onShowFiducial)
        
        self.showTrajectoriesCheckBox = qt.QCheckBox()
        self.showTrajectoriesCheckBox.checked = 0
        self.showTrajectoriesCheckBox.setToolTip("Show 3D model of the fiducial")
        mainFormLayout.addRow("Show Trajectories:", self.showTrajectoriesCheckBox)
        self.showTrajectoriesCheckBox.connect('toggled(bool)', self.onShowTrajectories)
        
        #
        # input volume selector
        #
        self.targetFiducialsSelector = slicer.qMRMLNodeComboBox()
        self.targetFiducialsSelector.nodeTypes = ( ("vtkMRMLMarkupsFiducialNode"), "" )
        self.targetFiducialsSelector.selectNodeUponCreation = True
        self.targetFiducialsSelector.addEnabled = True
        self.targetFiducialsSelector.removeEnabled = True
        self.targetFiducialsSelector.noneEnabled = False
        self.targetFiducialsSelector.showHidden = False
        self.targetFiducialsSelector.showChildNodeTypes = False
        self.targetFiducialsSelector.setMRMLScene( slicer.mrmlScene )
        self.targetFiducialsSelector.setToolTip( "Select Markups for targets" )
        mainFormLayout.addRow("Targets: ", self.targetFiducialsSelector)
        
        self.targetFiducialsNode = None
        self.targetFiducialsSelector.connect("currentNodeChanged(vtkMRMLNode*)",
                                             self.onFiducialsSelected)
        
        #
        # Target List Table
        #
        self.table = qt.QTableWidget(1, 4)
        self.table.setSelectionBehavior(qt.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(qt.QAbstractItemView.SingleSelection)
        #self.table.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        
        self.headers = ["Name", "Hole", "Depth (mm)", "Position (RAS)"]
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        mainLayout.addWidget(self.table)
        
        self.table.connect('cellClicked(int, int)', self.onTableSelected)
        
        
        self.onFiducialsSelected()
        
        ##
        ## input volume selector
        ##
        #self.inputSelector = slicer.qMRMLNodeComboBox()
        #self.inputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
        #self.inputSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
        #self.inputSelector.selectNodeUponCreation = True
        #self.inputSelector.addEnabled = False
        #self.inputSelector.removeEnabled = False
        #self.inputSelector.noneEnabled = False
        #self.inputSelector.showHidden = False
        #self.inputSelector.showChildNodeTypes = False
        #self.inputSelector.setMRMLScene( slicer.mrmlScene )
        #self.inputSelector.setToolTip( "Pick the input to the algorithm." )
        #mainFormLayout.addRow("Input Volume: ", self.inputSelector)
        
        ##
        ## scale factor for screen shots
        ##
        #self.screenshotScaleFactorSliderWidget = ctk.ctkSliderWidget()
        #self.screenshotScaleFactorSliderWidget.singleStep = 1.0
        #self.screenshotScaleFactorSliderWidget.minimum = 1.0
        #self.screenshotScaleFactorSliderWidget.maximum = 50.0
        #self.screenshotScaleFactorSliderWidget.value = 1.0
        #self.screenshotScaleFactorSliderWidget.setToolTip("Set scale factor for the screen shots.")
        #mainFormLayout.addRow("Screenshot scale factor", self.screenshotScaleFactorSliderWidget)
        
        ##
        ## Apply Button
        ##
        #self.applyButton = qt.QPushButton("Apply")
        #self.applyButton.toolTip = "Run the algorithm."
        #self.applyButton.enabled = False
        #mainFormLayout.addRow(self.applyButton)
        
        # connections
        #self.applyButton.connect('clicked(bool)', self.onApplyButton)
        #self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
        
        
        #--------------------------------------------------
        #
        # Projection
        #
        projectionCollapsibleButton = ctk.ctkCollapsibleButton()
        projectionCollapsibleButton.text = "Projection"
        
        self.layout.addWidget(projectionCollapsibleButton)
        projectionLayout = qt.QVBoxLayout(projectionCollapsibleButton)
        
        projectionCollapsibleButton.collapsed = False
        
        self.openWindowButton = qt.QPushButton("OpenWindow")
        self.openWindowButton.toolTip = "Run the algorithm."
        self.openWindowButton.enabled = True
        projectionLayout.addWidget(self.openWindowButton)
        
        
        self.openWindowButton.connect('clicked(bool)', self.onOpenWindowButton)
        
        
        # Add vertical spacer
        self.layout.addStretch(1)
        
        self.ex = None
    
    def cleanup(self):
        pass
    
    
    def updateTable(self):
        
        print "updateTable() is called"
        if not self.targetFiducialsNode:
            self.table.clear()
            self.table.setHorizontalHeaderLabels(self.headers)
        else:
            
            self.tableData = []
            nOfControlPoints = self.targetFiducialsNode.GetNumberOfFiducials()
            
            if self.table.rowCount != nOfControlPoints:
                self.table.setRowCount(nOfControlPoints)
            
            for i in range(nOfControlPoints):
                
                label = self.targetFiducialsNode.GetNthFiducialLabel(i)
                pos = [0.0, 0.0, 0.0]
                
                self.targetFiducialsNode.GetNthFiducialPosition(i,pos)
                (indexX, indexY, depth, inRange) = self.logic.computeNearestPath(pos)
                
                posstr = '(%.3f, %.3f, %.3f)' % (pos[0], pos[1], pos[2])
                cellLabel = qt.QTableWidgetItem(label)
                cellIndex = qt.QTableWidgetItem('(%s, %s)' % (indexX, indexY))
                cellDepth = None
                if inRange:
                    cellDepth = qt.QTableWidgetItem('%.3f' % depth)
                else:
                    cellDepth = qt.QTableWidgetItem('(%.3f)' % depth)
                cellPosition = qt.QTableWidgetItem(posstr)
                row = [cellLabel, cellIndex, cellDepth, cellPosition]
                
                self.table.setItem(i, 0, row[0])
                self.table.setItem(i, 1, row[1])
                self.table.setItem(i, 2, row[2])
                self.table.setItem(i, 3, row[3])
                
                self.tableData.append(row)
        
        self.table.show()
    
    def onFiducialsSelected(self):
        # Remove observer if previous node exists
        if self.targetFiducialsNode and self.tag:
            self.targetFiducialsNode.RemoveObserver(self.tag)
        
        # Update selected node, add observer, and update control points
        if self.targetFiducialsSelector.currentNode():
            self.targetFiducialsNode = self.targetFiducialsSelector.currentNode()
            self.tag = self.targetFiducialsNode.AddObserver('ModifiedEvent', self.onFiducialsUpdated)
        self.updateTable()
    
    def onFiducialsUpdated(self,caller,event):
        if caller.IsA('vtkMRMLMarkupsFiducialNode') and event == 'ModifiedEvent':
            self.updateTable()
    
    def onSelect(self):
        #self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()
        pass
    
    def onApplyButton(self):
        logic = NeedleGuideTemplateLogic()
        enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
        #screenshotScaleFactor = int(self.screenshotScaleFactorSliderWidget.value)
        print("Run the algorithm")
    
    def onReload(self, moduleName="NeedleGuideTemplate"):
        # Generic reload method for any scripted module.
        # ModuleWizard will subsitute correct default moduleName.
        
        globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)
    
    def onTemplateConfigButton(self):
        path = self.templateConfigPathEdit.text
        path = qt.QFileDialog.getOpenFileName(None, 'Open Template File', path, '*.csv')
        self.templateConfigPathEdit.setText(path)
        self.logic.loadTemplateConfigFile(path)
        self.updateTable()
    
    def onFiducialConfigButton(self):
        path = self.fiducialConfigPathEdit.text
        filename = qt.QFileDialog.getOpenFileName(None, 'Open Fiducial File', path, '.csv')
        self.fiducialConfigPathEdit.setText(path)
    
    def onShowTemplate(self):
        print "onShowTemplate(self)"
        self.logic.setTemplateVisibility(self.showTemplateCheckBox.checked)
    
    def onShowFiducial(self):
        pass
    
    def onShowTrajectories(self):
        print "onTrajectories(self)"
        self.logic.setNeedlePathVisibility(self.showTrajectoriesCheckBox.checked)
    
    def onOpenWindowButton(self):
        print "onOpenWindowButton(self) is called!!!"
        self.ex = ProjectionWindow()
        self.ex.repaint()
        self.sc = SizeCalc()
        self.sc.setProjectionWindow(self.ex)
        self.sc.repaint()
    
    def onTableSelected(self, row, column):
        print "onTableSelected(%d, %d)" % (row, column)
        pos = [0.0, 0.0, 0.0]
        label = self.targetFiducialsNode.GetNthFiducialLabel(row)
        self.targetFiducialsNode.GetNthFiducialPosition(row,pos)
        (indexX, indexY, depth, inRange) = self.logic.computeNearestPath(pos)
        
        
        print "index = "
        print indexX
        print indexY
        
        d = 20
        Letters={'A': .5,'B': 1.5,'C': 2.5,'D': 3.5,'E': 4.5,'F': 5.5,'G': 6.5,'H': 7.5,'I': 8.5,'J':9.5,'K':10.5,'L':11.5,'M':12.5,'N':13.5}
        Numbers={'-7' : .5,'-6' : 1.5,'-5' : 2.5,'-4' : 3.5,'-3' : 4.5,'-2' : 5.5,'-1' : 6.5, '0' : 7.5, '1' : 8.5, '2' : 9.5, '3' : 10.5, '4' : 11.5, '5' : 12.5, '6' : 13.5, '7' : 14.5}
        
        ConvertedL = Letters[indexX]
        ConvertedN = Numbers[indexY]
        x = ConvertedL * d + 50
        y = ConvertedN * d
        
        if self.ex:
            self.ex.setXY(x, y)   
            #  self.ex.setDepth(depth)
            self.ex.setTemplateLabels(indexX, indexY, depth)
            self.ex.repaint()



#
# NeedleGuideTemplateLogic
#

class NeedleGuideTemplateLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
        computation done by your module.  The interface
        should be such that other python code can import
        this class and make use of the functionality without
        requiring an instance of the Widget.
        Uses ScriptedLoadableModuleLogic base class, available at:
        https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
        """
    
    def __init__(self, parent):
        ScriptedLoadableModuleLogic.__init__(self, parent)
        
        self.fiducialName = ''
        self.fiducialConfig = []
        self.templateName = ''
        self.templateConfig = []
        self.templateIndex = []
        self.templateMaxDepth = []
        self.templateModelNodeID = ''
        self.needlePathModelNodeID = ''
        self.templatePathOrigins = []  ## Origins of needle paths
        self.templatePathVectors = []  ## Normal vectors of needle paths
        self.pathOrigins = []  ## Origins of needle paths (after transformation by parent transform node)
        self.pathVectors = []  ## Normal vectors of needle paths (after transformation by parent transform node)
        self.depth = 0
    
    def loadFiducialConfigFile(self, path):
        reader = csv.reader(open(path, 'rb'))
    
    def loadTemplateConfigFile(self, path):
        self.templateIndex = []
        self.templateConfig = []
        
        header = False
        reader = csv.reader(open(path, 'rb'))
        try:
            for row in reader:
                if header:
                    self.templateIndex.append(row[0:2])
                    self.templateConfig.append([float(row[2]), float(row[3]), float(row[4]),
                                                float(row[5]), float(row[6]), float(row[7]),
                                                float(row[8])])
                else:
                    self.templateName = row[0]
                    header = True
        except csv.Error as e:
            print('file %s, line %d: %s' % (filename, reader.line_num, e))
        
        self.createTemplateModel()
        self.setTemplateVisibility(0)
        self.setNeedlePathVisibility(0)
        self.updateTemplateVectors()
    
    def setDepth(self, depth):
        self.depth = depth
    
    def createTemplateModel(self):
        
        self.templatePathVectors = []
        self.templatePathOrigins = []
        
        tempModelNode = slicer.mrmlScene.GetNodeByID(self.templateModelNodeID)
        if tempModelNode == None:
            tempModelNode = slicer.vtkMRMLModelNode()
            tempModelNode.SetName('NeedleGuideTemplate')
            slicer.mrmlScene.AddNode(tempModelNode)
            self.templateModelNodeID = tempModelNode.GetID()
            
            dnode = slicer.vtkMRMLModelDisplayNode()
            #dnode.SetColor(self.ModelColor)
            slicer.mrmlScene.AddNode(dnode)
            tempModelNode.SetAndObserveDisplayNodeID(dnode.GetID())
            self.modelNodetag = tempModelNode.AddObserver(slicer.vtkMRMLTransformableNode.TransformModifiedEvent,
                                                          self.onTemplateTransformUpdated)
        
        pathModelNode = slicer.mrmlScene.GetNodeByID(self.needlePathModelNodeID)
        if pathModelNode == None:
            pathModelNode = slicer.vtkMRMLModelNode()
            pathModelNode.SetName('NeedleGuideNeedlePath')
            slicer.mrmlScene.AddNode(pathModelNode)
            self.needlePathModelNodeID = pathModelNode.GetID()
            
            dnode = slicer.vtkMRMLModelDisplayNode()
            slicer.mrmlScene.AddNode(dnode)
            pathModelNode.SetAndObserveDisplayNodeID(dnode.GetID())
        
        pathModelAppend = vtk.vtkAppendPolyData()
        tempModelAppend = vtk.vtkAppendPolyData()
        
        for row in self.templateConfig:
            
            p1 = numpy.array(row[0:3])
            p2 = numpy.array(row[3:6])
            tempLineSource = vtk.vtkLineSource()
            tempLineSource.SetPoint1(p1)
            tempLineSource.SetPoint2(p2)
            
            tempTubeFilter = vtk.vtkTubeFilter()
            tempTubeFilter.SetInputConnection(tempLineSource.GetOutputPort())
            tempTubeFilter.SetRadius(1.0)
            tempTubeFilter.SetNumberOfSides(18)
            tempTubeFilter.CappingOn()
            tempTubeFilter.Update()
            
            pathLineSource = vtk.vtkLineSource()
            v = p2-p1
            nl = numpy.linalg.norm(v)
            n = v/nl  # normal vector
            l = row[6]
            p3 = p1 + l * n
            pathLineSource.SetPoint1(p1)
            pathLineSource.SetPoint2(p3)
            
            self.templatePathOrigins.append([row[0], row[1], row[2], 1.0])
            self.templatePathVectors.append([n[0], n[1], n[2], 1.0])
            self.templateMaxDepth.append(row[6])
            
            pathTubeFilter = vtk.vtkTubeFilter()
            pathTubeFilter.SetInputConnection(pathLineSource.GetOutputPort())
            pathTubeFilter.SetRadius(0.8)
            pathTubeFilter.SetNumberOfSides(18)
            pathTubeFilter.CappingOn()
            pathTubeFilter.Update()
            
            if vtk.VTK_MAJOR_VERSION <= 5:
                tempModelAppend.AddInput(tempTubeFilter.GetOutput());
                pathModelAppend.AddInput(pathTubeFilter.GetOutput());
            else:
                tempModelAppend.AddInputData(tempTubeFilter.GetOutput());
                pathModelAppend.AddInputData(pathTubeFilter.GetOutput());
            
            tempModelAppend.Update()
            tempModelNode.SetAndObservePolyData(tempModelAppend.GetOutput())
            pathModelAppend.Update()
            pathModelNode.SetAndObservePolyData(pathModelAppend.GetOutput())
    
    
    def setModelVisibilityByID(self, id, visible):
        
        mnode = slicer.mrmlScene.GetNodeByID(id)
        if mnode != None:
            dnode = mnode.GetDisplayNode()
            if dnode != None:
                dnode.SetVisibility(visible)
    
    def setModelSliceIntersectionVisibilityByID(self, id, visible):
        
        mnode = slicer.mrmlScene.GetNodeByID(id)
        if mnode != None:
            dnode = mnode.GetDisplayNode()
            if dnode != None:
                dnode.SetSliceIntersectionVisibility(visible)
    
    def setTemplateVisibility(self, visibility):
        self.setModelVisibilityByID(self.templateModelNodeID, visibility)
    
    def setNeedlePathVisibility(self, visibility):
        self.setModelVisibilityByID(self.needlePathModelNodeID, visibility)
        self.setModelSliceIntersectionVisibilityByID(self.needlePathModelNodeID, visibility)
    
    #def onFiducialsUpdated(self,caller,event):
    def onTemplateTransformUpdated(self,caller,event):
        print 'onTemplateTransformUpdated()'
        self.updateTemplateVectors()
    
    def updateTemplateVectors(self):
        print 'updateTemplateVectors()'
        
        mnode = slicer.mrmlScene.GetNodeByID(self.templateModelNodeID)
        if mnode == None:
            return 0
        tnode = mnode.GetParentTransformNode()
        
        trans = vtk.vtkMatrix4x4()
        if tnode != None:
            tnode.GetMatrixTransformToWorld(trans);
        else:
            trans.Identity()
        
        # Calculate offset
        zero = [0.0, 0.0, 0.0, 1.0]
        offset = []
        offset = trans.MultiplyDoublePoint(zero)
        
        self.pathOrigins = []
        self.pathVectors = []
        
        i = 0
        for orig in self.templatePathOrigins:
            torig = trans.MultiplyDoublePoint(orig)
            self.pathOrigins.append(numpy.array(torig[0:3]))
            vec = self.templatePathVectors[i]
            tvec = trans.MultiplyDoublePoint(vec)
            self.pathVectors.append(numpy.array([tvec[0]-offset[0], tvec[1]-offset[1], tvec[2]-offset[2]]))
            i = i + 1
    
    def computeNearestPath(self, pos):
        # Identify the nearest path and return the index for self.templateConfig[] and depth
        #  (index_x, index_y, depth, inRange) = computeNearestPath()
        
        p = numpy.array(pos)
        
        minMag2 = numpy.Inf
        minDepth = 0.0
        minIndex = -1
        
        ## TODO: Can following loop can be described by matrix calculation?
        i = 0
        for orig in self.pathOrigins:
            vec = self.pathVectors[i]
            op = p - orig
            aproj = numpy.inner(op, vec)
            perp = op-aproj*vec
            mag2 = numpy.vdot(perp,perp) # magnitude^2
            if mag2 < minMag2:
                minMag2 = mag2
                minIndex = i
                minDepth = aproj
            i = i + 1
        
        indexX = '--'
        indexY = '--'
        inRange = False
        
        if minIndex >= 0:
            indexX = self.templateIndex[minIndex][0]
            indexY = self.templateIndex[minIndex][1]
            if minDepth > 0 and minDepth < self.templateMaxDepth[minIndex]:
                inRange = True
        
        return (indexX, indexY, minDepth, inRange)


class NeedleGuideTemplateTest(ScriptedLoadableModuleTest):
    """
        This is the test case for your scripted Uses.
        module ScriptedLoadableModuleTest base class, available at:
        https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
        """
    
    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
            """
        slicer.mrmlScene.Clear(0)
    
    def runTest(self):
        """Run as few or as many tests as needed here.
            """
        self.setUp()
        self.test_NeedleGuideTemplate1()
    
    def test_NeedleGuideTemplate1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
            tests sould exercise the functionality of the logic with different inputs
            (both valid and invalid).  At higher levels your tests should emulate the
            way the user would interact with your code and confirm that it still works
            the way you intended.
            One of the most important features of the tests is that it should alert other
            developers when their changes will have an impact on the behavior of your
            module.  For example, if a developer removes a feature that you depend on,
            your test should break so they know that the feature is needed.
            """
        
        self.delayDisplay("Starting the test")
        #
        # first, get some data
        #
        import urllib
        downloads = (
                     ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
                     )
        
        for url,name,loader in downloads:
            filePath = slicer.app.temporaryPath + '/' + name
            if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
                print('Requesting download %s from %s...\n' % (name, url))
                urllib.urlretrieve(url, filePath)
            if loader:
                print('Loading %s...\n' % (name,))
                loader(filePath)
        self.delayDisplay('Finished with download and loading\n')
        
        volumeNode = slicer.util.getNode(pattern="FA")
        logic = NeedleGuideTemplateLogic()
        self.assertTrue( logic.hasImageData(volumeNode) )
        self.delayDisplay('Test passed!')


class SizeCalc(qt.QWidget):
    
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.mousePointX1=None
        self.mousePointY1=None
        self.mousePointX2=None
        self.mousePointY2=None
        self.mousePointX3=None
        self.mousePointY3=None
        self.mousePointX4=None
        self.mousePointY4=None
        self.state=0
        self.distance=None
        self.LT_Text="Please Select the Top Left Corner"
        self.RT_Text="Please Select the Top Right Corner"
        self.LB_Text="Please Select the Bottom Left Corner"
        self.RB_Text="Please Select the Bottom Right Corner"
        self.Quit_Text="Please Exit the Window"
        self.scale = None
        self.projectionWindow=None
        self.prevState=self.state
        self.timer = None
        
        self.initUI()
    
    def setProjectionWindow(self, pw):
        self.projectionWindow = pw
    
    def drawLines(self, qp):
        pen = qt.QPen(qt.Qt.green, 2, qt.Qt.SolidLine)
        
        if self.state == 0:
            pen.setColor(qt.Qt.black)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 30))
            qp.drawText(qt.QPointF(325,60), self.LT_Text)
        
        elif self.state == 1:
            pen.setColor(qt.Qt.black)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 30));
            qp.drawText(qt.QPointF(325,60), self.RT_Text)
        
        elif self.state == 2:
            pen.setColor(qt.Qt.black)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 30));
            qp.drawText(qt.QPointF(325,60), self.LB_Text)
        
        elif self.state == 3:
            pen.setColor(qt.Qt.black)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 30));
            qp.drawText(qt.QPointF(325,60), self.RB_Text)
        
        elif self.state == 4:
            pen.setColor(qt.Qt.black)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 30));
            qp.drawText(qt.QPointF(325,60), self.Quit_Text)
    
    
    def voiceInstruction(self, state):
        if state == 0:
            os.system("say -v Victoria 'Please select the top left template corner'")
        elif state == 1:
            os.system("say -v Victoria 'Please select the top right template corner'")
        elif state == 2:
            os.system("say -v Victoria 'Please select the bottom left template corner'")
        elif state == 3:
            os.system("say -v Victoria 'Please select the bottom right template corner'")
        elif state == 4:
            os.system("say -v Victoria 'Please exit the window'")
    
    
    def paintEvent(self, e):
        qp = qt.QPainter()
        qp.begin(self)
        self.drawLines(qp)
        qp.end()
    
    
    def initUI(self):              
        self.qbtn = qt.QPushButton('Quit', self)
        # qbtn.clicked.connect(qt.QCoreApplication.instance().quit)
        self.qbtn.clicked.connect(self.onQuitButton)
        self.qbtn.move(50, 50)      
        
        self.setGeometry(0, 0, 1024, 768)
        self.setWindowTitle('Quit button')   
        self.setWindowFlags(self.windowFlags() | qt.Qt.FramelessWindowHint)
        #self.qbtn.connect("clicked", self.onQuitButton)
        self.show()
        self.voiceInstruction(0)
    
    def onQuitButton(self):
        self.projectionWindow.setScale(self.scale)
        self.projectionWindow.repaint()
        self.destroy()
    
    def mousePressEvent(self, QMouseEvent):
        print 'mousePressEvent(self, QMouseEvent)'
        
        if self.state==0:
            self.mousePos = QMouseEvent.pos()
            self.mousePointX1 = self.mousePos.x()
            self.mousePointY1 = self.mousePos.y()
            print "Top Left Corner(x, y) = (%d, %d)" % (self.mousePointX1, self.mousePointY1)
            self.state = 1
        elif self.state==1:
            self.mousePos = QMouseEvent.pos()
            self.mousePointX2 = self.mousePos.x()
            self.mousePointY2 = self.mousePos.y()
            print "Top Right Corner(x, y) = (%d, %d)" % (self.mousePointX2, self.mousePointY2)
            self.state = 2
        elif self.state==2:
            self.mousePos = QMouseEvent.pos()
            self.mousePointX3 = self.mousePos.x()
            self.mousePointY3 = self.mousePos.y()
            print "Bottom Left Corner(x, y) = (%d, %d)" % (self.mousePointX3, self.mousePointY3)
            self.state = 3
        elif self.state==3:
            self.mousePos = QMouseEvent.pos()
            self.mousePointX4 = self.mousePos.x()
            self.mousePointY4 = self.mousePos.y()
            print "Bottom Right Corner(x, y) = (%d, %d)" % (self.mousePointX4, self.mousePointY4)
            self.state = 4
            
            TL = (self.mousePointX1, self.mousePointY1)  # point 1 coordinate
            TR = (self.mousePointX2, self.mousePointY2)  # point 2 coordinate
            BL = (self.mousePointX3, self.mousePointY3)
            BR = (self.mousePointX4, self.mousePointY4)
            self.scale = (math.hypot(BR[0] - TL[0], BR[1] - TL[1]))/382.099463491 # Linear distance
            print self.scale
        
        self.repaint()
        
        if self.state != self.prevState:
            self.voiceInstruction(self.state)
        self.prevState = self.state


class ProjectionWindow(qt.QWidget):
    
    horizontal = 0
    vertical = 0
    
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.initUI()
    
    def initUI(self):
        self.text_n7 = "-7"
        self.text_n6 = "-6"
        self.text_n5 = "-5"
        self.text_n4 = "-4"
        self.text_n3 = "-3"
        self.text_n2 = "-2"
        self.text_n1 = "-1"
        self.text_0 = "0"
        self.text_1 = "1"
        self.text_2 = "2"
        self.text_3 = "3"
        self.text_4 = "4"
        self.text_5 = "5"
        self.text_6 = "6"
        self.text_7 = "7"
        self.setStyleSheet("background-color:black;")
        self.setGeometry(330, 330 ,355 ,355) #Area of total window = 117150 ... Area of graph = 84000
        self.setWindowTitle('Crosshair')
        
        self.text_A = "A"
        self.text_B = "B"
        self.text_C = "C"
        self.text_D = "D"
        self.text_E = "E"
        self.text_F = "F"
        self.text_G = "G"
        self.text_H = "H"
        self.text_I = "I"
        self.text_J = "J"
        self.text_K = "K"
        self.text_L = "L"
        self.text_M = "M"
        self.text_N = "N"
        self.indexX = ""
        self.indexY = ""
        self.ndepth = ""
        self.state2 = 0
        self.blink= 0
        
        self.text_Hole = "o"
        
        self.scale = 1.0
        
        self.setGeometry(0, 0, 600, 600)
        self.setWindowTitle('Template')   
        self.setWindowFlags(self.windowFlags() | qt.Qt.FramelessWindowHint)
        self.show()
    
        self.timer = qt.QTimer()
        self.timer.timeout.connect(self.doBlinkMethod)
        self.timer.start(500) # every 10 seconds

    def onQuitButton2(self):
        self.destroy()
        
    def initUI2(self):              
        self.qbtn = qt.QPushButton('Quit', self)
        # qbtn.clicked.connect(qt.QCoreApplication.instance().quit)
        self.qbtn.clicked.connect(self.onQuitButton2)
        self.qbtn.move(100, 100)   
    
        self.setWindowTitle('Quit button')   
        self.setWindowFlags(self.windowFlags() | qt.Qt.FramelessWindowHint)
        #self.qbtn.connect("clicked", self.onQuitButton)
        self.show()  
    
    def paintEvent(self, e):
        
        qp = qt.QPainter()
        qp.begin(self)
        self.drawLines(qp)
        qp.end()
    
    def setXY(self, x, y):
        self.horizontal = x
        self.vertical = y+40
    
    def setTemplateLabels(self, indexX, indexY, ndepth):
        print "setTemplateLabels(%s, %s, %s) is called" % (indexX, indexY, ndepth)
        self.indexX = indexX
        self.indexY = indexY
        self.ndepth = ndepth
        self.state2 = 1
        
        iy = self.indexY
        if int(iy) < 0:
          iy = 'minus %d' % -int(iy)
        nd = '%d' % self.ndepth
        if int(nd) < 0:
            nd = 'minus %d' % -int(nd)       
        os.system("say -v Victoria Please navigate to template hole %s, %s. The Needle Instertion depth is  %s millimeters" % (self.indexX, iy, nd))
 	
 
    def doBlinkMethod(self):
       self.repaint()
       
            
    def setScale( self, scale ):
        self.scale = scale
    
    def drawLines(self, qp):
        
        pen = qt.QPen(qt.Qt.green, 2, qt.Qt.SolidLine)
        
        #Beginning of Line Drawing
        
        qp.setPen(pen)
        qp.drawLine(self.scale * 40, self.scale * self.horizontal, self.scale * 340, self.scale * self.horizontal)
        
        qp.setPen(pen)
        qp.drawLine(self.scale * self.vertical, self.scale * 50, self.scale * self.vertical, self.scale * 330)
        
        pen.setStyle(qt.Qt.DashLine)
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.drawText(qt.QPointF(100,40), "Template Coordinate: %s,%s    Needle Insertion Depth:%s millimeters" % (self.indexX,self.indexY,self.ndepth))

               
        pen.setStyle(qt.Qt.DashLine)
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.drawLine(self.scale * 40, self.scale * 50, self.scale * 340, self.scale * 50)
        
        pen.setStyle(qt.Qt.DashLine)
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.drawLine(self.scale * 40, self.scale * 50, self.scale * 40, self.scale * 330)
        
        pen.setStyle(qt.Qt.DashLine)
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.drawLine(self.scale * 40, self.scale * 330, self.scale * 340, self.scale * 330)
        
        #pen.setStyle(qt.Qt.DashLine)
        #pen.setColor(qt.Qt.white)
        #qp.setPen(pen)
        #qp.drawLine(40, 290, 40, 330)
        
        #pen.setStyle(qt.Qt.DashLine)
        #pen.setColor(qt.Qt.black)
        #qp.setPen(pen)
        #qp.drawLine(300, 0, 260, 0)
        
        pen.setStyle(qt.Qt.DashLine)
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.drawLine(self.scale * 340, self.scale * 50, self.scale * 340, self.scale * 330)
        
        #pen.setStyle(qt.Qt.DashLine)
        #pen.setColor(qt.Qt.white)
        #qp.setPen(pen)
        #qp.drawLine(340, 290, 340, 330)
        
        #pen.setStyle(qt.Qt.DashLine)
        #pen.setColor(qt.Qt.white)
        
        #qp.setPen(pen)
        #qp.drawLine(340, 330, 300, 330)
        
        #End of Line Drawing
        
        #pen.setColor(qt.Qt.white)
        #qp.setPen(pen)
        #qp.setFont(qt.QFont("Arial", 12));
        #qp.drawText(qt.QPointF(163, 47), self.text_info)
        
        #Beginning of Number Indicators
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 45, self.scale * 47), self.text_n7)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 65, self.scale * 47), self.text_n6)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 85, self.scale * 47), self.text_n5)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 105, self.scale * 47), self.text_n4)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 125, self.scale * 47), self.text_n3)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 145, self.scale * 47), self.text_n2)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 165, self.scale * 47), self.text_n1)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 185, self.scale * 47), self.text_0)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 205, self.scale * 47), self.text_1)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 225, self.scale * 47), self.text_2)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 245, self.scale * 47), self.text_3)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 265, self.scale * 47), self.text_4)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 285, self.scale * 47), self.text_5)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 305, self.scale * 47), self.text_6)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 325, self.scale * 47), self.text_7)
        
        #End of Number Indicators
        #Beginning of Letter Indicators
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 26, self.scale * 62), self.text_A)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 26, self.scale * 82), self.text_B)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 26, self.scale * 102), self.text_C)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 26, self.scale * 122), self.text_D)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 26, self.scale * 142), self.text_E)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 26, self.scale * 162), self.text_F)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 26, self.scale * 182), self.text_G)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 26, self.scale * 202), self.text_H)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 26, self.scale * 222), self.text_I)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 26, self.scale * 242), self.text_J)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 26, self.scale * 262), self.text_K)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 26, self.scale * 282), self.text_L)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 26, self.scale * 302), self.text_M)
        
        pen.setColor(qt.Qt.white)
        qp.setPen(pen)
        qp.setFont(qt.QFont("Arial", 12));
        qp.drawText(qt.QPointF(self.scale * 26, self.scale * 322), self.text_N)
        
        #End of Letter Indicators
        
        self.blink= self.blink+1
        
        if self.blink % 2 == 0: 
          pen.setColor(qt.Qt.green)
          qp.setPen(pen)
          qp.setFont(qt.QFont("Arial", 15*self.scale));
          qp.drawText(qt.QPointF((self.scale * self.vertical) - 5 * self.scale,(self.scale * self.horizontal) + 4 * self.scale), "X")
          
        else:
          pen.setColor(qt.Qt.black)
          qp.setPen(pen)
          qp.setFont(qt.QFont("Arial", 15*self.scale));
          qp.drawText(qt.QPointF((self.scale * self.vertical) - 5 * self.scale,(self.scale * self.horizontal) + 4 * self.scale), "X")
        
        
        Spaces = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]     
        
        #Beginning of Hole Indicators A
        
        
        for i in Spaces:
            pen.setColor(qt.Qt.white)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 12));
            qp.drawText(qt.QPointF(self.scale * (47 + 20*i), self.scale * 61), self.text_Hole)
        
        
        #End of Hole Indicators A
        #Beginning of Hole Indicators B
        
        
        for i in Spaces:
            pen.setColor(qt.Qt.white)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 12));
            qp.drawText(qt.QPointF(self.scale * (47 + 20*i), self.scale * 81), self.text_Hole)       
        
        
        #End of Hole Indicators B
        #Beginning of Hole Indicators C
        
        
        for i in Spaces:
            pen.setColor(qt.Qt.white)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 12));
            qp.drawText(qt.QPointF(self.scale * (47 + 20*i), self.scale * 101), self.text_Hole)         
        
        
        #End of Hole Indicators C
        #Beginning of Hole Indicators D
        
        
        for i in Spaces:
            pen.setColor(qt.Qt.white)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 12));
            qp.drawText(qt.QPointF(self.scale * (47 + 20*i), self.scale * 121), self.text_Hole)     
        
        
        #End of Hole Indicators D
        #Beginning of Hole Indicators E
        
        
        
        for i in Spaces:
            pen.setColor(qt.Qt.white)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 12));
            qp.drawText(qt.QPointF(self.scale * (47 + 20*i), self.scale * 141), self.text_Hole)     
        
        
        #End of Hole Indicators E
        #Beginning of Hole Indicators F
        
        
        for i in Spaces:
            pen.setColor(qt.Qt.white)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 12));
            qp.drawText(qt.QPointF(self.scale * (47 + 20*i), self.scale * 161), self.text_Hole)     
        
        
        #End of Hole Indicators F
        #Beginning of Hole Indicators G
        
        
        for i in Spaces:
            pen.setColor(qt.Qt.white)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 12));
            qp.drawText(qt.QPointF(self.scale * (47 + 20*i), self.scale * 181), self.text_Hole)        
        
        
        #End of Hole Indicators G
        #Beginning of Hole Indicators H
        
        
        for i in Spaces:
            pen.setColor(qt.Qt.white)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 12));
            qp.drawText(qt.QPointF(self.scale * (47 + 20*i), self.scale * 201), self.text_Hole)   
        
        
        #End of Hole Indicators H
        #Beginning of Hole Indicators I
        
        
        for i in Spaces:
            pen.setColor(qt.Qt.white)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 12));
            qp.drawText(qt.QPointF(self.scale * (47 + 20*i), self.scale * 221), self.text_Hole)
        
        
        #End of Hole Indicators I
        #Beginning of Hole Indicators J
        
        
        for i in Spaces:
            pen.setColor(qt.Qt.white)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 12));
            qp.drawText(qt.QPointF(self.scale * (47 + 20*i), self.scale * 241), self.text_Hole)
        
        
        #End of Hole Indicators J
        #Beginning of Hole Indicators K
        
        
        for i in Spaces:
            pen.setColor(qt.Qt.white)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 12));
            qp.drawText(qt.QPointF(self.scale * (47 + 20*i), self.scale * 261), self.text_Hole)
        
        
        #End of Hole Indicators K
        #Beginning of Hole Indicators L
        
        
        for i in Spaces:
            pen.setColor(qt.Qt.white)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 12));
            qp.drawText(qt.QPointF(self.scale * (47 + 20*i), self.scale * 281), self.text_Hole)
        
        
        #End of Hole Indicators L
        #Beginning of Hole Indicators M
        
        
        for i in Spaces:
            pen.setColor(qt.Qt.white)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 12));
            qp.drawText(qt.QPointF(self.scale * (47 + 20*i), self.scale * 301), self.text_Hole)
        
        
        #End of Hole Indicators M
        #Beginning of Hole Indicators N
        
        
        for i in Spaces:
            pen.setColor(qt.Qt.white)
            qp.setPen(pen)
            qp.setFont(qt.QFont("Arial", 12));
            qp.drawText(qt.QPointF(self.scale * (47 + 20*i), self.scale * 321), self.text_Hole)






