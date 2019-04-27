import gcodesender as gc
import os
import operator

def ensure_directory(file_path):
    """Checks the given file path for a directory, and creates one if not already present.

    Args:
        file_path: a string representing a valid URL
    """

    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

#-----------------------------------------------------------------------------------------------------------------------

def setup():
    """Prints initial directions to the feedback frame upon startup and after completing a run.
    """

    print("> Make your selections and")
    print("> press '\"'GO'\" to begin")
    print(" ")

#-----------------------------------------------------------------------------------------------------------------------

def sort_to_snake(locations, type):
    """Sorts the list of locations to form a 'snake' pattern through the wells

    Causes imager to move fully down one column of the tray (A01-1 -- H01-3)
    before changing rows.
    Consecutive rows will be traversed in opposite directions (H02-3 -- A02-1)
    This ensures that the imager only moves in one direction at a time, minimizing
    transit errors.

    Args:
        locations: A list of strings of wells to be imaged.

    Returns:
        A list of locations sorted to the specifications described above."""

    if type == "Intelli-plate 96-3":
        rows = [[]]
        retVal = []
        for i in range(12):
            init = []
            rows.append(init)

        for loc in locations:
            row = int(loc[1] + loc[2])
            rows[row].append(loc)

        for obj in rows[0::2]:
            obj.sort(key=operator.itemgetter(0,4), reverse = True)

        for obj in rows:
            for i in obj:
                retVal.append(i)
        return retVal

    elif type == "Greiner 1536":
        cols = [[]]
        retVal = []
        for i in range(48):
            init = []
            cols.append(init)

        for loc in locations:
            col = ((int(loc[1] + loc[2]) - 1) * 4) + int(loc[6]) - 1
            cols[col].append(loc)

        for obj in cols[1::2]:
            obj.sort(key=operator.itemgetter(0,4), reverse=True)

        for obj in cols:
            for i in obj:
                retVal.append(i)
        return retVal

####################################################################################################################


