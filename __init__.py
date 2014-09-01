import bpy, mathutils
import os
from bpy_extras.io_utils import ExportHelper


bl_info = {
    "name": "Tetgen .smesh export", 
    "location":     "File > Import-Export",
    "description":  "Export custom data format",
    "category":     "Import-Export"
}

AXIS_MODES =  [
    ('xyz', 'xyz', 'no swapping'),
    ('xz-y', 'xz-y', 'ogre standard'),
    ('-xzy', '-xzy', 'non standard'),
]

def swap(vec):
    if CONFIG['SWAP_AXIS'] == 'xyz': return vec
    elif CONFIG['SWAP_AXIS'] == 'xzy':
        if len(vec) == 3: return mathutils.Vector( [vec.x, vec.z, vec.y] )
        elif len(vec) == 4: return mathutils.Quaternion( [ vec.w, vec.x, vec.z, vec.y] )
    elif CONFIG['SWAP_AXIS'] == '-xzy':
        if len(vec) == 3: return mathutils.Vector( [-vec.x, vec.z, vec.y] )
        elif len(vec) == 4: return mathutils.Quaternion( [ vec.w, -vec.x, vec.z, vec.y] )
    elif CONFIG['SWAP_AXIS'] == 'xz-y':
        if len(vec) == 3: return mathutils.Vector( [vec.x, vec.z, -vec.y] )
        elif len(vec) == 4: return mathutils.Quaternion( [ vec.w, vec.x, vec.z, -vec.y] )
    else:
        print( 'unknown swap axis mode', CONFIG['SWAP_AXIS'] )
        assert 0

## Config

last_export_filepath = ""

CONFIG_PATH = bpy.utils.user_resource('CONFIG', path='scripts', create=True)
CONFIG_FILENAME = 'export_tetgen_smesh.pickle'
CONFIG_FILEPATH = os.path.join(CONFIG_PATH, CONFIG_FILENAME)

_CONFIG_DEFAULTS_ALL = {
    'SWAP_AXIS' : 'xz-y', # ogre standard
}

CONFIG = {}

def load_config():
    global CONFIG

    if os.path.isfile( CONFIG_FILEPATH ):
        try:
            with open( CONFIG_FILEPATH, 'rb' ) as f:
                CONFIG = pickle.load( f )
        except:
            print('[ERROR]: Can not read config from %s' %CONFIG_FILEPATH)

    for tag in _CONFIG_DEFAULTS_ALL:
        if tag not in CONFIG:
            CONFIG[ tag ] = _CONFIG_DEFAULTS_ALL[ tag ]

    return CONFIG

CONFIG = load_config()
 

class ExportTetgenSmesh(bpy.types.Operator, ExportHelper):
    bl_idname = "export_tetgen.smesh"
    bl_label = "Tetgen .smesh exporter"
    bl_options = {'REGISTER'}

    EX_SWAP_AXIS = bpy.props.EnumProperty(
        items=AXIS_MODES,
        name='swap axis',
        description='axis swapping mode',
        default= CONFIG['SWAP_AXIS'])

    filename_ext = '.smesh'

    def write_file(self, filepath, mesh):
        def veckey3d(v):
            return round(v.x, 6), round(v.y, 6), round(v.z, 6)

        def veckey2d(v):
            return round(v[0], 6), round(v[1], 6)
     
        # prepare the mesh
        mesh.update(calc_tessface=True)

        # open file
        filepath = os.fsencode(filepath)
        filepathsmesh = filepath.decode("utf-8")
        smeshfile = open(filepathsmesh, "w", encoding="utf8", newline="\n")
        sfw = smeshfile.write

        # write vertices
        numVerts = len(mesh.vertices)
        sfw(str(numVerts) + " 3 0 0\n")
        cntVerts = 0
        for vert in mesh.vertices:
            x, y, z = veckey3d(swap(vert.co))
            # index is 1-based
            cntVerts += 1
            sfw(str(cntVerts) + " " + str(x) + " " + str(y) + " " + str(z) + "\n")
          
        # write number of faces, number of boundary markers
        sfw("%d %d\n" % (len(mesh.tessfaces), 0))
        # write faces
        for i in range(len(mesh.tessfaces)):
            sfw(str(len(mesh.tessfaces[i].vertices))+' ')
            for j in range(len(mesh.tessfaces[i].vertices)):
                vertex = (mesh.tessfaces[i].vertices[j])+1
                sfw(str(vertex)+' ')
            sfw("\n")

        # write number of holes, number of regions
        sfw("0\n")
        sfw("0\n")
        smeshfile.close()

    def invoke(self, context, event):
        # Resolve path from opened .blend if available. It's not if
        # blender normally was opened with "last open scene".
        # After export is done once, remember that path when re-exporting.
        global last_export_filepath
        if last_export_filepath == "":
            # First export during this blender run
            if self.filepath == "" and context.blend_data.filepath != "":
                path, name = os.path.split(context.blend_data.filepath)
                self.filepath = os.path.join(path, name.split('.')[0])
            if self.filepath == "":
                self.filepath = "tetgenSmeshExport"
            self.filepath += ".smesh"
        else:
            # Sequential export, use the previous path
            self.filepath = last_export_filepath

        # Update ui setting from the last export, or file config.
        self.update_ui()
        
        wm = context.window_manager
        fs = wm.fileselect_add(self) # writes to filepath
        return {'RUNNING_MODAL'}




    def execute(self, context):

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        # Store this path for later re-export
        global last_export_filepath
        last_export_filepath = self.filepath

        if (context.object):
            if (context.object.type == "MESH"):
                mesh = context.object.data
                self.write_file(self.filepath, mesh)

        return {'FINISHED'}


    def update_ui(self):
        self.EX_SWAP_AXIS = CONFIG['SWAP_AXIS']

def menu_func(self, context):
    self.layout.operator(ExportTetgenSmesh.bl_idname, text="Tetgen (.smesh)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()






