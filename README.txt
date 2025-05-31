Control Builder – User Manual
Author: Written by Sarah Greifer, inspired by *wiz_controllers* by skif

---

Description

The Control Builder is a custom Maya tool for creating rigging controllers with live color previews, grouping, locking/hiding attributes, and more. It supports importing custom controller shapes, mirroring across axis, and modifying existing controllers.

---

How to Launch

1. Place the script (OOP_build_controllers.py) into your Maya scripts directory.
2. Open Maya and run the following in the Python tab of your Script Editor:

    import OOP_build_controllers as bcf
    bcf.BuildControllersUI().show()
    bcf.ui.show()

Optionally, assign it to a shelf button for quick access.

---

Setup (Required for Custom Shapes)

I have build out a folder of custom shapes that can be used as controllers.


If your Maya user folder is not located on C:/ (e.g., on a server), go to the top of the script and replace:

    self.custom_shape_folder = "REPLACE WITH YOUR CUSTOM FILE PATH"

    with your local file path. For example:

    self.custom_shape_folder = "H:/maya/scripts/BuildControllers/shapes"


This ensures cross-machine compatibility for controller libraries.

---

Tool Instructions

1. Open the tool. The title will read "Control Builder".

2. Color Index:
   Use the color slider for a live preview of your controller's override color.

3. Shape Dropdown:
   Choose a built-in or custom shape from the dropdown.

4. Name Field:
   Enter a name for your controller. _CTRL will be appended automatically.

5. Grouping:
   If checked, your controller will be placed in an offset group (_CTRL_0) and an SDK group (_CTRL_SDK), ensuring zero transforms on the control itself.

6. Lock & Hide Options:
   Select attributes you want locked/hidden from the channel box (Translate, Rotate, Scale, Visibility).

7. Placement:
   - Select an object in your scene to snap the controller to that object
   - If nothing is selected, the controller appears at world origin

8. Create Controller Button:
   Builds the controller using all the selected options.

---

Mirror Tool (NEW)

After creating a controller with a prefix L_, select it and click Mirror Controller from the UI.
This will duplicate and flip the controller in world space to the opposite side with proper naming.

---

Change Color (NEW)

Under Additional Tools > Change Color:

- Use the existing color slider at the top of the UI
- Select a controller (or multiple)
- Click Apply Color to Selected

---

Help

The Help menu includes a direct link to sarahgreifer.com for tool support.
