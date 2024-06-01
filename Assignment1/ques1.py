import vtk

def load_dataset(input_file):
    # Step 1: Load the dataset in VTKImageData format
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(input_file)
    reader.Update()
    
    return reader.GetOutput()



def generate_smooth_isocontour(image_data, isovalue):
    dimensions = image_data.GetDimensions()

    contour_polydata = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    lines = vtk.vtkCellArray()

    isocontour_segment = []

    def add_isocontour_segment(segment):
        line_id = lines.InsertNextCell(len(segment))
        for point_id in segment:
            lines.InsertCellPoint(point_id)

    def interpolate(p1, p2, t):
        return [p1[i] + t * (p2[i] - p1[i]) for i in range(2)]

    def smooth_isocontour_segment(segment):
        smoothed_segment = []
        for i in range(len(segment) - 1):
            p1 = image_data.GetPoint(segment[i])
            p2 = image_data.GetPoint(segment[i + 1])
            smoothed_segment.append(segment[i])
            #isocontour_point = p2
            #point_id = points.InsertNextPoint(isocontour_point[0], isocontour_point[1], 0)
            #smoothed_segment.append(point_id)

            #for t in [1]:  # Adjust the weights for smoother result
                #isocontour_point = interpolate(p1, p2, t)
                #point_id = points.InsertNextPoint(isocontour_point[0], isocontour_point[1], 0)
                #smoothed_segment.append(point_id)
                #isocontour_point = interpolate(p1, p2, t)
                #smoothed_segment.append(points.InsertNextPoint(isocontour_point[0], isocontour_point[1], 0))

            #smoothed_segment.append(segment[i + 1])
        return smoothed_segment

    for i in range(dimensions[0] - 1):
        for j in range(dimensions[1] - 1):
            v1 = image_data.GetPointData().GetScalars().GetValue(j * dimensions[0] + i)
            v2 = image_data.GetPointData().GetScalars().GetValue(j * dimensions[0] + (i + 1))
            v3 = image_data.GetPointData().GetScalars().GetValue((j + 1) * dimensions[0] + (i + 1))
            v4 = image_data.GetPointData().GetScalars().GetValue((j + 1) * dimensions[0] + i)

            crossings = ((v1 - isovalue) * (v2 - isovalue) < 0, (v2 - isovalue) * (v3 - isovalue) < 0,
                          (v3 - isovalue) * (v4 - isovalue) < 0, (v4 - isovalue) * (v1 - isovalue) < 0)

            for edge, (p1, p2) in enumerate([(0, 1), (1, 2), (2, 3), (3, 0)]):
                if crossings[edge]:
                    t = (isovalue - [v1, v2, v3, v4][p1]) / ([v1, v2, v3, v4][p2] - [v1, v2, v3, v4][p1])
                    point_id_1 = j * dimensions[0] + i
                    point_id_2 = j * dimensions[0] + (i + 1)
                    point_id_3 = (j + 1) * dimensions[0] + (i + 1)
                    point_id_4 = (j + 1) * dimensions[0] + i
                    x, y, _ = image_data.GetPoint(point_id_1) if edge in [0, 2] else image_data.GetPoint(point_id_4)
                    next_x, next_y, _ = image_data.GetPoint(point_id_2) if edge in [0, 2] else image_data.GetPoint(point_id_3)

                    isocontour_point = [x + t * (next_x - x), y + t * (next_y - y)]
                    point_id = points.InsertNextPoint(isocontour_point[0], isocontour_point[1], 0)
                    isocontour_segment.append(point_id)

            
            if len(isocontour_segment) == 2:
                # Smooth the isocontour segment
                smoothed_segment = smooth_isocontour_segment(isocontour_segment)
                add_isocontour_segment(smoothed_segment)

            isocontour_segment = []

    contour_polydata.SetPoints(points)
    contour_polydata.SetLines(lines)

    clean_filter = vtk.vtkCleanPolyData()
    clean_filter.SetInputData(contour_polydata)
    clean_filter.Update()

    return clean_filter.GetOutput()

    
def write_to_vtp(output_file, contour_polydata):
    # Step 3: Write the isocontour to disk as a VTKPolyData file (*.vtp)
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(output_file)
    writer.SetInputData(contour_polydata)
    writer.Write()

def visualize_dataset_and_isocontour(image_data, contour_polydata):
    # Create a renderer for visualization
    renderer = vtk.vtkRenderer()
    
    # Create a mapper for the dataset
    dataset_mapper = vtk.vtkDataSetMapper()
    dataset_mapper.SetInputData(image_data)
    dataset_actor = vtk.vtkActor()
    dataset_actor.SetMapper(dataset_mapper)
    
    # Create a mapper for the isocontour
    contour_mapper = vtk.vtkPolyDataMapper()
    contour_mapper.SetInputData(contour_polydata)
    contour_actor = vtk.vtkActor()
    contour_actor.SetMapper(contour_mapper)
    
    contour_actor.GetProperty().SetColor(0.0, 1.0, 0.0)
    contour_actor.GetProperty().SetPointSize(2)
    # Add actors to the renderer
    renderer.AddActor(dataset_actor)
    renderer.AddActor(contour_actor)
    
    # Create a render window and render window interactor
    render_window = vtk.vtkRenderWindow()
    render_window.SetWindowName("Dataset and Isocontour Visualization")
    render_window.SetSize(600, 600)
    
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)
    
    # Set up the camera
    renderer.ResetCamera()
    
    # Add renderer to the render window
    render_window.AddRenderer(renderer)
    
    # Start the rendering loop
    render_window.Render()
    render_window_interactor.Start()

if __name__ == "__main__":
    # replace 'Data\Isabel_2D.vti' with the actual file name
    input_file = 'Data\Isabel_2D.vti'
    output_file = 'output_file_1.vtp'
    # Change the isovalue variable to desired value
    isovalue = float(input("Enter desired isovalue: "))
    # isovalue = 100

    # Load the dataset
    image_data = load_dataset(input_file)

    # Generate the isocontour
    contour_polydata = generate_smooth_isocontour(image_data, isovalue)

    # Write it out to disk as a VTKPolyData file
    write_to_vtp(output_file, contour_polydata)

    # Visualize the dataset and isocontour
    visualize_dataset_and_isocontour(image_data, contour_polydata)