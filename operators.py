import pathlib
import time

import bpy
from bpy_extras import object_utils
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
    CollectionProperty,
)

from . import operator_generator

template_path = pathlib.Path(__file__).parent / "primitivo_library.blend"

# may add asset library somehow?
# C.preferences.filepaths.asset_libraries[1].path

class PRIMITIVO_OT_GenerateOperators(bpy.types.Operator):
    bl_idname = 'primitivo.generate_operators'
    bl_label = "Primitivo Generate Operators"
    bl_options = {'REGISTER', 'UNDO' }

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):

        with bpy.data.libraries.load(str(template_path)) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects if name.startswith('Primitivo_')]
              
       
        target = template_path.parent / "operators_generated.py"
        operator_generator.run(data_to.objects, target)

        bpy.data.libraries.remove(bpy.data.libraries.get(template_path.name))

        for obj in data_to.objects:
            bpy.data.objects.remove(obj)

        bpy.ops.script.reload()

        return {'FINISHED'} 

# def PrimitivoPropertyEntry_Update(self, context):
#     modifier = bpy.context.active_object.modifiers[0]
     
#     if self.type == 'VALUE':
#         modifier[f"'{self.name}'"] = self.floatProp
#     elif self.type == 'INT':           
#         modifier[f"'{self.name}'"] = self.intProp            
#     elif self.type == 'BOOLEAN':
#         modifier[f"'{self.name}'"] = int(self.boolProp)
      
#     bpy.context.object.data.update()

# class PrimitivoPropertyEntry(bpy.types.PropertyGroup):
#     name: bpy.props.StringProperty()
#     type: bpy.props.StringProperty()
#     primitivo_type: bpy.props.StringProperty()
#     intProp: bpy.props.IntProperty(update=PrimitivoPropertyEntry_Update)
#     boolProp: bpy.props.BoolProperty(update=PrimitivoPropertyEntry_Update)
#     floatProp: bpy.props.FloatProperty(update=PrimitivoPropertyEntry_Update)

class PRIMITIVO_OP_Add:   

    def align_update_callback(self, _context):
        if self.align == 'WORLD':
            self.rotation.zero()

    align: EnumProperty(
        name="Align",
        items=(
            ('WORLD', "World", "Align the new object to the world"),
            ('VIEW', "View", "Align the new object to the view"),
            ('CURSOR', "3D Cursor", "Use the 3D cursor orientation for the new object"),
        ),
        default='WORLD',
        update=align_update_callback,
    )
    location: FloatVectorProperty(
        name="Location",
        subtype='TRANSLATION',
    )
    rotation: FloatVectorProperty(
        name="Rotation",
        subtype='EULER',
    )

    # settings: bpy.props.CollectionProperty(type=PrimitivoPropertyEntry)
    
    # @property
    # def modifier_properties(self):
    #     #return bpy.context.scene.Primitivo_Settings
    #     return self.settings
    
    @classmethod
    def poll(cls, context):
        return context.scene.library is None 

    def create_quad(self, mesh):       
        vertices = [(-1.0, -1.0, 0.0), (1.0, -1.0, 0.0), (-1.0, 1.0, 0.0), (1.0, 1.0, 0.0)]
        face = [(0, 1, 3, 2)]
        mesh.from_pydata(vertices, [], face)
        mesh.update(calc_edges=True)


    def add_primitive(self, context, type):
        ''' Searches for node_tree, if that fails appends it from library '''

        layer = context.view_layer               
        for ob in layer.objects:
            ob.select_set(False)

        obj = None        

        group = bpy.data.node_groups.get(self.primitivo_type)
        if not group or group.type != 'GEOMETRY':
            with bpy.data.libraries.load(str(template_path)) as (data_from, data_to):
                data_to.objects = [name for name in data_from.objects if name == self.primitivo_type]
            
            for lib_obj in data_to.objects:
                
                bpy.context.view_layer.active_layer_collection.collection.objects.link(lib_obj)
                bpy.context.view_layer.objects.active = lib_obj
                obj = lib_obj

            lib = bpy.data.libraries.get(str(template_path.name))
            if lib:
                bpy.data.libraries.remove(lib)
        else:            
            mesh = bpy.data.meshes.new(self.primitivo_type + "Shape")
            mesh.use_auto_smooth = True
            mesh.auto_smooth_angle = self.auto_smooth_angle
          
            self.create_quad(mesh)
            obj = bpy.data.objects.new(self.primitivo_type, mesh)
            bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)
            modifier = obj.modifiers.new(self.primitivo_type, "NODES")
            node_group = bpy.data.node_groups[self.primitivo_type]
            modifier.node_group  = node_group

        modifier = obj.modifiers[0]
        obj.select_set(True)    
        bpy.context.view_layer.objects.active = obj

        obj.matrix_world = object_utils.add_object_align_init(context, operator=self)
      
        # if len(self.modifier_properties) == 0 or self.modifier_properties[0].primitivo_type != self.primitivo_type:
        #     self.modifier_properties.clear()

        #     for input in modifier.node_group.inputs:
        #         item = self.modifier_properties.add()
        #         item.primitivo_type = self.primitivo_type    
        #         item.name = input.identifier
            
        #         if input.identifier == "Input_0": continue
                
        #         item.type = input.type

        #         value = modifier[input.identifier]
                
        #         if input.type == 'VALUE':
        #             item.floatProp = value                    
        #         elif input.type == 'INT':
        #             item.intProp = value
        #         elif input.type == 'BOOLEAN':
        #             item.boolProp = value


    def invoke(self, context, event):        
        return self.execute(context)        
        
    def execute(self, context):
        self.add_primitive(context, self.primitivo_type)
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        # if len(self.modifier_properties) > 0:
        #     modifier = context.active_object.modifiers[0]
        #     for index, input in enumerate(modifier.node_group.inputs):
        #         if input.identifier == "Input_0": continue
            
        #         item = self.modifier_properties[index]
                
        #         if input.type == 'VALUE':
        #             layout.prop(item, "floatProp", text=input.name)
        #         elif input.type == 'INT':
        #             layout.prop(item, "intProp", text=input.name)
        #         elif input.type == 'BOOLEAN':               
        #             layout.prop(item, "boolProp", text=input.name)
        
        layout.prop(self, "align")
        layout.prop(self, "location")
        layout.prop(self, "rotation")

classes = (
    # PrimitivoPropertyEntry,

    PRIMITIVO_OT_GenerateOperators,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # bpy.types.Scene.Primitivo_Settings = bpy.props.CollectionProperty(type=PrimitivoPropertyEntry)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # del bpy.types.Scene.Primitivo_Settings