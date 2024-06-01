import vtk
    
        
def RK4_integration(starting_point, step_size, max_steps, probe_filter):
    """
    Function to perform RK4 integration to trace a streamline from a given seed point.
    """

    streamline_points = [starting_point]
    current_point = starting_point
    

    for _ in range(max_steps):
        # Performing the RK4 integration steps
        probe_filter.Update()
        output = probe_filter.GetOutput()
        vector_data = output.GetPointData().GetVectors()

        if vector_data is not None:
            current_index = output.FindPoint(current_point)
            
            if current_index != -1:
                # Using RK4 integration formulas
                a = [2 * step_size * value for value in vector_data.GetTuple(current_index)]
                current_index = output.FindPoint([current_point[i] + a[i]/2 for i in range(3)])
                b = [2 * step_size * value for value in vector_data.GetTuple(current_index)]
                current_index = output.FindPoint([current_point[i] + b[i]/2 for i in range(3)])
                c = [2 * step_size * value for value in vector_data.GetTuple(current_index)]
                current_index = output.FindPoint([current_point[i] + c[i]/2 for i in range(3)])
                d = [2 * step_size * value for value in vector_data.GetTuple(current_index)]

                next_point = make_next_point(current_point, a, b, c, d)
                
                
                # Check if the next point is within bounds
                bounds = output.GetBounds()
                if (bounds[0] <= next_point[0] <= bounds[1] and 
                    bounds[2] <= next_point[1] <= bounds[3] and 
                    bounds[4] <= next_point[2] <= bounds[5]):
                    streamline_points.append(next_point)
                    current_point = next_point
                else:
                    break
            else:
                break
        else:
            break

    return streamline_points

def make_next_point(current_point, a, b, c, d):
    next_point = [current_point[i] + (a[i] + 2*b[i] + 2*c[i] + d[i]) / 6 for i in range(3)]
    return next_point

def display_vtp_file(filename):
    # Read the VTKPolyData file
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()

    # Create a mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(reader.GetOutput())

    # Create an actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0, 100, 0)  # Set color to dark green

    # Create a renderer
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(1, 1, 1)  # Set background color to white

    # Create a render window
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # Create a render window interactor
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    # Start the rendering loop
    render_window.Render()
    render_window_interactor.Start()


def main():
    
    # Setting the integration parameters
    step_size = 0.05
    max_steps = 1000
    
    # Loading the vector field dataset
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName("tornado3d_vector.vti")
    reader.Update()

    # Creating a probe filter
    probe_filter = vtk.vtkProbeFilter()
    probe_filter.SetInputConnection(reader.GetOutputPort())

    # Getting the user input for seed location
    seed_3D_location = list(map(float, input("Enter the 3D seed location (x y z): ").split()))



    # Tracing the streamline forwards
    probe_filter.SetSourceConnection(reader.GetOutputPort())
    forward_streamline = RK4_integration(seed_3D_location, step_size, max_steps, probe_filter)

    # Tracing the streamline backwards
    probe_filter.SetSourceConnection(reader.GetOutputPort())
    backward_streamline = RK4_integration(seed_3D_location, -step_size, max_steps, probe_filter)[::-1]

    # Combine forward and backward streamlines into a single streamline
    streamline_points = backward_streamline + forward_streamline[1:]

    # Create a vtkPolyData to store the streamline
    poly_data = vtk.vtkPolyData()
    lines = vtk.vtkCellArray()

    # Convert streamline points to VTK points
    vtk_points = vtk.vtkPoints()
    for point in streamline_points:
        vtk_points.InsertNextPoint(point)

    # Connect points into lines
    line_ids = list(range(len(streamline_points)))
    line_ids.pop(0)  # Remove the first point
    for i, j in zip(line_ids[:-1], line_ids[1:]):
        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, i - 1)
        line.GetPointIds().SetId(1, j)
        lines.InsertNextCell(line)

    poly_data.SetPoints(vtk_points)
    poly_data.SetLines(lines)

    # Writing the streamline to a VTKPolyData file
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName("streamline_output.vtp")
    writer.SetInputData(poly_data)
    writer.Write()

    # Displaying the VTKPolyData file Output
    display_vtp_file("streamline_output.vtp")

if __name__ == "__main__":
    main()
