import bpy

from bpy.types import (
    Panel,
    Menu,
)

from . import operators_generated


class VIEW3D_MT_Primitivo_add(Menu):    
    bl_label = "Primitivo"
    bl_idname = "VIEW3D_MT_primitivo_add"

    def draw(self, context):
        layout = self.layout
        
        for op in sorted(operators_generated.classes, key=lambda x: x.bl_label ):
            layout.operator(op.bl_idname)

def add_menu_draw(self, context):
    self.layout.menu(VIEW3D_MT_Primitivo_add.bl_idname, icon='MOD_MESHDEFORM')


classes = (
    VIEW3D_MT_Primitivo_add,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_add.prepend(add_menu_draw)

def unregister():   
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_add.remove(add_menu_draw)
