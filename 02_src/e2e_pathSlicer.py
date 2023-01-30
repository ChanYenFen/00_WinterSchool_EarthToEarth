import os
import json
import csv
import Rhino.Geometry as rg
import math as m

def calc_blendRadius(new_pts, buffer=0.001):
    blend_radiuses = []
    for i in range(len (new_pts)-1):
        pt = new_pts[i]
        pt_1 = new_pts[i+1]
        dist = pt.DistanceTo(pt_1)
        blend_radius = dist*buffer
        blend_radiuses.append(blend_radius)
        if i == len (new_pts)-1:
            blend_radiuses.append(blend_radius)

    #blend_radiuses.append(blend_radiuses[-1]*0.4)
    return blend_radiuses

def divide_crv(crv, seg_len, endInc):
    crv_length = crv.GetLength()
    count = crv_length/seg_len
    params = crv.DivideByCount(count, endInc)
    points = [crv.PointAt(p) for p in params]
    
    tangents = [crv.TangentAt(p) for p in params]
    normals = [rg.Vector3d.CrossProduct(t, rg.Vector3d.ZAxis) for t in tangents]
    return points, normals

def divide_crvs(crvs, seg_len, endInc, returnNest):
    counts = [crv.GetLength() / seg_len for crv in crvs]
    param_nList =[]
    param_nList.append([crv.DivideByCount(count, endInc) for (crv,count) in zip(crvs,counts)])

    wayPoints_nList = []
    for crv, params in zip(crvs,*param_nList):
        points = [crv.PointAt(p) for p in params]
        if returnNest:
            wayPoints_nList.append(points)
        else:
            wayPoints_nList.extend(points)
    return wayPoints_nList 

def rhino_to_robot_space(plane, rhino_centerPt, robot_centerPt):
    rhino_centerPlane = rg.Plane(rhino_centerPt, rg.Vector3d.XAxis, rg.Vector3d.YAxis)
    robot_centerPlane = rg.Plane(robot_centerPt, rg.Vector3d.XAxis, rg.Vector3d.YAxis)
    T = rg.Transform.PlaneToPlane(rhino_centerPlane, robot_centerPlane)
    plane.Transform(T)
    return plane

def contour_XY(brep, layer_height, simplify):
    contour_crvs =[]
    bbox = rg.Brep.GetBoundingBox(brep, rg.Plane.WorldXY)
    lowest_pt = bbox.Min
    highest_pt = bbox.Max
    contour_range = int((highest_pt.Z-lowest_pt.Z)/layer_height) +1
    for i in range(contour_range):
        plane_ori = lowest_pt + rg.Vector3d(0,0,1)*layer_height*i
        intersection_plane = rg.Plane(plane_ori, rg.Vector3d.XAxis, rg.Vector3d.YAxis)
        intersection_events = rg.Intersect.Intersection.BrepPlane(brep, intersection_plane,0.01)
        if intersection_events[0]:
            layer_crvs = intersection_events[1]
            if len(layer_crvs)>1:
                layer_crvs = rg.Curve.JoinCurves(layer_crvs)
            for crv in layer_crvs:
                if simplify:
                    crv.Simplify(rg.CurveSimplifyOptions.All, distanceTolerance=0.01, angleToleranceRadians=0.01)
                contour_crvs.append(crv)
    return contour_crvs
    
def contour(srf, inter_origin, normal, layer_height, simplify):
    contour_crvs =[]
    for i in range(1000):
        intersection_plane = rg.Plane(inter_origin+normal*i, rg.Vector3d.XAxis, rg.Vector3d.YAxis)
        intersection_events = rg.Intersect.Intersection.BrepPlane(srf, intersection_plane,0.01)

        if intersection_events[0]:
            layer_crvs = intersection_events[1]
            if len(layer_crvs)>1:
                layer_crvs = rg.Curve.JoinCurves(layer_crvs)
            for crv in layer_crvs:
                if simplify:
                    crv.Simplify(rg.CurveSimplifyOptions.All, distanceTolerance=0.01, angleToleranceRadians=0.01)
                contour_crvs.append(crv)
    return contour_crvs

def find_offset_distance(interval):
    return m.sin(m.radians(60))*interval

def offset_crv(crv, base_pt, distance):
    offset_crv = rg.Curve.Offset(crv, base_pt, rg.Vector3d.ZAxis, distance, 0.01, 0.01, True, rg.CurveOffsetCornerStyle.None, rg.CurveOffsetEndStyle.None)
    return offset_crv

def offset_crvs(crv, distance, seg_len, bothSides, side, offset_layers):
    """
    This function return a list of offset curves form an input curve.
    Seg is about the precision of the results which suggested set to 10.0
    If it is a closed curve,
    set side = 0 to get offset curves outside,
    set side = 1 to get offset curves inside.
    """
    params = crv.DivideByLength(seg_len, True)
    points = [crv.PointAt(p) for p in params]
    tangents = [crv.TangentAt(p) for p in params]
    normals = [rg.Vector3d.CrossProduct(t, rg.Vector3d.ZAxis) for t in tangents]
    
    pts_nlists =[]
    if bothSides:
        side = None
        for i in range(1,offset_layers+1):
            side_0_pts =[]
            side_1_pts =[]
            for pt,nor in zip(points,normals):
                side_0 = rg.Transform.Translation(nor*i*distance)
                side_1 = rg.Transform.Translation(nor*i*distance *-1)
                pt_0 = pt.Clone()
                pt_0.Transform(side_0)
                side_0_pts.append(pt_0)
                pt_1 = pt.Clone()
                pt_1.Transform(side_1)
                side_1_pts.append(pt_1)
            pts_nlists.append(side_0_pts)
            pts_nlists.append(side_1_pts)
    if not bothSides:
        if side ==0:
            dir = 1
        elif side ==1:
            dir = -1
        for i in range(1,offset_layers+1):
                side_0_pts =[]
                for pt,nor in zip(points,normals):
                    side_0 = rg.Transform.Translation(nor*i*distance*dir)
                    pt_0 = pt.Clone()
                    pt_0.Transform(side_0)
                    side_0_pts.append(pt_0)
                pts_nlists.append(side_0_pts)
    offset_crvs= []
    for pts in pts_nlists:
        if crv.IsClosed:
            pts.append(pts[0].Clone())
            offset_crv = rg.Curve.CreateInterpolatedCurve(pts, degree=3, knots=rg.CurveKnotStyle.Uniform)
            offset_crv.MakeClosed(0.001)
            offset_crvs.append(offset_crv)
        else:
            offset_crv = rg.Curve.CreateInterpolatedCurve(pts, degree=3, knots=rg.CurveKnotStyle.Chord)
            offset_crvs.append(offset_crv)      
    return offset_crvs
