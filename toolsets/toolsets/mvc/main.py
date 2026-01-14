"""
UI entry points for the Toolsets application.

Functions are called from Nuke menu commands. They create Qt views, bind
controllers and models, show windows, and keep references alive to prevent
garbage collection.
"""

from toolsets.mvc import controller, model, view
from toolsets import saver

VIEW = None
ADD_NEW_TOOLSET_VIEW = None
CONTROLLER = None
ADD_NEW_TOOLSET_CONTROLLER = None


def show():
    """
    Show the toolsets main GUI.
    Instantiates the main view, model, and controller.
    """
    global VIEW
    VIEW = view.View()
    VIEW.raise_()
    VIEW.show()
    model_ = model.Model()
    global CONTROLLER
    CONTROLLER = controller.Controller(VIEW, model_)



def show_add_new_toolset(saver_type):
    """
    Show the GUI to add a new toolset.

    Args:
        saver_type (str): The saver type to use for saving ("Nuke" or "Python").
    """
    saver_classes = {
        "Nuke": saver.ToolsetSaverNK,
        "Python": saver.ToolsetSaverPY
    }
    try:
        saver_class = saver_classes[saver_type]()
    except KeyError:
        raise KeyError(
            f"No such saver type implemented: {saver_type}. Choose from {list(saver_classes.keys())}"
        )
    global ADD_NEW_TOOLSET_VIEW
    ADD_NEW_TOOLSET_VIEW = view.AddNewToolsetView()
    ADD_NEW_TOOLSET_VIEW.raise_()
    ADD_NEW_TOOLSET_VIEW.show()
    model_ = model.AddNewToolsetModel(saver_class)
    global ADD_NEW_TOOLSET_CONTROLLER
    ADD_NEW_TOOLSET_CONTROLLER = controller.AddNewToolsetViewController(
        ADD_NEW_TOOLSET_VIEW,
        model_,
        saver_type
    )
