"""Collection of utility functions commonly used"""

import maya.cmds as cmds
import maya.api.OpenMaya as om


def getMDagPath(node):
    selList = om.MSelectionList()
    selList.add(node)
    return selList.getDagPath(0)

def getMObject(node):
    selList = om.MSelectionList()
    selList.add(node)
    return selList.getDependNode(0)

def getWorldTranslation(node):
    """Returns given nodes world translation of rotate pivot"""
    targetMTransform = om.MFnTransform(getMDagPath(node))
    targetRotatePivot = om.MVector(targetMTransform.rotatePivot(om.MSpace.kWorld))
    return targetRotatePivot

def getDistance(node1, node2):
    """Returns the distance between two nodes"""
    Ax, Ay, Az = getWorldTranslation(node1)
    Bx, By, Bz = getWorldTranslation(node2)
    return ((Ax-Bx)**2 + (Ay-By)**2 + (Az-Bz)**2)**0.5


def alignTo(node, target, translation=True, rotation=True):
    """
    This is the fastest align method. May not work in all cases
    http://www.rihamtoulan.com/blog/2017/12/21/matching-transformation-in-maya-and-mfntransform-pitfalls
    """
    nodeMTransform = om.MFnTransform(getMDagPath(node))
    targetMTransform = om.MFnTransform(getMDagPath(target))
    if translation:
        targetRotatePivot = om.MVector(targetMTransform.rotatePivot(om.MSpace.kWorld))
        nodeMTransform.setTranslation(targetRotatePivot, om.MSpace.kWorld)
    if rotation:
        targetMTMatrix = om.MTransformationMatrix(om.MMatrix(cmds.xform(target, matrix=True, ws=1, q=True)))
        # using the target matrix decomposition
        # Worked on all cases tested
        nodeMTransform.setRotation(targetMTMatrix.rotation(True), om.MSpace.kWorld)

        # Using the MFnTransform quaternion rotation in world space
        # Doesn't work when there is a -1 scale on the object itself
        # Doesn't work when the object has frozen transformations and there is a -1 scale on a parent group.
        # followerMTransform.setRotation(MFntMainNode.rotation(OpenMaya.MSpace.kWorld, asQuaternion=True),OpenMaya.MSpace.kWorld)

def alignToAlter(node, target, position=True, rotation=False, o=(0,0,0)):
    """Old School Method"""
    if position:
        cmds.delete(cmds.pointConstraint(target, node, mo=False))
    if rotation:
        cmds.delete(tempOri = cmds.orientConstraint(target, node, o=o, mo=False))

def uniqueName(name):
    """Makes sure there is no other object with the same name. Returns the new unique name"""
    baseName = name
    idcounter = 0
    while cmds.objExists(name):
        name = "%s%s" % (baseName, str(idcounter + 1))
        idcounter = idcounter + 1
    return name

def createUpGrp(node, suffix, mi=True):
    """
    Creates an Upper Group for the given object.
    Args:
        node: (Pymel Object) Source Object
        suffix: (String) Suffix for the group. String.
        mi: (Boolean) Stands for "makeIdentity" If True, freezes the transformations of the new group. Default is True

    Returns: The created group node

    """
    grpName = "%s_%s" % (node, suffix)
    newGrp = cmds.group(em=True, name=grpName)

    #align the new created empty group to the selected object

    alignTo(newGrp, node, translation=True, rotation=True)

    #check if the target object has a parent
    originalParent = cmds.listRelatives(node, p=True)
    if originalParent:
        cmds.parent(newGrp, originalParent[0], r=False)
        if mi:
            cmds.makeIdentity(newGrp, a=True)

    cmds.parent(node,newGrp)
    return newGrp
