import os
import json
import csv
import Rhino.Geometry as rg

def remapValues(values, targetMin, targetMax):
    """ Remap numbers into a numeric domain """
    if len(set(values)) >1:
        remappedValues = []
        # Get source domain min and max
        scrMin = min(values)
        scrMax = max(values)
        # Iterate the values and remap
        for v in values:
            rv = ((v-scrMin)/(scrMax-scrMin))*(targetMax-targetMin)+targetMin
            remappedValues.append(rv)
        return remappedValues
    # Else return targeMax for each value
    else:
        return [targetMax]*len(values)

def remapValue(v,ori_Min,ori_Max,targetMin,targetMax):
    rv = ((v-ori_Min)/(ori_Max-ori_Min))*(targetMax-targetMin)+targetMin
    return rv
    
def duplicateData_list(list, value):
    """
    This function duplicate value as many as the length of a list
    """
    new_list = []
    for i in range(len(list)):
        new_list.append(value)
    return new_list

def duplicateData_nlist(nlist, value):
    """
    This function duplicate value as many as the length of a nested list
    """
    new_nlist = []
    for i in range(len(nlist)):
        new_list = []
        for j in range(len(nlist[i])):
            new_list.append(value)
        new_nlist.append(new_list)
    return new_nlist

def cal_list_len(nlist):
    """
    This function returns how many items in a nested list
    """
    length = 0
    for list in nlist:
        length += len(list)
    return length

def flatten_nlist(nlist):
    """
    This function flatten a nested list
    """
    flatten_list= [item for list in nlist for item in list]
    return flatten_list

def rearrange_nlist(nlist, slice_length):
    """
    This function reorganize the length of sub lists form a nested list
    to match the desired number.
    """
    flatten_list = flatten_nlist(nlist)
    new_nlist = [flatten_list[i:i+slice_length] for i in range(0, len(flatten_list), slice_length)]
    return new_nlist
