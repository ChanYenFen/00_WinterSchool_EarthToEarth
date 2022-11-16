"""
This module manages communications and script execution
"""

import socket

import traceback
from struct import *
import math

PORT = 30003        
HOST = "192.168.10.10"



def send_script(script_to_send,robot_id):
    """
    Opens a socket to the Robot and sends a script
    
    Args:
        script_to_send: Script to send to socket
        robot_id: Integer. ID of robot
            
    """
    
    '''Function that opens a socket connection to the robot'''

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((HOST, PORT))
    except:
        print ("Cannot connect to ",HOST,PORT)
        
    s.settimeout(None)
    max_size= 2<<18
    n=len(script_to_send)
    if n>max_size:
        raise Exception("Program too long")
        
    try:
        s.send(script_to_send)
    except:
        print("failed to send")
    s.close()

###############################################################
# ------ Real time 

def listen_to_robot(robot_id):
    # Create dictionary to store data 
    chunks={}   
    chunks["target_joints"] = []
    chunks["actual_joints"]= []
    chunks["forces"] = []
    chunks["pose"] = []
    chunks["time"] = [0]
    
    data = read(HOST, PORT)
    get_messages(data, chunks)
    return chunks

def read(HOST, PORT):
    """
    Method that opens a TCP socket to the robot, receives data from the robot server and then closes socket
    
    Returns:
        data: Data broadcast by the robot. In bytes
    """
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(.1)
    try:
        s.connect((HOST, PORT))
        print("connected")
    except:
        traceback.print_exc()
        print ("Cannot connect to ",HOST,PORT)
    #s.settimeout(None)
    data = s.recv(1024)
    s.close()
    return data

def get_messages(bytes, chunks_info):
    """
    Function parses data stream and selects the following information:
    1) q_target
    2) q_actual
    3) TCP force
    4) Tool Vector
    5) Time
    
    This data is formatted and the chunks dictionary is updated
    for more info see: http://wiki03.lynero.net/Technical/RealTimeClientInterface
    """
    
    # get messages
    q_target = bytes[12:60]
    q_actual = bytes[252:300]
    tcp_force = bytes[540:588]
    tool_vector = bytes[588:636]
    controller_time = bytes[740:748]
    
    # format type: int, 
    fmt_double6 = "!dddddd"
    fmt_double1 = "!d"
    
    #Unpack selected data
    target_joints = unpack(fmt_double6,q_target)
    chunks_info["target_joints"]= (math.degrees(j) for j in target_joints)
    actual_joints = unpack(fmt_double6,q_actual)
    chunks_info["actual_joints"]= (math.degrees(j) for j in actual_joints)
    forces = unpack(fmt_double6,tcp_force)
    chunks_info["forces"]= forces
    pose = unpack(fmt_double6,tool_vector)
    chunks_info["pose"]= pose
    time = unpack(fmt_double1,controller_time)
    chunks_info["time"]= time




if __name__ == '__main__':

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((HOST, PORT))
        print('connected')
    except:
        print ("Cannot connect to ",HOST,PORT)