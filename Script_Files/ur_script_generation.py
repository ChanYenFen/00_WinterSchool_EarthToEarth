from compas.geometry import Frame, Point, Vector
from compas.geometry.transformations.transformations import world_to_local_coordinates
import math as m

# Constants
extruder_IOs = [4, 5, 6, 7]
tool_angle_axis = [0.0, 0.0, 500.0, 0.0, 0.0, 0.0] # TODO! MEASURE AND FIX
blend_radius = 0.035

# ===============================================================
def set_DO(pin, state):
    cmd = "set_digital_out({:d}, {})".format(pin, state)
    return add_whitespace(cmd)


# ===============================================================
def textmsg(string):
    cmd = "textmsg(\"" + string + "\")"
    return add_whitespace(cmd)


# ===============================================================
def set_tcp():
    x, y, z, ax, ay, az = tool_angle_axis
    cmd = "set_tcp(p[{:.5f}, {:.5f}, {:.5f}, {:.5f}, {:.5f}, {:.5f}])".format(x / 1000., y / 1000., z / 1000., ax, ay, az)
    return add_whitespace(cmd)

# ===============================================================
def add_whitespace(string):
    return "\t" + string + "\n"


# ===============================================================
def move_p(x, y, z, ax, ay, az , v, r):
    cmd = "movep(p[%.5f, %.5f, %.5f, %.3f, %.3f, %.3f], v=%.4f, r=%.4f)" % (
        x / 1000., y / 1000., z / 1000., ax, ay, az, v / 1000., max(0.0025, r / 1000.))
    return add_whitespace(cmd)

# ===============================================================
def move_l(x, y, z, ax, ay, az, a, v, r):
    cmd = "movel(p[%.5f, %.5f, %.5f, %.3f, %.3f, %.3f], a=%.4f, v=%.4f, r=%.4f)" % (
        x / 1000., y / 1000., z / 1000., ax, ay, az, a/1000., v / 1000., max(0.000, r))
    return add_whitespace(cmd)

# ===============================================================
def sleep(time):
    cmd = "sleep(%.2f)" % (time)
    return add_whitespace(cmd)

# ===============================================================
def get_fabrication_frame(x,y,z):
    return Frame(Point(x, y, z), Vector(1, 0, 0), Vector(0, -1, 0))

def get_fabrication_frame_by_roate(x,y,z,xAxis):
    # rotated by xAxis
    vx = Vector(xAxis[0], xAxis[1], xAxis[2])
    vy = Vector(0, 0, -1).cross(vx)
    return Frame(Point(x, y, z), vx, vy)

# ===============================================================
def better_grouper(inputs, n):
    iters = [iter(inputs)] * n
    return zip(*iters)

# ===============================================================
def create_script(data, world_origin, travel_velocity):
    script = ""
    script += "def program():\n"
    script += set_tcp()

    frames = []

    for i in range(len(data)):
        data_point = data[str(i)]

        # get data
        color = data_point['color_chanel']
        wait_time = data_point['wait_time']
        x, y, z = data_point['x'] + world_origin[0], data_point['y'] + world_origin[1], data_point['z'] + world_origin[2]
        
        frame = get_fabrication_frame(x,y,z)
        frames.append(frame)
        ax, ay, az = frame.axis_angle_vector[0], frame.axis_angle_vector[1], frame.axis_angle_vector[2] 
        
        # add data to UR script
        #script += ur.move_l_blend(x, y, z, ax, ay, az, travel_velocity, blend_radius)
        script += move_p(x, y, z, ax, ay, az, travel_velocity, blend_radius)
        #script += ur.move_l_blend(rhino_plane, travel_velocity/1000., max(0.0025, blend_radius / 1000.))

        if i % 5 == 0:
            script += textmsg("Point : %d" % i)

        IO = extruder_IOs[color]

        script += set_DO(IO, True)
        # script += set_DO(IO2, True)  # you can turn on more than one motors at the same time.
        script += sleep(wait_time)   
        script += set_DO(IO, False)
        # script += set_DO(IO2, False)  # remember to turn off all the motors you turned on
        #script += sleep(3.0)  


    for IO in extruder_IOs: 
        script += set_DO(IO, False) # make sure all IOs are off

    script += 'end\n'
    script += '\Awesome_glass_coloring_design()\n'
    return script, frames

def create_script_ptEffect(data, world_origin, travel_velocity):
    script = ""
    script += "def program():\n"
    script += set_tcp()

    frames = []

    #acceleration = 0

    for i in range(len(data)):
        data_point = data[str(i)]

        # get data
        color = data_point['color_chanel']
        wait_time = data_point['wait_time']
        xAxis = data_point["rotate_direction"]

        x, y, z = data_point['x'] + world_origin[0], data_point['y'] + world_origin[1], data_point['z'] + world_origin[2]
        
        frame = get_fabrication_frame_by_roate(x,y,z,xAxis)
        frames.append(frame)
        ax, ay, az = frame.axis_angle_vector[0], frame.axis_angle_vector[1], frame.axis_angle_vector[2] 
        
        # add data to UR script
        script += move_p(x, y, z, ax, ay, az,  travel_velocity, blend_radius)
        
        if i % 5 == 0:
            script += textmsg("Point : %d" % i)

        for c in color:
            IO = extruder_IOs[c]
            script += set_DO(IO, True) # you can turn on more than one motors at the same time.
        
        sorted_color = [c for _, c in sorted(zip(wait_time, color))]

        # wait itme change by gap
        sorted_wait_time = sorted(wait_time)
        
        gap_wait_time = []
        min_time = min(sorted_wait_time)
        gap_wait_time.append(min_time)
        for i in range(len(sorted_wait_time)-1):
            gap = sorted_wait_time[i+1] - sorted_wait_time[i]
            gap_wait_time.append(gap)
        print (gap_wait_time)
        for c, t in zip (sorted_color, gap_wait_time):
            IO = extruder_IOs[c]
            script += sleep(t)
            script += set_DO(IO, False) # remember to turn off all the motors you turned on

        script += sleep(3.0)   

    for IO in extruder_IOs: 
        script += set_DO(IO, False) # make sure all IOs are off

    script += 'end\n'
    script += '\Awesome_glass_coloring_design()\n'
    return script, frames


