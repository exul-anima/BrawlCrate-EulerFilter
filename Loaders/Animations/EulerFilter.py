__author__ = "Exul Anima"
__version__ = "1.0.0 BETA"

from BrawlCrate.API import *
from BrawlCrate.NodeWrappers import *
from BrawlLib.SSBB.ResourceNodes import *
from BrawlLib.Wii.Animations import *
from System.Windows.Forms import ToolStripMenuItem
import math

## Start enable check functions
# Wrapper: MDL0Wrapper
# Adapted from markymawk
def EnableCheckCHR0(sender, event_args):
	node = BrawlAPI.SelectedNode
	sender.Enabled = (node is not None and node.HasChildren)

def EnableCheckCHR0Entry(sender, event_args):
	node = BrawlAPI.SelectedNode
	sender.Enabled = node is not None

# Check to ensure that the BRESGroup is a CHR0 animation group that contains more than 1 CHR0
# Wrapper: BRESGroupWrapper
# Adapted from markymawk
def EnableCheckBRESGroup(sender, event_args):
	group = BrawlAPI.SelectedNode
	sender.Enabled = (group is not None and group.HasChildren and len(group.Children) > 1)

# Multiply together (dot product) two 3x3 matrices.
def mat3_dot(a, b):

    multMatrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    b = list(map(list, zip(*b)))
    for y in range(3):
        for x in range(3):
            print(a[x][0] * b[y][0] + a[x][1] * b[y][1] + a[x][2] * b[y][2])
            multMatrix[x][y] = a[x][0] * b[y][0] + a[x][1] * b[y][1] + a[x][2] * b[y][2]

    return multMatrix

# The following two matrix-related functions courtesy of LearnOpenCV Tutorials, refactored by me to avoid dependency on numpy.

# Calculates Rotation Matrix given euler angles.
def eulerAnglesToRotationMatrix(theta):

    R_x = [[1, 0, 0], [0, math.cos(theta[0]), -math.sin(theta[0])], [0, math.sin(theta[0]), math.cos(theta[0])]]
 
    R_y = [[math.cos(theta[1]), 0, math.sin(theta[1])], [0, 1, 0], [-math.sin(theta[1]), 0, math.cos(theta[1])]]
 
    R_z = [[math.cos(theta[2]), -math.sin(theta[2]), 0], [math.sin(theta[2]), math.cos(theta[2]), 0], [0, 0, 1]]
 
    R = mat3_dot(R_z, mat3_dot( R_y, R_x ))
 
    return R
 
# Calculates rotation matrix to euler angles
# The result is the same as MATLAB except the order
# of the euler angles ( x and z are swapped ).
def rotationMatrixToEulerAngles(R):

    sy = math.sqrt(R[0][0] * R[0][0] + R[1][0] * R[1][0])
 
    singular = sy < 1e-6
 
    if  not singular :
        x = math.atan2(R[2][1] , R[2][2])
        y = math.atan2(-R[2][0], sy)
        z = math.atan2(R[1][0], R[0][0])
    else :
        x = math.atan2(-R[1][2], R[1][1])
        y = math.atan2(-R[2][0], sy)
        z = 0

    newAngle = [x, y, z]
    return newAngle

def eulerFilterMultiChannel(bone):
    
    for k in range(0, bone.FrameCount):
        eulerBefore = [bone.GetFrameValue(3, k), bone.GetFrameValue(4, k), bone.GetFrameValue(5, k)]

        if bone.GetKeyframe(3, k) is None or bone.GetKeyframe(4, k) is None or bone.GetKeyframe(5, k) is None:
            continue
        if eulerBefore == [0.0, 0.0, 0.0]:
            continue

        for e in range(len(eulerBefore)):
            eulerBefore[e] = eulerBefore[e] * math.pi / 180
        eulerAfter = []
        eulerAfter = rotationMatrixToEulerAngles(eulerAnglesToRotationMatrix(eulerBefore))
        for e in range(len(eulerAfter)):
            eulerAfter[e] = eulerAfter[e] * 180 / math.pi
        
        for axis in range(len(eulerAfter)):
            if (bone.GetKeyframe(axis + 3, k)._value - 1e-3) <= eulerAfter[axis] <= (bone.GetKeyframe(axis + 3, k)._value + 1e-3):
                continue
            bone.SetKeyframe(axis + 3, k, eulerAfter[axis])

    return None

