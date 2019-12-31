# WIP Weight read / write approaches

# this reads/writes painted weight values in blendShape1's first input target
import maya.OpenMaya as om
p = om.MPlug()
sl = om.MSelectionList()
sl.add("blendShape1.inputTarget[0].baseWeights")
# sl.add("skinCluster1.weightList")
sl.getPlug(0, p)
ids = om.MIntArray()
p.getExistingArrayAttributeIndices(ids)
count = ids.length()
weights = [0.0]*count

# read
for i in range(count):
    weights[i] = p.elementByPhysicalIndex(i).asFloat()
    # weights[i] = p.elementByPhysicalIndex(i).asDouble()

# inject here somewhere to gather the getAllVerts with MPointArray return
# if arrays are a match you can go from there and create proximity functions or ray casts


# write
for i in range(count):
    p.elementByLogicalIndex(ids[i]).setFloat(weights[i])