import bpy
import os
from bpy_extras.io_utils import ExportHelper


bl_info = {
    "name": "Tetgen .smesh export", 
    "location":     "File > Import-Export",
    "description":  "Export custom data format",
    "category":     "Import-Export"
}

class ExportTetgenSmesh(bpy.types.Operator, ExportHelper):
    bl_idname = "export_tetgen.smesh"
    bl_label = "Tetgen .smesh exporter"
    bl_options = {'PRESET'}

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
            x, y, z = veckey3d(vert.co)
            sfw(str(cntVerts) + " " + str(x) + " " + str(y) + " " + str(z) + "\n")
            cntVerts += 1
          
        # write number of faces, number of boundary markers
        sfw("%d %d\n" % (len(mesh.tessfaces), 0))
        # write faces
        for i in range(len(mesh.tessfaces)):
            sfw(str(len(mesh.tessfaces[i].vertices))+' ')
            for j in range(len(mesh.tessfaces[i].vertices)):
                vertex = ((mesh.tessfaces[i].vertices[j]) +1)
                sfw(str(vertex)+' ')
            sfw("\n")

        # write number of holes, number of regions
        sfw("0\n")
        sfw("0\n")
        smeshfile.close()


    def execute(self, context):

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        if (context.object):
            if (context.object.type == "MESH"):
                mesh = context.object.data
                self.write_file(self.filepath, mesh)

        return {'FINISHED'}


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