def eulerFilterSingleChannel(bone):
    
    validKeyframes = []
    for k in range(0, bone.FrameCount):
        if bone.GetKeyframe(3, k) is None and bone.GetKeyframe(4, k) is None and bone.GetKeyframe(5, k) is None:
            continue
        validKeyframes.append(k)
    
    #BrawlAPI.ShowMessage("valids for " + str(bone.Name) + ": " + str(validKeyframes) + '\n', "Discontinuity (Euler) Filter")
    if len(validKeyframes) < 2:
        return None
    
    for k in range(1, len(validKeyframes)):
        for axis in range(3, 6):

            if bone.GetKeyframe(axis, validKeyframes[k]) is None:
                #BrawlAPI.ShowMessage("key " + str(validKeyframes[k]) + " invalid on axis " + str(axis) + " \n", "Discontinuity (Euler) Filter")
                continue
            #BrawlAPI.ShowMessage("key " + str(validKeyframes[k]) + " valid on axis " + str(axis) + "\nvalue: " + str(bone.GetKeyframe(axis, validKeyframes[k])._value) + " \n", "Discontinuity (Euler) Filter")
            currentRot = bone.GetKeyframe(axis, validKeyframes[k])._value
            
            for g in range(1, k + 1):
                if bone.GetKeyframe(axis, validKeyframes[k - g]) is None:
                    continue
                previousRot = bone.GetKeyframe(axis, validKeyframes[k - g])._value
                break
            #BrawlAPI.ShowMessage("key " + str(validKeyframes[k - g]) + " valid on axis " + str(axis) + "\nvalue: " + str(bone.GetKeyframe(axis, validKeyframes[k - g])._value) + " \n", "Discontinuity (Euler) Filter")
            
            i = 0
            newRot = currentRot
            while abs(newRot - previousRot) >= 180 - 1e-3:
                if i >= 20:
                    newRot = currentRot
                    break
                if newRot - previousRot >= 1e-3:
                    newRot -= 360
                    #BrawlAPI.ShowMessage("delta > 180", "Discontinuity (Euler) Filter")
                elif newRot - previousRot <= -1e-3:
                    newRot += 360
                    #BrawlAPI.ShowMessage("delta < 180", "Discontinuity (Euler) Filter")
                else:
                    newRot += 0
                    #BrawlAPI.ShowMessage("delta == 180", "Discontinuity (Euler) Filter")
                    break
                i += 1
            
            if (180 - 1e-3) <= abs(newRot - previousRot) <= (180 + 1e-3):
                newRot = previousRot

            #BrawlAPI.ShowMessage("bone: " + str(bone.Name) + '\n' + "currentk: " + str(validKeyframes[k]) + '\n' + "prevk: " + str(validKeyframes[k - 1]) + '\n' + "currentRot: " + str(currentRot) + '\n' + "previousRot: " + str(previousRot) + '\n' + "newRot: " + str(newRot) + '\n', "Discontinuity (Euler) Filter")
            if (bone.GetKeyframe(axis, validKeyframes[k])._value - 1e-3) <= newRot <= (bone.GetKeyframe(axis, validKeyframes[k])._value + 1e-3):
                continue
            bone.SetKeyframe(axis, validKeyframes[k], newRot)

    return None

## Batch animation filter
def filterAllAnims(sender, event_args):

    BrawlAPI.ShowMessage("Filter about to begin. \nThis may take a while (especially for batching entire sets of character animations) so please be patient.", "Discontinuity (Euler) Filter")
    animationsFiltered = 0
    if BrawlAPI.SelectedNode.HasChildren:
        for node in BrawlAPI.SelectedNode.Children:
            if isinstance(node, CHR0Node):
                for bone in node.Children:
                    eulerFilterMultiChannel(bone)
                    eulerFilterSingleChannel(bone)
                animationsFiltered += 1
                #break
                #BrawlAPI.ShowMessage("Filtered anim " + str(node.Name) + '\n', "Discontinuity (Euler) Filter")
            else:
                BrawlAPI.ShowMessage("Not an anim: " + str(node.Name) + '\n', "Discontinuity (Euler) Filter")
    else:
        BrawlAPI.ShowMessage("Not a group of animations: " + str(BrawlAPI.SelectedNode.Name) + '\n', "Discontinuity (Euler) Filter")

    if animationsFiltered == 1:
        BrawlAPI.ShowMessage("Filtered " + str(animationsFiltered) + " animation. \n\n Look over your animations to make sure they aren't messed up. This tool isn't perfect.\n\n If one is, just right click and select \"Restore\" to revert errors BEFORE YOU SAVE ANYTHING.", "Discontinuity (Euler) Filter")
    else:
        BrawlAPI.ShowMessage("Filtered " + str(animationsFiltered) + " animations. \n\n Look over your animations to make sure they aren't messed up. This tool isn't perfect.\n\n If one is, just right click and select \"Restore\" to revert errors BEFORE YOU SAVE ANYTHING.", "Discontinuity (Euler) Filter")

    return None

