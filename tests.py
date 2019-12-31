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

# write
for i in range(count):
    p.elementByLogicalIndex(ids[i]).setFloat(weights[i])