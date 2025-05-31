"""

Build Controllers Tool

DESCRIPTION: build_controller is a multi-tool that allows for creation of controls using curves with customizable features (ex/ title, lock/hide attributes/color)

AUTHOR: Sarah Greifer, inspired by wiz_controllers by Alex Kyshtymov (skif)

USAGE: Create a customized control for rigging

"""

# IMPORTS
import os
import maya.cmds as cmds
import webbrowser

# CLASS
class BuildControllersUI:
    def __init__(self):
        self.window = "mc"
        self.title = "Control Builder"
        self.size = (360, 380)
        self.color_override_index = 22

        # SHAPES
        # Existing maya curves
        self.shape_options = {
            "Circle": self.shp_circle,
            "Square": self.shp_square,
        }

        # Custom curves
        self.custom_shape_folder = os.path.expanduser(
            "~/Documents/maya/scripts/BuildControllers/shapes"
        )
        shape_names = ["template_ARROW", "template_ARROW3D", "template_ARROW4SIDED", "template_BULB", "template_CUBE", "template_HAND", "template_LOCATOR", "template_ORIENT", "template_SPHERE"]  # Add more here
        self.shape_options.update({
            name.replace("template_", "").capitalize(): 
                lambda n, s=name: self.load_single_shape_file(s, n)
            for name in shape_names
        })

        # Color preview index
        self.maya_colors = [
            (0.000, 0.000, 0.800), (0.000, 0.000, 0.000), (0.2, 0.2, 0.2), (0.5, 0.5, 0.5),
            (0.6, 0.0, 0.0), (0.0, 0.0, 0.4), (0.0, 0.0, 1.0), (0.0, 0.3, 0.0),
            (0.3, 0.0, 0.3), (1.0, 0.0, 0.5), (0.9, 0.4, 0.0), (0.4, 0.2, 0.0),
            (0.8, 0.3, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0),
            (1.0, 1.0, 1.0), (1.0, 1.0, 0.0), (0.5, 0.8, 1.0), (0.5, 1.0, 0.5),
            (1.0, 0.7, 0.6), (1.0, 0.8, 0.6), (1.0, 1.0, 0.6), (0.3, 0.7, 0.3),
            (1.0, 0.5, 0.0), (0.9, 0.7, 0.1), (0.7, 1.0, 0.2), (0.2, 0.8, 0.7),
            (0.0, 0.7, 0.7), (0.4, 0.7, 1.0), (1.0, 0.0, 1.0), (1.0, 0.6, 0.8)
        ]

    # ALIGN CONTROLLER
    def align_controller_to_target(self, ctrl, target):
        """
        Align the offset group of a controller to a target so the controller itself remains zeroed.
        Assumes grouping hierarchy: ctrl <- SDK <- offset
        """
        sdk = cmds.listRelatives(ctrl, parent=True)[0]
        offset = cmds.listRelatives(sdk, parent=True)[0]

        if not cmds.objExists(target):
            cmds.warning(f"Target object '{target}' does not exist.")
            return

        # Applies alignment to the offset group, NOT the controller itself (allows for animators to key on zeroed out controls)
        temp_constraint = cmds.parentConstraint(target, offset, maintainOffset=False)
        cmds.delete(temp_constraint)

    # TOOL UI
    def show(self):
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)

        cmds.window(self.window, title=self.title, widthHeight=self.size)

        # Menu Bar
        cmds.menuBarLayout()
        cmds.menu(label="File")
        cmds.menuItem(label="Exit", command=lambda *args: cmds.deleteUI(self.window, window=True))
        cmds.menu(label="Help", helpMenu=True)
        cmds.menuItem(label="Script Help", command=lambda *args: self.open_help())

        cmds.columnLayout(adjustableColumn=True)

        # Mirror selection
        cmds.separator(h=10)
        cmds.text(label="Tools")
        cmds.button(label="Mirror Selected", c=lambda *_: self.mirror_selected_controller())
        cmds.separator(h=10)


        # Color preview
        cmds.frameLayout(label="Color", collapsable=True)
        cmds.columnLayout(adjustableColumn=True, columnAttach=("left", 10), rowSpacing=10)
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(200, 55))
        cmds.intSlider("cis01", width=200, min=0, max=31, value=0, step=1,
            dragCommand=lambda *args: self.store_and_update_color(),
            changeCommand=lambda *args: self.store_and_update_color())
        cmds.iconTextButton("clr", width=55, bgc=(0.467, 0.467, 0.467))
        cmds.setParent("..")
        cmds.setParent("..")
        cmds.setParent("..")

        # Additional Tools > Change Color
        cmds.frameLayout(label="Additional Tools", collapsable=True, collapse=True, mw=5)
        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label="Use current Color Index selection (above)")
        cmds.button(label="Apply Color to Selected", c=self.change_selected_controller_color)
        cmds.setParent("..")
        cmds.setParent("..")

        # Shape selection
        cmds.frameLayout(label="Controller Shape", collapsable=True)
        cmds.columnLayout(adjustableColumn=True)
        cmds.optionMenu("shapeMenu", label="Select Shape:")
        for shape_name in self.shape_options.keys():
            cmds.menuItem(label=shape_name)
        cmds.setParent("..")
        cmds.setParent("..")

        # Name and grouping
        cmds.frameLayout(label="Name & Group", collapsable=True)
        cmds.columnLayout(adjustableColumn=True)
        cmds.textField("tfName", placeholderText="Enter controller name...")
        cmds.checkBox("grp01", label="Group", value=True)
        cmds.textField("text01", visible=False)
        cmds.setParent("..")
        cmds.setParent("..")

        # LOCK AND HIDE SYSTEM UI
        # These functions lock/hide attributes based on checkboxes
        cmds.frameLayout(label="Lock & Hide", collapsable=True)
        cmds.columnLayout(adjustableColumn=True)

        # TRANSFORMATION COLUMNS FOR LOCK AND HIDE SYSTEM
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=3, columnAlign=(1, 'center'),
                    columnAttach=[(1, 'both', 10), (2, 'both', 10), (3, 'both', 10)])

        # Translate Column
        cmds.columnLayout()
        cmds.text(label="Translate", align='center')
        cmds.checkBox("t", label="All",
                    onc=lambda *args: self.toggle_group('t', True),
                    ofc=lambda *args: self.toggle_group('t', False))
        for axis in "xyz":
            cmds.checkBox(f"t{axis}", label=axis.upper())
        cmds.setParent("..")

        # Rotate Column
        cmds.columnLayout()
        cmds.text(label="Rotate", align='center')
        cmds.checkBox("r", label="All",
                    onc=lambda *args: self.toggle_group('r', True),
                    ofc=lambda *args: self.toggle_group('r', False))
        for axis in "xyz":
            cmds.checkBox(f"r{axis}", label=axis.upper())
        cmds.setParent("..")

        # Scale Column
        cmds.columnLayout()
        cmds.text(label="Scale", align='center')
        cmds.checkBox("s", label="All",
                    onc=lambda *args: self.toggle_group('s', True),
                    ofc=lambda *args: self.toggle_group('s', False))
        for axis in "xyz":
            cmds.checkBox(f"s{axis}", label=axis.upper())
        cmds.setParent("..")

        cmds.setParent("..")  # Close rowLayout

        cmds.separator(height=10, style='none')
        cmds.checkBox("v", label="Visibility", align='center')

        cmds.setParent("..")  # Close columnLayout
        cmds.setParent("..")  # Close frameLayout


        cmds.button(label="Create Controller", command=lambda *args: self.create_controller_button())
        cmds.showWindow(self.window)

    # LOCK AND HIDE SYSTEM FUNCTIONS
    def lockhide_target(self, obj):
        attrs = {
            "t": ["tx", "ty", "tz"],
            "r": ["rx", "ry", "rz"],
            "s": ["sx", "sy", "sz"],
            "v": ["visibility"]
        }
        for group, keys in attrs.items():
            for attr in keys:
                full_attr = f"{obj}.{attr}"
                checkbox = attr if attr != "visibility" else "v"
                if cmds.checkBox(checkbox, exists=True):
                    lock = cmds.checkBox(checkbox, query=True, value=True)
                    try:
                        cmds.setAttr(full_attr, lock=False)
                        cmds.setAttr(full_attr, keyable=not lock)
                        cmds.setAttr(full_attr, lock=lock)
                    except Exception as e:
                        print(f"Could not lock/hide {full_attr}: {e}")

    def toggle_group(self, prefix, state):
        for axis in "xyz":
            attr = f"{prefix}{axis}"
            cmds.checkBox(attr, edit=True, value=state)
        selected = cmds.ls(selection=True)
        if selected:
            self.lockhide_target(selected[0])

    def sync_from_selected(self):
        sele = cmds.ls(selection=True)
        if not sele:
            return
        obj = sele[0]
        attrs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "visibility"]
        for attr in attrs:
            locked = cmds.getAttr(f"{obj}.{attr}", lock=True)
            check = attr if attr != "visibility" else "v"
            cmds.checkBox(check, edit=True, value=locked)
        self.update_group_checkbox("t")
        self.update_group_checkbox("r")
        self.update_group_checkbox("s")

    def update_group_checkbox(self, prefix):
        total = sum(cmds.checkBox(f"{prefix}{axis}", query=True, value=True) for axis in "xyz")
        cmds.checkBox(prefix, edit=True, value=(total == 3))

    # COLOR PREVIEW
    # auto-update as you slide
    def update_color_preview(self):
        val = cmds.intSlider("cis01", query=True, value=True)
        color = self.maya_colors[val] if 0 <= val < len(self.maya_colors) else (0.467, 0.467, 0.467)
        cmds.iconTextButton("clr", edit=True, bgc=color)

    def store_and_update_color(self):
        self.color_override_index = cmds.intSlider("cis01", q=True, value=True)
        self.update_color_preview()

    # CONTROLLER BUTTON
    def create_controller_button(self):
        sel = cmds.ls(selection=True)
        if sel:
            cmds.textField("text01", edit=True, text=sel[0])
        target = cmds.textField("text01", query=True, text=True)
        ctrl = self.create_controller()
        if target and cmds.objExists(target):
            self.align_controller_to_target(ctrl, target)
        self.apply_color(ctrl)

        # Freeze transforms before locking
        cmds.makeIdentity(ctrl, apply=True, t=1, r=1, s=1, n=0)

        self.lockhide_target(ctrl)

        cmds.select(clear=True)

    # CONTROLLER GROUP HIERARCHY
    def create_controller(self):
        name = cmds.textField("tfName", query=True, text=True)
        selected_shape = cmds.optionMenu("shapeMenu", query=True, value=True)
        ctrl_func = self.shape_options.get(selected_shape, self.shp_circle)
        ctrl = ctrl_func(name)
        ctrl = cmds.rename(ctrl, f"{name}_CTRL")
        cmds.makeIdentity(ctrl, apply=True, t=0, r=0, s=1, n=0)
        cmds.xform(ctrl, os=True, piv=(0, 0, 0))

        if cmds.checkBox("grp01", query=True, value=True):
            sdk_grp = cmds.group(ctrl, name=f"{name}_CTRL_SDK")
            cmds.xform(sdk_grp, os=True, piv=(0, 0, 0))
            offset_grp = cmds.group(sdk_grp, name=f"{name}_CTRL_0")
            cmds.xform(offset_grp, os=True, piv=(0, 0, 0))

        return ctrl

    # APPLY COLOR TO CONTROLLER
    def apply_color(self, obj):
        val = cmds.intSlider("cis01", query=True, value=True)
        if cmds.objExists(obj):
            cmds.setAttr(f"{obj}.overrideEnabled", 1)
            cmds.setAttr(f"{obj}.overrideColor", val)

    # LOADS CUSTOM SHAPE FILE FROM SHAPES FOLDER
    # Includes debugging in case file does not exist
    def load_single_shape_file(self, shape_name, new_name):
        folder = self.custom_shape_folder
        file_path = f"{folder}/{shape_name}.ma"
        try:
            cmds.file(file_path, i=True, type="mayaAscii", ra=True, mergeNamespacesOnClash=False,
                      namespace="tmpShape", options="v=0")
        except Exception as e:
            cmds.warning(f"Could not import shape file: {e}")
            return None
        full_name = f"tmpShape:{shape_name}"
        if not cmds.objExists(full_name):
            cmds.warning(f"Shape '{shape_name}' not found in imported file.")
            return None
        renamed = cmds.rename(full_name, f"{new_name}_CTRL")
        try:
            cmds.namespace(removeNamespace="tmpShape", mergeNamespaceWithRoot=True)
        except:
            pass
        return renamed

    # MIRROR SELECTION FUNCTION
    def mirror_selected_controller(self):
        """
        Mirrors the currently selected L_ controller by duplicating its hierarchy (offset → sdk → ctrl),
        mirroring across X, flipping orientation via Y and Z rotation, and renaming to R_ equivalents.
        Keeps the controller and SDK group zeroed.
        """
        import re
        sel = cmds.ls(selection=True, type="transform")
        if not sel:
            cmds.warning("Please select a controller or its offset group to mirror.")
            return

        ctrl = sel[0]
        parent = cmds.listRelatives(ctrl, parent=True, type="transform")
        grandparent = cmds.listRelatives(parent, parent=True, type="transform") if parent else []

        if grandparent:
            offset = grandparent[0]
            sdk = parent[0]
        elif parent:
            offset = parent[0]
            sdk = ctrl
            ctrl = cmds.listRelatives(sdk, children=True, type="transform")[0]
        else:
            cmds.warning("Could not resolve controller hierarchy. Please select a valid controller.")
            return

        if not offset.startswith("L_"):
            cmds.warning("Controller must start with 'L_' to mirror.")
            return

        # Duplicate the offset group (with children)
        dup_offset = cmds.duplicate(offset, renameChildren=True)[0]

        # Create temp group to capture mirrored world transform
        temp_grp = cmds.createNode('transform', name='tempMirrorGRP')
        cmds.delete(cmds.parentConstraint(offset, temp_grp, mo=False))

        # Mirror transform in world space
        pos = cmds.xform(temp_grp, q=True, ws=True, t=True)
        rot = cmds.xform(temp_grp, q=True, ws=True, ro=True)
        pos[0] *= -1
        rot[1] *= -1  # flip Y
        rot[2] *= -1  # flip Z

        cmds.xform(temp_grp, ws=True, t=pos)
        cmds.xform(temp_grp, ws=True, ro=rot)
        cmds.delete(cmds.parentConstraint(temp_grp, dup_offset, mo=False))
        cmds.delete(temp_grp)

        # Resolve hierarchy and rename with R_ prefix
        dup_sdk = cmds.listRelatives(dup_offset, children=True, type="transform")[0]
        dup_ctrl = cmds.listRelatives(dup_sdk, children=True, type="transform")[0]

        dup_offset = cmds.rename(dup_offset, re.sub(r'^L_', 'R_', offset))
        dup_sdk = cmds.rename(dup_sdk, re.sub(r'^L_', 'R_', sdk))
        dup_ctrl = cmds.rename(dup_ctrl, re.sub(r'^L_', 'R_', ctrl))

        print(f"Mirrored controller created: {dup_ctrl}")
        return dup_ctrl

    # UPDATE SELECTED CONTROLLER COLOR
    def change_selected_controller_color(self, *_):
        sel = cmds.ls(selection=True, type="transform")
        if not sel:
            cmds.warning("Please select one or more controllers to change color.")
            return

        for obj in sel:
            shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
            for shape in shapes:
                try:
                    cmds.setAttr(shape + ".overrideEnabled", 1)
                    cmds.setAttr(shape + ".overrideColor", self.color_override_index)
                except Exception as e:
                    cmds.warning(f"Could not override color on {shape}: {e}")

    # HELP SECTION
    def open_help(self):
        webbrowser.open("https://sarahgreifer.com")

    # MAYA BASIC CURVES
    def shp_circle(self, name):
        return cmds.circle(name=f"{name}_CTRL", normal=(0, 1, 0), radius=3)[0]

    def shp_square(self, name):
        pts = [(-1, 0, 1), (1, 0, 1), (1, 0, -1), (-1, 0, -1), (-1, 0, 1)]
        return cmds.curve(name=f"{name}_CTRL", d=1, p=pts)



# Example usage:
# ui = BuildControllersUI()
# ui.show()
# OR
# import oop_build_controllers as bcf
# bcf.ui = bcf.BuildControllersUI()
# bcf.ui.show()
