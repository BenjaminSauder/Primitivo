
bl_info = {
    "name": "Primitivo",
    "category": "Object",
    "author": "Benjamin Sauder",
    "description": "Add geometry nodes primitves",
    "blender": (3, 5, 0),
    "version": (0, 1)
}

import bpy

from . import ui
from . import operators
from . import operators_generated

import importlib
if 'bpy' in locals():
    importlib.reload(ui)
    importlib.reload(operators)
    importlib.reload(operators_generated)


classes = (
    operators,
    operators_generated,
    ui,
)

def register():
    for cls in classes:
       cls.register()

def unregister():   
    for cls in reversed(classes):
        cls.unregister()

if __name__ == "__main__":
    register()
