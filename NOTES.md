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
    character in Sublime Text to help with this. [Here are instructions][2]. Set
    the rulers in your defaults. Don't enable line wrap.
  * I have added very basic command-line argument functionality to
    `poitillism.py` so that it can be passed an alternative filename. I have
    also enhanced `run.sh` to query `whoami` and pass an appropriate filename
    to `pointillism.py` based on who is running the script.

[1]: https://google.github.io/styleguide/pyguide.html
[2]: https://stackoverflow.com/a/25901060