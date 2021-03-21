# Notes

## 2021-03-20 - from Duncan

  * Refactored and encapsulated so that there are almost no global variables.
    Just the CAPITALIZED ones at the top remain. I have also organized into
    what seems like a class structure that makes things simpler and easier to
    understand.
  * Wrapped lines appropriately before they cross the 80-character limit. This
    makes the code easier to read and work with. See the
    [Google Python Style Guide][1] for more info about how to do this in a
    standard way in various situations. You can/should also set a ruler at 80
    character in Sublime Text to help with this; [here are instructions][2]. Set
    the rulers in your defaults. DO NOT enable line wrap.
  * I have added very basic command-line argument functionality to
    `poitillism.py` so that it can be passed an alternative filename. I have
    also enhanced `run.sh` to query `whoami` and pass an appropriate filename
    to `pointillism.py` based on who is running the script.

[1]: https://google.github.io/styleguide/pyguide.html
[2]: https://stackoverflow.com/a/25901060

## 2021-03-21 - from Callum

  * Enabled render constants to be changed through the shell interface without having to re-PDS.
  * Added constants to allow a combination of several modes to be selected from RENDER_CONSTANTS
  * Encapsulated rendering so that it can be called from the shell once a render constant has 
    been tweaked.
  * Changed l to be stored by the points as it doesn't need to be re-calculated for re-rendering
  * Introduced brightness moderation although it sucks so best to leave turned off
  * Re-factored drawDot for less repeated code.

  NEXT STEPS:
  ==========
  * Allow a mode for RGB images where a red point will spawn a green point and a green point a blue 
    point etc. so that each channel can be represented by 1/3 of the points.
  * Introduce variable-radius DS as a means of changing brightness with density: may require seperate
    algorith or alot of ternaries, not sure which approach is best yet.
  * make pixel-sampling radius modifiable via some constant