## Single animation filter
def filterSingleAnim(sender, event_args):

    BrawlAPI.ShowMessage("Filter about to begin. \nPlease be patient.", "Discontinuity (Euler) Filter")
    keyframesFiltered = 0
    if BrawlAPI.SelectedNode.HasChildren:
        if isinstance(BrawlAPI.SelectedNode, CHR0Node):
            for bone in BrawlAPI.SelectedNode.Children:
                eulerFilterMultiChannel(bone)
                eulerFilterSingleChannel(bone)
                keyframesFiltered += 1
            #break
            #BrawlAPI.ShowMessage("Filtered anim " + str(node.Name) + '\n', "Discontinuity (Euler) Filter")
        else:
            BrawlAPI.ShowMessage("Not an anim: " + str(node.Name) + '\n', "Discontinuity (Euler) Filter")
    else:
        BrawlAPI.ShowMessage("Animation has no keyed bones: " + str(BrawlAPI.SelectedNode.Name) + '\n', "Discontinuity (Euler) Filter")

    if keyframesFiltered == 1:
        BrawlAPI.ShowMessage("Filtered " + str(keyframesFiltered) + " keyframed bone. \n\n Look over your animations to make sure they aren't messed up. This tool isn't perfect.\n\n If one is, just right click and select \"Restore\" to revert errors BEFORE YOU SAVE ANYTHING.", "Discontinuity (Euler) Filter")
    else:
        BrawlAPI.ShowMessage("Filtered " + str(keyframesFiltered) + " keyframed bones. \n\n Look over your animations to make sure they aren't messed up. This tool isn't perfect.\n\n If one is, just right click and select \"Restore\" to revert errors BEFORE YOU SAVE ANYTHING.", "Discontinuity (Euler) Filter")

    return None

## Single bone filter
def filterSingleBone(sender, event_args):

    BrawlAPI.ShowMessage("Filter about to begin. \nPlease be patient.", "Discontinuity (Euler) Filter")
    keyframesFiltered = 0
    if isinstance(BrawlAPI.SelectedNode, CHR0EntryNode):
        eulerFilterMultiChannel(BrawlAPI.SelectedNode)
        eulerFilterSingleChannel(BrawlAPI.SelectedNode)
        #break
        #BrawlAPI.ShowMessage("Filtered anim " + str(node.Name) + '\n', "Discontinuity (Euler) Filter")
    else:
        BrawlAPI.ShowMessage("Not an animated bone: " + str(node.Name) + '\n', "Discontinuity (Euler) Filter")
    BrawlAPI.ShowMessage("Filtered bone's keyframes.\n\n Look over your animations to make sure they aren't messed up. This tool isn't perfect.\n\n If one is, just right click and select \"Restore\" to revert errors BEFORE YOU SAVE ANYTHING.", "Discontinuity (Euler) Filter")

    return None

## Adding options to the context menus
BrawlAPI.AddContextMenuItem(BRESGroupWrapper, "", "Fix discontinuities from baked Euler rotation keyframes that break slow motion playback", EnableCheckBRESGroup, ToolStripMenuItem('Discontinuity (Euler) Filter', None, filterAllAnims))
BrawlAPI.AddContextMenuItem(CHR0Wrapper, "", "Fix discontinuities from baked Euler rotation keyframes that break slow motion playback", EnableCheckCHR0, ToolStripMenuItem('Discontinuity (Euler) Filter', None, filterSingleAnim))
BrawlAPI.AddContextMenuItem(CHR0EntryWrapper, "", "Fix discontinuities from baked Euler rotation keyframes that break slow motion playback", EnableCheckCHR0Entry, ToolStripMenuItem('Discontinuity (Euler) Filter', None, filterSingleBone))