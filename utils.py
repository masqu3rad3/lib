"""Collection of utility functions commonly used"""

import maya.cmds as cmds
import maya.OpenMaya as om
# import maya.api.OpenMaya as om2


def getMDagPath(node):
    selList = om.MSelectionList()
    selList.add(node)
    dagPath = om.MDagPath()
    selList.getDagPath(0, dagPath)
    return dagPath

# def getMDagPath2(node):
#     "API 2.0"
#     selList = om2.MSelectionList()
#     selList.add(node)
#     return selList.getDagPath(0)

def getMObject(node):
    selList = om.MSelectionList()
    selList.add(node)
    mObject = om.MObject()
    selList.getDependNode(0, mObject)
    return mObject

# def getMObject2(node):
#     "API 2.0"
#     selList = om2.MSelectionList()
#     selList.add(node)
#     return selList.getDependNode(0)

def getWorldTranslation(node):
    """Returns given nodes world translation of rotate pivot"""
    targetMTransform = om.MFnTransform(getMDagPath(node))
    targetRotatePivot = om.MVector(targetMTransform.rotatePivot(om.MSpace.kWorld))
    return targetRotatePivot

# def getWorldTranslation2(node):
#     """(API 2.0) Returns given nodes world translation of rotate pivot"""
#     targetMTransform = om2.MFnTransform(getMDagPath2(node))
#     targetRotatePivot = om2.MVector(targetMTransform.rotatePivot(om2.MSpace.kWorld))
#     return targetRotatePivot

def getDistance(node1, node2):
    """Returns the distance between two nodes"""
    Ax, Ay, Az = getWorldTranslation(node1)
    Bx, By, Bz = getWorldTranslation(node2)
    return ((Ax-Bx)**2 + (Ay-By)**2 + (Az-Bz)**2)**0.5

# def getAllVerts(node):
#     """
#     Using Maya Python API 1.0
#     """
#
#     # 1 # initialize a selectionList holder
#     selectionLs = om.MSelectionList()
#
#     # 2 # get the selected object in the viewport and put it in the selection list
#     # om.MGlobal.getActiveSelectionList(selectionLs)
#
#     # add the node to the selectionList
#     selectionLs.add(node)
#
#     # 3 # initialize a dagpath object
#     dagPath = om.MDagPath()
#
#     # 4 # populate the dag path object with the first object in the selection list
#     selectionLs.getDagPath(0, dagPath)
#
#     # ___________Query vertex position ___________
#
#     # initialize a Point array holder
#     vertPoints = om.MPointArray()
#
#     # create a Mesh functionset from our dag object
#     mfnObject = om.MFnMesh(dagPath)
#
#     # call the function "getPoints" and feed the data into our pointArray
#     mfnObject.getPoints(vertPoints)
#     posList = [[i[0], i[1], i[2]] for i in vertPoints]
#     # posList=[]
#     # for i in range(vertPoints.length()):
#     #     posList.append([vertPoints[i][0], vertPoints[i][1], vertPoints[i][2]])
#     # # print posList
#     # return posList
#     return vertPoints

def getAllVerts(node, output="generator"):
    """
    Using Maya Python API 1.0
    """
    # ___________Query vertex position ___________

    # initialize a Point array holder
    vertPoints = om.MPointArray()

    # create a Mesh functionset from our dag object
    mfnObject = om.MFnMesh(getMDagPath(node))

    # call the function "getPoints" and feed the data into our pointArray
    mfnObject.getPoints(vertPoints, om.MSpace.kWorld)

    if output=="generator":
        # Create a generator from the points
        posSet = ((vertPoints[i][0], vertPoints[i][1], vertPoints[i][2]) for i in range(vertPoints.length()))
        return posSet
    elif output=="list":
        posList = [(vertPoints[i][0], vertPoints[i][1], vertPoints[i][2]) for i in range(vertPoints.length())]
        return posList
    elif output=="MpointArray":
        return vertPoints
    else:
        cmds.error("Unrecognized output type")


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

