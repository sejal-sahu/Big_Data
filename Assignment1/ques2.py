import vtk

def create_opacity_transfer():
    opacity_transfer_function = vtk.vtkPiecewiseFunction()
    opacity_transfer_function.AddPoint(-4931.54, 1.0)
    opacity_transfer_function.AddPoint(101.815, 0.002)
    opacity_transfer_function.AddPoint(2594.97, 0.0)
    return opacity_transfer_function


def create_color_transfer():
    color_transfer_function = vtk.vtkColorTransferFunction()
    color_transfer_function.AddRGBPoint(-4931.54, 0, 1, 1)
    color_transfer_function.AddRGBPoint(-2508.95, 0, 0, 1)
    color_transfer_function.AddRGBPoint(-1873.9, 0, 0, 0.5)
    color_transfer_function.AddRGBPoint(-1027.16, 1, 0, 0)
    color_transfer_function.AddRGBPoint(-298.031, 1, 0.4, 0)
    color_transfer_function.AddRGBPoint(2594.97, 1, 1, 0)
    return color_transfer_function


def set_render(volume, outline_actor):
    # Renderer and Render Window
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.SetSize(1000, 1000)
    render_window.AddRenderer(renderer)

    # Interacto
    render_interactor = vtk.vtkRenderWindowInteractor()
    render_interactor.SetRenderWindow(render_window)

    # Add actors to the renderer
    renderer.AddActor(volume)
    renderer.AddActor(outline_actor)

    # Set up the renderer and render window
    renderer.SetBackground(1, 1, 1)
    render_window.Render()
    render_interactor.Start()

def set_vp_for_phong_shading():
    volume_property = vtk.vtkVolumeProperty()
    volume_property.ShadeOn()
    volume_property.SetAmbient(0.5)
    volume_property.SetDiffuse(0.5)
    volume_property.SetSpecular(0.5)


def main_f(use_phong_shading, input):
    # Load 3D data 
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(input)
    
    # Create Color and Opacity Transfer functions
    color_transfer_function = create_color_transfer()
    opacity_transfer_function = create_opacity_transfer()
    
    # Volume Rendering
    mapper = vtk.vtkSmartVolumeMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    # Volume Property
    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetColor(color_transfer_function)
    volume_property.SetScalarOpacity(opacity_transfer_function)

    # Phong Shading
    if use_phong_shading:
        volume_property.ShadeOn()
        volume_property.SetAmbient(0.5)
        volume_property.SetDiffuse(0.5)
        volume_property.SetSpecular(0.5)

    # Volume
    volume = vtk.vtkVolume()
    volume.SetMapper(mapper)
    volume.SetProperty(volume_property)

    # Outline
    outline = vtk.vtkOutlineFilter()
    outline.SetInputConnection(reader.GetOutputPort())

    outline_mapper = vtk.vtkPolyDataMapper()
    outline_mapper.SetInputConnection(outline.GetOutputPort())

    outline_actor = vtk.vtkActor()
    outline_actor.SetMapper(outline_mapper)

    set_render(volume, outline_actor)
    

if __name__ == "__main__":
    
    phong_shading = input("Do you want to use Phong shading? (yes/no): ").lower() == "yes"
    # replace 'Data/Isabel_3D.vti' with the actual file name
    input = 'Data/Isabel_3D.vti'
    # use_phong_shading = False
    main_f(phong_shading, input)

