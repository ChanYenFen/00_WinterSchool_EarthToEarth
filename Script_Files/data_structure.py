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
    for i in list:
        new_list.append(value)
    return new_list

def duplicateData_nlist(nlist, value):
    """
    This function duplicate value as many as the length of a nested list
    """
    new_nlist = []
    for l in nlist:
        new_list = []
        for i in l:
            new_list.append(value)
        new_nlist.append(new_list)
    return new_nlist

def nlistItemLength(nlist):
    """
    This function returns how many items in a nested list
    """
    length = 0
    for list in nlist:
        length += len(list)
    return length

def flattenNlist(nlist):
    """
    This function flatten a nested list
    """
    flatten_list= [item for l in nlist for item in l]
    return flatten_list

def chunk_list(list, slice_length):
    """
    This function chunk a list to a nested list
    to match the desired number.
    """
    if slice_length < 1:
        raise ValueError('Chunk size must be greater than 0.')
    new_list = [list[i:i+slice_length] for i in range(0, len(list), slice_length)]
    return new_list

def chunk_nlist(nlist, slice_length):
    """
    This function rearrange the length of sub lists form a nested list
    to match the desired number.
    """
    if slice_length < 1:
        raise ValueError('Chunk size must be greater than 0.')
    flatten_list = [item for l in nlist for item in l]
    new_nlist = [flatten_list[i:i+slice_length] for i in range(0, len(flatten_list), slice_length)]
    return new_nlist

def zip2Lists(list1, list2, flatten = False):
    """
    list1 = [1,1,1]
    list2 = [2,2,2,'A','A','A']
    result = [1, 2, 1, 2, 1, 2, 'A', 'A', 'A']
    """
    # import izip_longest from Python 2 in Rhino
    from itertools import izip_longest

    zipList = list(map(list, izip_longest(list1,list2, fillvalue='None')))
    cleanedZipList = []
    for subList in zipList:
        if 'None' in subList:
            subList.remove('None') 
        cleanedZipList.append(subList)
    flattenZipList = [i for subList in zipList for i in subList if i is not None]
    if not flatten:
        return cleanedZipList
    elif flatten == True:
        return flattenZipList