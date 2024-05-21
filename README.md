# Discontinuity (Euler) Filter for BrawlCrate
*BrawlCrate v0.42 or newer required.*  

In BrawlCrate, navigate to Tools > Settings > Updater tab, and click the Manage Subscriptions button.  
Click add, then paste the link to this Github repo: https://github.com/exul-anima/BrawlCrate-EulerFilter  
These plug-ins will then be downloaded, and future updates will be pulled automatically!

## What is this?

This plugin fixes discontinuities in Euler rotations (usually resulting from baking animations in software like Blender/Autodesk Maya) that result in jittery interpolation of CHR0 animations. This most commonly manifests as jitteriness during playback in slow motion.

This is specifically an attempt to port the feature as implemented in Blender 3.X.

## Usage

**For all CHR0 animations in a BRRES file:**

Right click the **AnmChr(NW4R)** folder containing the animations to filter, and under Plugins, select *Discontinuity (Euler) Filter*.

**For a single CHR0 animation file:**

Right click the animation to filter, and under Plugins, select *Discontinuity (Euler) Filter*.

**For a single bone's keyframes in a CHR0 animation file:**

Right click the bone with the keyframes to filter, and under Plugins, select *Discontinuity (Euler) Filter*.

## Disclaimers

This is not a 100% fix to all discontinuity issues. There is only so much that can be automatically fixed. At times you will have to fix some discontinuities yourself. This tool is meant to help automate getting you 99% the way there.

Credits to soopercool101 and the current/previous contributors to [BrawlCrate](https://github.com/soopercool101/BrawlCrate) and its API, markymawk for their [sample plugins](https://github.com/soopercool101/BrawlCrateSamplePlugins), and LearnOpenCV Tutorials for their rotation matrix code that's adapted in this plugin.

All files within this repository are published under the GPLv3 license.