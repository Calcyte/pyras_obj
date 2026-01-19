# pyras_obj
This is a real time OpenGL rasterizor programmed in Python using pygame and PyOpenGl.
# File support
There is currently only support for .OBJ files and their associated file types (.MTL and texture files).Texture files must be .JPEG or .PNG, and must be placed within the /assets/bucket folder. Models must be placed within /assets/models.
# Camera Controls
Camera view angle is based off mouse movement, and the movement keys are WASD as per most video games.
# Multi monitor support
This program currently does not work on devices with multiple monitors, it will always display on DP1 or HDMI1.
