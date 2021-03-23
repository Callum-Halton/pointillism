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

## 2021-03-21 - from Callum

  * Enabled render constants to be changed through the shell interface without
    having to re-PDS.
  * Added constants to allow a combination of several modes to be selected from
    RENDER_CONSTANTS
  * Encapsulated rendering so that it can be called from the shell once a render
    constant has been tweaked.
  * Changed l to be stored by the points as it doesn't need to be re-calculated
    for re-rendering
  * Introduced brightness moderation although it sucks so best to leave turned
    off
  * Re-factored drawDot for less repeated code.

  NEXT STEPS:
  ==========
  * Allow a mode for RGB images where a red point will spawn a green point and a
    green point a blue
    point etc. so that each channel can be represented by 1/3 of the points.
  * Introduce variable-radius DS as a means of changing brightness with density:
    may require seperate algorithm or a lot of ternaries. Not sure which
    approach is best yet.
  * make pixel-sampling radius modifiable via some constant

## 2021-03-21 - from Duncan

  * Formatted your notes above so that the lines are not longer than 80 chars.
  * Add Q = quit option to the interactive system.
  * Limited and enacapsulated the use of integer conversion exception checking
    to very precisely check if the input string can be converted to int and then
    use the function in normal code (in two places) in the main loop.
  * Move the menu rendering into a function and call it every time before user
    inputs option.
  * Removed `RENDER_CONSTANT_ORDER`. This was making the code brittle. Can use
    the keys in the order they are stored, as shown.
  * Added info about current values to the menu.
  * Fixed line wrapping in a number of cases to 80 chars. Please try take care
    of this yourself in the future.
  * Fixed bug in the vary-dot-radius code. It was setting the dot radius to
    `RENDER_CONSTANTS['Max Draw Radius']` squared when varying was disabled.
    This is one of the issues with using ternary statements. They can get really
    hard to read and understand and therefore can instroduce bugs. I
    recommend using ternary statements very minimally and only for very simple
    and short expressions. Motto of software engineering: don't be smart.
  * I removed various instances of trailing whitespace, that can make `git diff`
    confusing. To keep the files clear of trailing whitespace, install the
    Sublime Text package called [Highlight Trailing Whitespace][3].

## 2021-03-22 - from Duncan

  * You committed two large JPEG files to the repo; not good. `git status`
    would have shown you that you were about to commit these, and after
    `git add` they would have shown up as green on `git status`, ready to be
    committed. After grabbing copies of them (so I can use them as source
    images), I removed them from the repo using `git rm ...`. I can provide
    copies of them if the git pull removed them for you. It's important to
    review and revise what you commit, using `git status` and `git diff`.
  * Added `*.jpg` into the .gitignore file so that git ignores all `.jpg` files.
    Note that `.gitignore` already included `*.jpeg`.
  * Added a folder called `input` to put input images into. Note that it's
    good to name folders that will be manipulated on the command line without
    spaces in them. So `input-images` is better than `input images`.
  * Added `.gitkeep` files to both the `input` and `output` folders. Git does
    not explicitly track and commit folders. It tracks folders only so far as
    they are needed to track files. By putting the empty `.gitkeep` files in
    these folders, it forces git to track these folders. So when you pull, you
    will see these two folders appear. You should move your input images into
    the `input` folder.

[1]: https://google.github.io/styleguide/pyguide.html
[2]: https://stackoverflow.com/a/25901060
[3]: https://packagecontrol.io/packages/Highlight%20Trailing%20Whitespace
