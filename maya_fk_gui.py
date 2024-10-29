#!/usr/bin/env python
# SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Kris Hernandez

:synopsis:
    This module provides a Maya tool for working with joint and curve selection.

:description:
    This module is focused on practicing  on how to make custom GUIs for tools in 
    Maya. The script that is running within the GUI selects and manipulates joints and curves 
    in Maya, including history deletion, transformation freezing, and constraints. The original 
    script used, was referenced from class material. 

:applications:
    Maya

:see_also:
    N/A
"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Default Python Imports
from PySide2 import QtGui, QtWidgets
from maya import cmds, OpenMayaUI as omui
from shiboken2 import wrapInstance

#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

def get_maya_window():
    """
    Get a pointer to the Maya window.

    :return: A pointer to the Maya window.
    :rtype: QWidget
    """
    maya_main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(maya_main_window_ptr), QtWidgets.QWidget)

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

class JointCurveTool(QtWidgets.QDialog):
    """
    GUI for selecting and manipulating joints and curves in Maya.
    """
    def __init__(self):
        super(JointCurveTool, self).__init__(parent=get_maya_window())
        self.setWindowTitle("Joint-Curve Tool")
        self.setGeometry(300, 300, 350, 200)
        
        self.init_gui()

    def init_gui(self):
        """
        Set up the layout and widgets.
        """
        # Main layout
        main_vb = QtWidgets.QVBoxLayout(self)
        
        # Information and labels
        self.info_label = QtWidgets.QLabel("Select one joint and one curve.")
        main_vb.addWidget(self.info_label)

        self.selected_label = QtWidgets.QLabel("No selection made.")
        main_vb.addWidget(self.selected_label)
        
        # Buttons layout
        btn_hb = QtWidgets.QHBoxLayout()
        self.run_button = QtWidgets.QPushButton("Run Tool")
        self.run_button.clicked.connect(self.run_tool)
        btn_hb.addWidget(self.run_button)
        
        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        btn_hb.addWidget(self.close_button)
        
        main_vb.addLayout(btn_hb)
        self.update_selection()

    def update_selection(self):
        """
        Updates the selected items based on the current Maya selection.
        """
        sel = cmds.ls(selection=True)
        if not sel or len(sel) != 2:
            self.selected_label.setText("You must select one joint and one curve.")
            self.run_button.setEnabled(False)
        else:
            joint, curve = self.identify_selection(sel)
            if joint and curve:
                self.selected_label.setText(f"Selected Joint: {joint}\nSelected Curve: {curve}")
                self.run_button.setEnabled(True)
            else:
                self.selected_label.setText("Selection must include one joint and one curve.")
                self.run_button.setEnabled(False)

    def identify_selection(self, sel):
        """
        Identifies and returns the joint and curve from the selection.
        
        :param: The list of selected objects.
        :return: The selected joint and curve.
        :type: tuple
        """
        sel_joint, sel_curve = None, None
        for obj in sel:
            if cmds.objectType(obj) == 'joint':
                sel_joint = obj
            elif cmds.objectType(obj) == 'transform':
                sel_curve = obj
        return sel_joint, sel_curve

    def run_tool(self):
        """
        Main logic for executing the tool's actions.
        """
        sel_joint, sel_curve = self.identify_selection(cmds.ls(selection=True))
        
        if not sel_joint or not sel_curve:
            cmds.warning("Selection must contain one joint and one curve.")
            return

        # Delete history and freeze transformations
        cmds.makeIdentity(sel_curve, apply=True)
        cmds.delete(sel_curve, constructionHistory=True)
        
        # Rename curve based on joint name
        ctrl_name = sel_joint.replace('BIND', 'CC')
        ctrl_name = cmds.rename(sel_curve, ctrl_name)
        
        # Group the curve
        grp_name = ctrl_name.replace('CC', 'cc_GRP')
        grp_name = cmds.group(ctrl_name, name=grp_name)
        
        # Move the group to the joint position
        result = cmds.parentConstraint(sel_joint, grp_name, maintainOffset=False)
        
        # Delete the parent constraint
        cmds.delete(result)
        
        # Constrain the controller to the joint
        cmds.orientConstraint(ctrl_name, sel_joint, maintainOffset=False)
        
        # Parent constrain the group to the parent joint
        parent_joint = cmds.pickWalk(sel_joint, direction='up')[0]
        cmds.parentConstraint(parent_joint, grp_name, maintainOffset=True)
        
        self.info_label.setText("Tool executed successfully.")
        self.update_selection()

def show_tool():
    """
    Displays the Joint-Curve Tool GUI.
    """
    global tool_instance
    tool_instance = JointCurveTool()
    tool_instance.show()

# Run the GUI
show_tool()


