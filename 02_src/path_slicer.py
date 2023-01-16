import os
import json
import csv
import Rhino.Geometry as rg
import math as m

def divide_crv(crv, seg_len, endInc):
    crv_length = crv.GetLength()
    count = crv_length/seg_len
    params = crv.DivideByCount(count, endInc)
    planes = [rg.Plane(crv.PointAt(p), rg.Vector3d.XAxis, rg.Vector3d.YAxis) for p in params]
    
    tangents = [crv.TangentAt(p) for p in params]
    normals = [rg.Vector3d.CrossProduct(t, rg.Vector3d.ZAxis) for t in tangents]
    return planes, normals

def divide_crvs(crvs, seg_len, endInc):
    counts = [crv.GetLength() / seg_len for crv in crvs]
    param_lists =[]
    param_lists.append([crv.DivideByCount(count, endInc) for (crv,count) in zip(crvs,counts)])
    way_plane_lists = []

    for crv, params in zip(crvs,*param_lists):
        planes = [rg.Plane(crv.PointAt(p), rg.Vector3d.XAxis, rg.Vector3d.YAxis) for p in params]
        way_plane_lists.append(planes)
    return way_plane_lists

def rhino_to_robot_space(plane, rhino_centerPt, robot_centerPt):
    rhino_centerPlane = rg.Plane(rhino_centerPt, rg.Vector3d.XAxis, rg.Vector3d.YAxis)
    robot_centerPlane = rg.Plane(robot_centerPt, rg.Vector3d.XAxis, rg.Vector3d.YAxis)
    orient = rg.Transform.PlaneToPlane(rhino_centerPlane, robot_centerPlane)
    plane.Transform(orient)
    return plane

def contour(srf, base_pt, layer_thickness):
    contours = []
    height_valuse = []
    for i in range(1000):
        intersection_plane = rg.Plane(rg.Point3d(0,0,base_pt.Z+layer_thickness *i), rg.Vector3d.XAxis, rg.Vector3d.YAxis)
        intersection_events = rg.Intersect.Intersection.BrepPlane(srf, intersection_plane,0.01)

        if intersection_events[0]:
            layer_crvs = intersection_events[1]
            for crv in layer_crvs:
                ref_pt = crv.PointAt(0)
                ref_ptZ = round(ref_pt.Z,2)
                contours.append(crv)
                height_valuse.append(ref_ptZ)
    return contours, height_valuse

def find_offset_distance(interval):
    return m.sin(m.radians(60))*interval

def offset(crv, base_pt, distance):
    offset_crv = rg.Curve.Offset(crv, base_pt, rg.Vector3d.ZAxis, distance, 0.01, 0.01, True, rg.CurveOffsetCornerStyle.None, rg.CurveOffsetEndStyle.None)
    return offset_crv

def offset_crv(crv, distance, seg_len, bothSides, side, offset_layers):
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
        if side ==1:
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
            offset_crv = rg.Curve.CreateInterpolatedCurve(pts, degree=3, knots=rg.CurveKnotStyle.ChordPeriodic)
            offset_crv.MakeClosed(0.001)
            offset_crvs.append(offset_crv)
        else:
            offset_crv = rg.Curve.CreateInterpolatedCurve(pts, degree=3, knots=rg.CurveKnotStyle.Chord)
            offset_crvs.append(offset_crv)      
    return offset_crvs