def alignAndAim(node, targetList, aimTargetList,
                upObject=None,
                upVector=None,
                localUp=(0.0,1.0,0.0),
                rotateOff=None,
                translateOff=None,
                freezeTransform=False,
                keepConnections=False
                ):
    """
    Aligns the position of the node to the target and rotation to the aimTarget object.
    Args:
        node: Node to be aligned
        targetList: (List) Target nodes for positioning
        aimTargetList: (List) Target nodes for aiming
        upObject: (string) if defined the up node will be up axis of this object
        rotateOff: (tuple) rotation offset with given value
        translateOff: (tuple) translate offset with given value
        freezeTransform: (bool) if set True, freezes transforms of the node at the end
        keepConnections: (bool) Keeps the point ant aim contstraints on the node. If this is turned on, rotateOff,
                        translateOff and freezeTransform options will be bypassed
    Returns:
        None

    """
    if upObject and upVector:
        cmds.warning("Both upObject and upVector parameters cannot be defined. Skipping upObject...")
        upObject = None

    pointFlags = ""
    for i in range (len(targetList)):
        if not i == 0:
            pointFlags = "%s, " % pointFlags
        pointFlags = "{0}targetList[{1}]".format(pointFlags, str(i))
    pointFlags = "%s, node" % pointFlags
    pointCommand = "cmds.pointConstraint({0})".format(pointFlags)
    tempPo = eval(pointCommand)

    aimFlags = ""
    for i in range (len(aimTargetList)):
        if not i == 0:
            aimFlags = "%s, " % aimFlags
        aimFlags = "{0}aimTargetList[{1}]".format(aimFlags, str(i))
    aimFlags = "%s, node" % aimFlags
    aimFlags = "%s, u=%s" % (aimFlags, localUp)
    if upObject:
        aimFlags = "%s, wuo=upObject, wut='object'" % aimFlags
    if upVector:
        aimFlags = "%s, wu=upVector, wut='vector'" % aimFlags

    aimCommand = "cmds.aimConstraint({0})".format(aimFlags)
    tempAim = eval(aimCommand)

    if keepConnections:
        if translateOff:
            cmds.warning("keepConnections is True. Bypassing translateOff flag")
        if rotateOff:
            cmds.warning("keepConnections is True. Bypassing rotateOff flag")
        if freezeTransform:
            cmds.warning("keepConnections is True. Bypassing freezeTransform flag")
        return

    cmds.delete(tempPo)
    cmds.delete(tempAim)
    if translateOff:
        cmds.move(translateOff[0], translateOff[1], translateOff[2], node, r=True)
    if rotateOff:
        cmds.rotate(rotateOff[0], rotateOff[1], rotateOff[2], node, r=True, os=True)
    if freezeTransform:
        cmds.makeIdentity(node, a=True, t=True)

def orientJoints(jointList, localMoveAxis=(1.0,0.0,0.0), upAxis=(0.0,1.0,0.0)):
    """
    Sets the the orientations of joints on a chain.
    :param jointList: (list) Set of joint chain. Order is important. It should start with root and end with tip
    :param localMoveAxis: Each joint local move axis. Default is X
    :param upAxis: Defines the up axis for the chain
    :return: None
    """

    for j in range(1, len(jointList)):
        cmds.parent(jointList[j], w=True)

    # get the aimVector
    tempAimLocator = cmds.spaceLocator(name="tempAimLocator")
    alignAndAim(tempAimLocator, [jointList[1]], [jointList[2]], upVector=upAxis)

    for j in range (0, len(jointList)):

        localAimLocator = cmds.duplicate(tempAimLocator)[0]
        alignTo(localAimLocator, jointList[j], translation=True, rotation=False)

        cmds.move(localMoveAxis[0], localMoveAxis[1], localMoveAxis[2], localAimLocator, r=True, os=True)

        if not (j == (len(jointList)-1)):
            cmds.delete(cmds.aimConstraint(jointList[j+1], jointList[j], wuo=localAimLocator, wut='object', aimVector=localMoveAxis))
            cmds.makeIdentity(jointList[j], a=True)
        cmds.delete(localAimLocator)
    #
    # re-parent the hierarchy
    for j in range (1, len(jointList)):
        cmds.parent(jointList[j], jointList[j-1])

    cmds.delete(tempAimLocator)
    cmds.makeIdentity(jointList[-1], a=True)
    cmds.setAttr("%s.jointOrient" %jointList[-1], 0, 0, 0)


def getBetweenVector(node, targetPointNodeList):
    """
    Calculates average normal vector between the given node and list of other nodes. Useful for finding normal direction of Pole vectors
    :param node: source node
    :param targetPointNodeList: List of nodes which the source node will be averaged into
    :return: MVector object
    """
    # get center vector
    nodePos = getWorldTranslation(node)
    # print "b", nodePos
    sumVectors = om.MVector(0,0,0)
    for p in targetPointNodeList:
        pPos = getWorldTranslation(p)
        # print "\nB_%s" % p, pPos.normal()
        addVector = (nodePos - pPos).normal()
        sumVectors = sumVectors + addVector
    return sumVectors.normal()


def uniqueName(name):
    """Makes sure there is no other object with the same name. Returns the new unique name"""
    baseName = name
    idcounter = 0
    while cmds.objExists(name):
        name = "%s%s" % (baseName, str(idcounter + 1))
        idcounter = idcounter + 1
    return name

def uniqueList(fList):
    """Makes the list unique. Protects ordering."""
    keys = {}
    for e in fList:
        keys[e] = 1
    return keys.keys()

def createUpGrp(node, suffix, freezeTransform=True):
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
        if freezeTransform:
            cmds.makeIdentity(newGrp, a=True)

    cmds.parent(node,newGrp)
    return newGrp


def lockAndHide (node, channelList):
    """
    Locks and hides the channels specified in the channelList.
    Args:
        node: Node
        channelArray: Must be list value containing the channels as string values. eg: ["sx", "sy", "sz"] or ["translateX", "rotateX", "sz"]
    Returns: None

    """
    map(lambda ch: cmds.setAttr("{0}.{1}".format(node, ch), lock=True, keyable=False, channelBox=False), channelList)
    # for i in channelList:
    #     attribute=("{0}.{1}".format(node, i))
    #     cmds.setAttr(attribute, lock=True, keyable=False, channelBox=False)



