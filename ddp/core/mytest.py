#-----------------------------------------------------------------------------
# Some sample code for slvs.dll. We draw some geometric entities, provide
# initial guesses for their positions, and then constrain them. The solver
# calculates their new positions, in order to satisfy the constraints.
#
# Copyright 2008-2013 Jonathan Westhues.
# Ported to Python by Benjamin Koch
#-----------------------------------------------------------------------------

#from slvs import System, Param
from slvs import *
import unittest

verbose = False

def printf(fmt, *args):
    print fmt % args

class H(object):
    __slots__ = "handle"

    def __init__(self, h):
        self.handle = h

class TestSlvs(unittest.TestCase):
    def floatEqual(self, a, b):
        return abs(a-b) < 0.001
    
    def assertFloatEqual(self, a, b):
        if not isinstance(a, (int, long, float)) \
                or not isinstance(b, (int, long, float)):
            self.assertTrue(False, "not a float")
        if self.floatEqual(a, b):
            self.assertTrue(True)
        else:
            self.assertEqual(a, b)
    
    def assertFloatListEqual(self, xs, ys):
        if len(xs) != len(ys):
            self.assertListEqual(xs, ys)
        else:
            for i,a,b in zip(range(len(xs)), xs, ys):
                aL = isinstance(a, (list, tuple))
                bL = isinstance(b, (list, tuple))
                if aL and bL:
                    self.assertFloatListEqual(a, b)
                elif not self.floatEqual(a, b):
                    self.assertEqual(a, b, "in list at index %d" % i)
            self.assertTrue(True)
    
    def test_param(self):
        sys = System()
        
        p1 = Param(17.3)
        self.assertFloatEqual(p1.value, 17.3)
        
        p2 = Param(1.0)
        p3 = Param(0.0)
        e = sys.add_point3d(p1, p2, p3)
        
        self.assertFloatEqual(p1.value, 17.3)
        self.assertFloatEqual(p2.value,  1.0)
        self.assertFloatEqual(p3.value,  0.0)
        
        p1 = e.x()
        p2 = e.y()
        p3 = e.z()
        
        self.assertFloatEqual(p1.value, 17.3)
        self.assertFloatEqual(p2.value,  1.0)
        self.assertFloatEqual(p3.value,  0.0)
        
        self.assertEqual(p1.handle, 1)
        self.assertEqual(p2.handle, 2)
        self.assertEqual(p3.handle, 3)
        
        
        p4 = sys.add_param(42.7)
        self.assertFloatEqual(p4.value, 42.7)
    
    #-----------------------------------------------------------------------------
    # An example of a constraint in 3d. We create a single group, with some
    # entities and constraints.
    #-----------------------------------------------------------------------------
    def test_example3d(self):
        sys = System()
        
        # This will contain a single group, which will arbitrarily number 1.
        g = 1;
        
        # A point, initially at (x y z) = (10 10 10)
        a = sys.add_param(10.0)
        b = sys.add_param(10.0)
        c = sys.add_param(10.0)
        p1 = Point3d(a, b, c)
        # and a second point at (20 20 20)
        p2 = Point3d(Param(20.0), Param(20.0), Param(20.0), sys)
        # and a line segment connecting them.
        LineSegment3d(p1, p2)
        
        # The distance between the points should be 30.0 units.
        Constraint.distance(30.0, p1, p2)
        
        # Let's tell the solver to keep the second point as close to constant
        # as possible, instead moving the first point.
        sys.set_dragged(p2)
        
        # Now that we have written our system, we solve.
        Slvs_Solve(sys, g);
        
        if (sys.result == SLVS_RESULT_OKAY):
            if verbose:
                print ("okay; now at (%.3f %.3f %.3f)\n" +
                       "             (%.3f %.3f %.3f)") % (
                          sys.get_param(0).val, sys.get_param(1).val, sys.get_param(2).val,
                          sys.get_param(3).val, sys.get_param(4).val, sys.get_param(5).val)
                print "%d DOF" % sys.dof
            
            self.assertFloatEqual(sys.get_param(0).val,  2.698)
            self.assertFloatEqual(sys.get_param(1).val,  2.698)
            self.assertFloatEqual(sys.get_param(2).val,  2.698)
            self.assertFloatEqual(sys.get_param(3).val, 20.018)
            self.assertFloatEqual(sys.get_param(4).val, 20.018)
            self.assertFloatEqual(sys.get_param(5).val, 20.018)
            self.assertEqual(sys.dof, 5)
        else:
            self.assertTrue(False, "solve failed")
    
    #-----------------------------------------------------------------------------
    # An example of a constraint in 2d. In our first group, we create a workplane
    # along the reference frame's xy plane. In a second group, we create some
    # entities in that group and dimension them.
    #-----------------------------------------------------------------------------
    def test_example2d(self):
        sys = System()
        
        g = 1;
        # First, we create our workplane. Its origin corresponds to the origin
        # of our base frame (x y z) = (0 0 0)
        p1 = Point3d(Param(0.0), Param(0.0), Param(0.0), sys)
        # and it is parallel to the xy plane, so it has basis vectors (1 0 0)
        # and (0 1 0).
        #Slvs_MakeQuaternion(1, 0, 0,
        #                    0, 1, 0, &qw, &qx, &qy, &qz);
        qw, qx, qy, qz = Slvs_MakeQuaternion(1, 0, 0,
                                             0, 1, 0)
        wnormal = Normal3d(Param(qw), Param(qx), Param(qy), Param(qz), sys)
        
        wplane = Workplane(p1, wnormal)
        
        # Now create a second group. We'll solve group 2, while leaving group 1
        # constant; so the workplane that we've created will be locked down,
        # and the solver can't move it.
        g = 2
        sys.default_group = 2
        # These points are represented by their coordinates (u v) within the
        # workplane, so they need only two parameters each.
        p11 = sys.add_param(10.0)
        p301 = Point2d(wplane, p11, Param(20))
        self.assertEqual(p11.group, 2)
        self.assertEqual(p301.group, 2)
        self.assertEqual(p301.u().group, 2)
        self.assertEqual(p301.v().group, 2)
        
        p302 = Point2d(wplane, Param(20), Param(10))
        
        # And we create a line segment with those endpoints.
        line = LineSegment2d(wplane, p301, p302)
        
        
        # Now three more points.
        p303 = Point2d(wplane, Param(100), Param(120))
        
        p304 = Point2d(wplane, Param(120), Param(110))
        
        p305 = Point2d(wplane, Param(115), Param(115))
        
        # And arc, centered at point 303, starting at point 304, ending at
        # point 305.
        p401 = ArcOfCircle(wplane, wnormal, p303, p304, p305);
        
        # Now one more point, and a distance
        p306 = Point2d(wplane, Param(200), Param(200))
        
        p307 = Distance(wplane, Param(30.0))
        
        # And a complete circle, centered at point 306 with radius equal to
        # distance 307. The normal is 102, the same as our workplane.
        p402 = Circle(wplane, wnormal, p306, p307);
        
        
        # The length of our line segment is 30.0 units.
        Constraint.distance(30.0, wplane, p301, p302)
        
        # And the distance from our line segment to the origin is 10.0 units.
        Constraint.distance(10.0, wplane, p1, line)
        
        # And the line segment is vertical.
        Constraint.vertical(wplane, line)
        # And the distance from one endpoint to the origin is 15.0 units.
        Constraint.distance(15.0, wplane, p301, p1)
        
        if False:
            # And same for the other endpoint; so if you add this constraint then
            # the sketch is overconstrained and will signal an error.
            Constraint.distance(18.0, wplane, p302, p1)
        
        # The arc and the circle have equal radius.
        Constraint.equal_radius(wplane, p401, p402)
        # The arc has radius 17.0 units.
        Constraint.diameter(17.0*2, wplane, p401)
        
        # If the solver fails, then ask it to report which constraints caused
        # the problem.
        sys.calculateFaileds = 1;
        
        # And solve.
        result = sys.solve()
        
        if(result == SLVS_RESULT_OKAY):
            if verbose:
                printf("solved okay");
                printf("line from (%.3f %.3f) to (%.3f %.3f)",
                       sys.get_param(7).val, sys.get_param(8).val,
                       sys.get_param(9).val, sys.get_param(10).val);
            self.assertFloatEqual(sys.get_param( 7).val,  10.000)
            self.assertFloatEqual(sys.get_param( 8).val,  11.180)
            self.assertFloatEqual(sys.get_param( 9).val,  10.000)
            self.assertFloatEqual(sys.get_param(10).val, -18.820)
            
            if verbose:
                printf("arc center (%.3f %.3f) start (%.3f %.3f) finish (%.3f %.3f)",
                       sys.get_param(11).val, sys.get_param(12).val,
                       sys.get_param(13).val, sys.get_param(14).val,
                       sys.get_param(15).val, sys.get_param(16).val);
            self.assertFloatListEqual(
                map(lambda i: sys.get_param(i).val, range(11, 17)),
                [101.114, 119.042, 116.477, 111.762, 117.409, 114.197])
            
            if verbose:
                printf("circle center (%.3f %.3f) radius %.3f",
                       sys.get_param(17).val, sys.get_param(18).val,
                       sys.get_param(19).val);
                printf("%d DOF", sys.dof);
            self.assertFloatEqual(sys.get_param(17).val, 200.000)
            self.assertFloatEqual(sys.get_param(18).val, 200.000)
            self.assertFloatEqual(sys.get_param(19).val,  17.000)
            
            self.assertEqual(sys.dof, 6)
        else:
            if verbose:
                printf("solve failed: problematic constraints are:");
                for i in range(sys.faileds):
                    printf(" %lu", sys.failed[i]);
                printf("");
                if (sys.result == SLVS_RESULT_INCONSISTENT):
                    printf("system inconsistent");
                else:
                    printf("system nonconvergent");
            self.assertTrue(False, "solve failed")
    
    def test_to_openscad(self):
        sys = System()
        
        # We want to find the plane for three points. The points
        # shouldn't change, so we put them into another group.
        
        p1 = Point3d(1, 1, 9, sys)
        p2 = Point3d(5, 2, 2, sys)
        p3 = Point3d(0, 7, 5, sys)
        
        # Other entities go into another group
        sys.default_group = 2
        
        wrkpl = Workplane(p1, Normal3d(Param(1), Param(0), Param(0), Param(0), sys))
        
        # Some constraints: all points are in the plane
        # (p1 is its origin, so we don't need a constraint)
        Constraint.on(wrkpl, p2)
        Constraint.on(wrkpl, p3)
        
        # Solve it (group 2 is still active)
        sys.solve()
        
        self.assertEqual(sys.result, SLVS_RESULT_OKAY)
        self.assertFloatListEqual(wrkpl.origin().to_openscad(),
                                  [ 1.000, 1.000, 9.000 ])
        self.assertFloatListEqual(wrkpl.normal().vector(),
                                  [ 0.863, -0.261, 0.432, -0.000 ])
        self.assertFloatListEqual(wrkpl.to_openscad(),
                                  [[0.6270915888275256, -0.22570772255200192, 0.7455281102701327, 1.0], [-0.22570772255200203, 0.8633874310873447, 0.45124069832139596, 1.0], [-0.7455281102701327, -0.45124069832139607, 0.49047901991447185, 9.0], [0, 0, 0, 1]])
    
    def test_example(self):
        sys = System(20)
        
        p1 = Point3d(Param(10.0), Param(10.0), Param(10.0), sys)
        p2 = Point3d(Param(20.0), Param(20.0), Param(20.0), sys)
        LineSegment3d(p1, p2)
        Constraint.distance(30.0, p1, p2)
        
        # Let's tell the solver to keep the second point as close to constant
        # as possible, instead moving the first point.
        sys.set_dragged(p2)
        
        sys.solve()
        
        if (sys.result == SLVS_RESULT_OKAY):
            print ("okay; now at (%.3f %.3f %.3f)\n" +
                   "             (%.3f %.3f %.3f)") % (
                      sys.get_param(0).val, sys.get_param(1).val, sys.get_param(2).val,
                      sys.get_param(3).val, sys.get_param(4).val, sys.get_param(5).val)
            print "%d DOF" % sys.dof
        else:
            print "solve failed"
    
    
    @staticmethod
    def set_up_2d_workplane():
        sys = System()
        # First, we create our workplane. Its origin corresponds to the origin
        # of our base frame (x y z) = (0 0 0)
        p1 = Point3d(Param(0.0), Param(0.0), Param(0.0), sys)
        # and it is parallel to the xy plane, so it has basis vectors (1 0 0)
        # and (0 1 0).
        #Slvs_MakeQuaternion(1, 0, 0,
        #                    0, 1, 0, &qw, &qx, &qy, &qz);
        qw, qx, qy, qz = Slvs_MakeQuaternion(1, 0, 0,
                                             0, 1, 0)
        wnormal = Normal3d(Param(qw), Param(qx), Param(qy), Param(qz), sys)
        wplane = Workplane(p1, wnormal)
        # Now create a second group. We'll solve group 2, while leaving group 1
        # constant; so the workplane that we've created will be locked down,
        # and the solver can't move it.
        sys.default_group = 2
        return sys, wplane, wnormal
    
    def test_my1(self):
        sys, workplane, wnormal = self.set_up_2d_workplane()
        
        pA = Point2d(workplane, Param(10), Param(10))
        pB = Point2d(workplane, Param(12), Param(30))
        line = LineSegment2d(workplane, pA, pB)
        
        # constrain to be immobile
        sys.set_dragged(pA)
        Constraint.distance(30.0, workplane, pA, pB)
        Constraint.horizontal(workplane, line)
        # Constraint.vertical()
        
        p306 = Point2d(workplane, Param(200), Param(200))
        p307 = Distance(workplane, Param(30.0))
        # This entity is specified by its center point, by its diameter, and by its normal.
        circle = Circle(workplane, wnormal, p306, p307)
        
        p303 = Point2d(workplane, Param(100), Param(120))
        p304 = Point2d(workplane, Param(120), Param(110))
        p305 = Point2d(workplane, Param(115), Param(115))
        
        #  This entity is specified by its center point, the two endpoints, and its normal. 
        arc = ArcOfCircle(workplane, wnormal, p303, p304, p305)
        Constraint.diameter(17.0*2, workplane, arc)
        Constraint.equal_radius(workplane, arc, circle)
        # TODO point-coincident constraint ...
        # TODO Equal Length / Radius / Angle
        
        
        result = sys.solve()
        
        if sys.result == SLVS_RESULT_OKAY:
            self.print_all_params(sys)
            
            print pA.to_openscad()
            print pB.to_openscad()
            
            print circle.__dict__
        else:
            print "solve failed"
    
    
    def print_all_params(self, sys):
        paramNo = 0
        while sys.get_param(paramNo) is not None:
            print paramNo, ":\t", sys.get_param(paramNo).val
            paramNo += 1
    
    
    def test_my2(self):
        sys, workplane, wnormal = self.set_up_2d_workplane()
        
        pA = Point2d(workplane, Param(10), Param(10))
        pB = Point2d(workplane, Param(12), Param(30))
        # this line is going to be constrained to represent the radius of the circle
        line = LineSegment2d(workplane, pA, pB)
        
        pC = Point2d(workplane, Param(15), Param(15))
        distance = Distance(workplane, Param(5.0))
        circle = Circle(workplane, wnormal, pC, distance)
        
        Constraint.coincident(workplane, pB, pC)
        Constraint.on(workplane, pA, circle)
        Constraint.vertical(workplane, line)
        
        # https://github.com/whitequark/solvespace/blob/for-upstream/src/constraint.cpp
        # TODO Equal Length / Radius / Angle
        # 
        # Constraint::some_other_constraint(System *,int,Workplane,double,Point,Point,Entity,Entity,Slvs_hGroup)
        # Constraint.some_other_constraint()
        
        
        result = sys.solve()
        if sys.result == SLVS_RESULT_OKAY:
            self.print_all_params(sys)
            print pA.to_openscad()
            print pB.to_openscad()
            print pC.to_openscad()
        else:
            print "solve failed"
    
    
    def convert_graph_into_system(self, g):
        import networkx as nx
        sys, workplane, wnormal = self.set_up_2d_workplane()
        points = []
        for node in g.nodes():
            newPoint = Point2d(workplane, Param(node[0]), Param(node[1]))
            g.node[node]["solve"] = newPoint
            points.append(newPoint)
        
        
        for edge in g.edges():
            pA = g.node[edge[0]]["solve"]
            pB = g.node[edge[1]]["solve"]
            line = LineSegment2d(workplane, pA, pB)
            data = g.get_edge_data(*edge)
            data["solve"] = line
            if "constrain" in data:
                if data["constrain"] == "horizontal":
                    Constraint.horizontal(workplane, line)
                if data["constrain"] == "vertical":
                    Constraint.vertical(workplane, line)
            if "distance" in data:
                Constraint.distance(data["distance"], workplane, pA, pB)
            
        result = sys.solve()
        self.print_slvs_result(sys)
        
        for node in g.nodes():
            point = g.node[node]["solve"]
            pArr = point.to_openscad()
            nx.relabel_nodes(g, {node: (pArr[0], pArr[1])}, copy=False)
        
        return g


    def print_slvs_result(self, sys):
        if sys.result == SLVS_RESULT_OKAY:
            print "OKAY"
        if sys.result == SLVS_RESULT_DIDNT_CONVERGE:
            print "DIDNT_CONVERGE"
        if sys.result == SLVS_RESULT_INCONSISTENT:
            print "INCONSISTENT"
        if sys.result == SLVS_RESULT_TOO_MANY_UNKNOWNS:
            print "TOO_MANY_UNKNOWNS"
        
        if sys.result != SLVS_RESULT_OKAY:
            for i in range(sys.faileds):
                printf(" %lu", sys.failed[i])
    
    
    def test_my3(self):
        import networkx as nx
        g = nx.Graph()
        g.add_node((1,1))
        g.add_node((2,2))
        g.add_edge((1,1), (2,2), {"constrain": "horizontal"})
        g.add_node((3,1))
        g.add_edge((2,2), (3,1), {"constrain": "vertical"})
        
        g = self.convert_graph_into_system(g)
        print "nodes", g.nodes()
        print "edges", g.edges()
        
        
    def test_my_square(self):
        import networkx as nx
        g = nx.Graph()
        # counterclockwise
        n1 = (1.2, 1)
        n2 = (1, 2)
        n3 = (2, 2.2)
        n4 = (2, 1)
        
        # g.add_edge(n1, n2, {"constrain": "vertical"})
        # g.add_edge(n2, n3, {"constrain": "horizontal"})
        # g.add_edge(n3, n4, {"constrain": "vertical", "distance": 1})
        # g.add_edge(n4, n1, {"constrain": "horizontal", "distance": 1})
        
        g.add_edge(n1, n2, {"distance": 1})
        g.add_edge(n2, n3, {"distance": 1})
        g.add_edge(n3, n4, {"constrain": "vertical", "distance": 1})
        g.add_edge(n4, n1, {"constrain": "horizontal", "distance": 1})
        
        print "my square"
        g = self.convert_graph_into_system(g)
        print "nodes", g.nodes()
        print "edges", g.edges()
        
        


if __name__ == '__main__':
    unittest.main()