def create_script_cvEffect(data, world_origin, travel_velocity):
    script = ""
    script += "def program():\n"
    script += set_tcp()

    frames = []
    blend_radius = 0.01
  
    index_list = list(better_grouper(range(len(data)),4))
    
    for i in index_list:
        for n,j in enumerate(i):  
            data_point = data[str(j)]

            # get data
            t_max = data_point['Max_t']
            color = data_point['color_chanel']
            wait_time = data_point['wait_time']
            xAxis = data_point["rotate_direction"]
            toggle = data_point["toggle"]
            x, y, z = data_point['x'] + world_origin[0], data_point['y'] + world_origin[1], data_point['z'] + world_origin[2]
            
            frame = get_fabrication_frame_by_roate(x, y, z, xAxis)
            frames.append(frame)
            ax, ay, az = frame.axis_angle_vector[0], frame.axis_angle_vector[1], frame.axis_angle_vector[2]

            s = t_max/4
            
            script += move_p(x, y, z, ax, ay, az, travel_velocity, blend_radius)
            if toggle == 1:
                for c, t in zip( color, wait_time):
                    IO = extruder_IOs[c]
                    if n == 0 :
                        if 0 < t <= t_max:
                            script += set_DO(IO, True)
                        else:
                            script += set_DO(IO, False)
                    if n == 1 :
                        if s < t <= t_max:
                            script += set_DO(IO, True)
                        else:
                            script += set_DO(IO, False)
                    if n == 2 :
                        if 2*s < t <= t_max:
                            script += set_DO(IO, True)
                        else:
                            script += set_DO(IO, False) 
                    if n == 3 :
                        if 3*s < t <= t_max:
                            script += set_DO(IO, True)
                        else:
                            script += set_DO(IO, False) 
            else :
                for IO in extruder_IOs: 
                    script += set_DO(IO, False) # toggle 0 all IOs are off               
           
            if j % 4 == 3:
                script += textmsg("Point : %d" % j)                          

            # add data to UR script

    # for IO in extruder_IOs: 
    #     script += set_DO(IO, False) # make sure all IOs are off

    script += 'end\n'
    script += '\completed the glass printing()\n'
    return script, frames


def create_script_cbEffect(data, world_origin, travel_velocity):
    script = ""
    script += "def program():\n"
    script += set_tcp()

    frames = []
    blend_radius = 0.01
  
    index_list = list(better_grouper(range(len(data)),4))
    
    for i in index_list:
        for n,j in enumerate(i):  
            data_point = data[str(j)]

            # get data
            t_max = data_point['Max_t']
            color = data_point['color_chanel']
            wait_time = data_point['wait_time']
            xAxis = data_point["rotate_direction"]
            x, y, z = data_point['x'] + world_origin[0], data_point['y'] + world_origin[1], data_point['z'] + world_origin[2]
            
            frame = get_fabrication_frame_by_roate(x, y, z, xAxis)
            frames.append(frame)
            ax, ay, az = frame.axis_angle_vector[0], frame.axis_angle_vector[1], frame.axis_angle_vector[2]
 
            s = t_max/3

            if j % 4 == 0:
                script += move_p(x, y, z, ax, ay, az, travel_velocity, blend_radius)
            else:
                script += move_p(x, y, z, ax, ay, az, travel_velocity/15, blend_radius)

            for c, t in zip( color, wait_time):
                IO = extruder_IOs[c]
                if n == 0 :
                    if 0 < t <= t_max:
                        script += set_DO(IO, True)
                    else:
                        script += set_DO(IO, False)
                if n == 1 :
                    if s < t <= t_max:
                        script += set_DO(IO, True)
                    else:
                        script += set_DO(IO, False)
                if n == 2 :
                    if 2*s < t <= t_max:
                        script += set_DO(IO, True)
                    else:
                        script += set_DO(IO, False) 
 
            if n == 3 :
                for IO in extruder_IOs: 
                        script += set_DO(IO, False)  
                script += sleep(1.0) 
            
            if j % 4 == 3:
                script += textmsg("Point : %d" % j)                          

            # add data to UR script

    # for IO in extruder_IOs: 
    #     script += set_DO(IO, False) # make sure all IOs are off

    script += 'end\n'
    script += '\completed the glass printing()\n'
    return script, frames


if __name__ == "__main__":
    pass