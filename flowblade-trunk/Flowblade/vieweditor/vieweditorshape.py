
import viewgeom

# Edit point display types
MOVE_HANDLE = 0
ROTATE_HANDLE = 1
CONTROL_POINT = 2
INVISIBLE_POINT = 3
TOP_LEFT_HANDLE = 4
BOTTOM_RIGHT_HANDLE = 5
        
EDIT_POINT_SIDE_HALF = 4

class EditPoint:
    """
    A point that user can move on the screen to edit image data.
    """
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.rotation = 0.0
        self.is_hittable = True
        self.start_x = x
        self.start_y = y        
        self.display_type = MOVE_HANDLE
    
    def set_pos(p):
        self.x, self.y = p
    
    def save_start_pos(self):
        self.start_x = self.x
        self.start_y = self.y

    def translate_from_move_start(self, delta):
        dx, dy = delta
        self.x = self.start_x + dx
        self.y = self.start_y + dy

    def hit(self, test_p, scale=1.0):
        if not self.is_hittable:
            return False
        
        test_x, test_y = test_p
        side_mult = 1.0 / scale        
        if((test_x >= self.x - EDIT_POINT_SIDE_HALF * side_mult) 
            and (test_x <= self.x + EDIT_POINT_SIDE_HALF  * side_mult) 
            and (test_y >= self.y - EDIT_POINT_SIDE_HALF * side_mult)
            and (test_y <= self.y + EDIT_POINT_SIDE_HALF * side_mult)):
            return True;

        return False;

    def draw(self, cr, view_editor):
        if self.display_type == INVISIBLE_POINT:
            return
        else:
            x, y = view_editor.movie_coord_to_panel_coord((self.x, self.y))
            cr.rectangle(x - 4, y - 4, 8, 8)
            cr.fill()


class EditPointShape:
    """
    A shape that user can move, rotate or scale on the screen to edit image data.
    """
    def __init__(self):
        self.edit_points = []

    def save_start_pos(self):
        for ep in self.edit_points:
            ep.save_start_pos()
            
    def translate_from_move_start(self, delta):
        for ep in self.edit_points:
            ep.translate_from_move_start(delta)

    def point_in_area(self, p):
        """
        Default hit test is to see if point is inside convex with points in order 0 - n.
        Override for different hit test.
        """
        points = self.editpoints_as_tuples_list()
        return viewgeom.point_in_convex_polygon(p, points, 0)

    def get_edit_point(self, p):
        for ep in self.edit_points:
            if ep.hit(p) == True:
                return ep
        return None

    def editpoints_as_tuples_list(self):
        points = []
        for ep in self.edit_points:
            points.append((ep.x, ep.y))
        return points

    def get_bounding_box(p):
        if len(self.edit_points) == 0:
            return None

        x_low = 1000000000
        x_high = -100000000
        y_low = 1000000000
        y_high = -100000000

        for p in self.edit_points:
            px, py = p
            if px < x_low:
                x_low = p.x
            if px > x_high:
                x_high = p.x;
            if py < y_low:
                y_low = p.y;
            if py > y_high:
                y_high = p.y;

        return (x_low, y_low, x_high - x_low, y_high - y_low)

    def draw_points(self, cr, view_editor):
        for ep in self.edit_points:
            ep.draw(cr, view_editor)
    
    def draw_line_shape(self, cr, view_editor, line_width):
        cr.set_line_width(line_width)
        x, y = view_editor.movie_coord_to_panel_coord((self.edit_points[0].x, self.edit_points[0].y))
        cr.move_to(x, y)
        for i in range(1, len(self.edit_points)):
            ep = self.edit_points[i]
            x, y = view_editor.movie_coord_to_panel_coord((ep.x, ep.y))
            cr.line_to(x, y)
        cr.close_path()
        cr.stroke()

    

class SimpleRectEditShape(EditPointShape):
    """
    A rect with two corner handles that can be moved scaled or rotated.
    """
    def __init__(self):
        EditPointShape.__init__(self)
        self.rect = (0,0,100,100) # we use this to create points, user should set real rect immediately with set_rect()
        self.rotation = 0.0

        x, y, w, h = self.rect
        self.edit_points.append(EditPoint(x, y))
        self.edit_points.append(EditPoint(x + w, y))
        self.edit_points.append(EditPoint(x + w, y + h))
        self.edit_points.append(EditPoint(x, y + h))
        self.edit_points[0].display_type = TOP_LEFT_HANDLE
        self.edit_points[2].display_type = BOTTOM_RIGHT_HANDLE
        self.edit_points[1].display_type = INVISIBLE_POINT
        self.edit_points[3].display_type = INVISIBLE_POINT
        self.edit_points[1].is_hittable = False
        self.edit_points[3].is_hittable = False

    def set_rect(self, rect):
        self.rect = rect
        self.reset_points(self)

    def reset_points(self):
        x, y, w, h = self.rect
        self.edit_points[0].x = x
        self.edit_points[0].y = y
        self.edit_points[1].x = x + w
        self.edit_points[1].y = y
        self.edit_points[2].x = x + w
        self.edit_points[2].y = y + h
        self.edit_points[3].x = x
        self.edit_points[3].y = y + h

